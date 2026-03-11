import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "auditor": set(),
            "finance": set(),
            "admin": set()
        }
        self.connection_info: Dict[WebSocket, dict] = {}
        
    async def connect(self, websocket: WebSocket, user_role: str, user_id: str):
        await websocket.accept()
        self.active_connections[user_role].add(websocket)
        self.connection_info[websocket] = {
            "user_id": user_id,
            "user_role": user_role,
            "connected_at": asyncio.get_event_loop().time()
        }
        logger.info(f"WebSocket connected: {user_id} ({user_role})")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "message": "WebSocket connection established",
            "user_id": user_id,
            "user_role": user_role
        }, websocket)
        
        # Broadcast connection count
        await self.broadcast_connection_stats()
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.connection_info:
            user_info = self.connection_info[websocket]
            user_role = user_info["user_role"]
            
            if websocket in self.active_connections[user_role]:
                self.active_connections[user_role].remove(websocket)
            
            del self.connection_info[websocket]
            logger.info(f"WebSocket disconnected: {user_info['user_id']} ({user_role})")
            
            # Broadcast updated connection stats
            asyncio.create_task(self.broadcast_connection_stats())
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast_to_role(self, message: dict, role: str):
        disconnected = []
        for websocket in self.active_connections[role]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {role}: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast to all connected clients"""
        disconnected = []
        for role in self.active_connections:
            for websocket in self.active_connections[role]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to broadcast: {e}")
                    disconnected.append(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_connection_stats(self):
        stats = {
            "type": "connection_stats",
            "total_connections": sum(len(connections) for connections in self.active_connections.values()),
            "connections_by_role": {
                role: len(connections) for role, connections in self.active_connections.items()
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(stats)
    
    def get_connection_stats(self) -> dict:
        return {
            "total_connections": sum(len(connections) for connections in self.active_connections.values()),
            "connections_by_role": {
                role: len(connections) for role, connections in self.active_connections.items()
            }
        }
    
    async def send_transaction_processed(self, transaction_data: dict):
        """Send transaction processed event to auditors"""
        message = {
            "type": "transaction_processed",
            "data": transaction_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_role(message, "auditor")
    
    async def send_analysis_completed(self, analysis_data: dict):
        """Send analysis completed event to auditors"""
        message = {
            "type": "analysis_completed",
            "data": analysis_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_role(message, "auditor")
    
    async def send_case_created(self, case_data: dict):
        """Send case created event to auditors"""
        message = {
            "type": "case_created",
            "data": case_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast_to_role(message, "auditor")
    
    async def send_system_status(self, status_data: dict):
        """Send system status updates to all users"""
        message = {
            "type": "system_status",
            "data": status_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()