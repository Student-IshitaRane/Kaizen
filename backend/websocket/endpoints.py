from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Optional
import asyncio
import json
import logging
from datetime import datetime

from .manager import websocket_manager
from app.auth.jwt_handler import decode_access_token
from app.database.session import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

async def get_current_user_from_ws(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """Authenticate user from WebSocket connection"""
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return None
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            await websocket.close(code=1008, reason="Invalid token")
            return None
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role", "auditor")
        }
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return None

async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time updates"""
    # Authenticate user
    user = await get_current_user_from_ws(websocket, token)
    if not user:
        return
    
    # Connect to WebSocket manager
    await websocket_manager.connect(websocket, user["role"], user["user_id"])
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for message from client (with timeout for keepalive)
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                
                # Handle different message types from client
                if data.get("type") == "ping":
                    await websocket_manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                elif data.get("type") == "subscribe":
                    # Handle subscription requests
                    await websocket_manager.send_personal_message({
                        "type": "subscription_confirmed",
                        "channels": data.get("channels", []),
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                elif data.get("type") == "request_stats":
                    # Send current connection stats
                    stats = websocket_manager.get_connection_stats()
                    await websocket_manager.send_personal_message({
                        "type": "connection_stats",
                        "data": stats,
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                
            except asyncio.TimeoutError:
                # Send keepalive ping
                try:
                    await websocket_manager.send_personal_message({
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    }, websocket)
                except:
                    break  # Connection lost
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        websocket_manager.disconnect(websocket)