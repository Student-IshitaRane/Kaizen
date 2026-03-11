from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import threading
from database import engine, Base
from core.config import settings
from routes import auth, dataset_upload, transactions, flagged_cases, review_actions, analysis, chatbot, reports, insights
from streaming.kafka_producer import producer
from streaming.kafka_consumer import consumer_manager
from streaming.consumer import start_analysis_consumer
from llm_service import llm_service
from services.agent_orchestrator import AgentOrchestrator
from websocket.endpoints import websocket_endpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Audit Analytics Platform API")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Initialize streaming services
    logger.info("Initializing streaming services...")
    # Kafka producer is already initialized as singleton
    logger.info("Kafka producer initialized")
    
    # Initialize AI services
    logger.info("Initializing AI services...")
    
    # Check LLM providers
    llm_providers = llm_service.get_available_providers()
    available_providers = [p for p in llm_providers if p.get("available", False)]
    logger.info(f"LLM providers available: {len(available_providers)}")
    for provider in available_providers:
        logger.info(f"  - {provider.get('provider')}: {provider.get('model')}")
    
    # Initialize agent orchestrator
    agent_orchestrator = AgentOrchestrator()
    agents = agent_orchestrator.get_agent_status()
    available_agents = [name for name, status in agents.items() if status.get("available", False)]
    logger.info(f"Agents initialized: {len(available_agents)}")
    for name in available_agents:
        logger.info(f"  - {name}: {agents[name].get('description', 'No description')}")
    
    # Start Kafka consumers (in background)
    logger.info("Starting Kafka consumers...")
    if settings.KAFKA_BOOTSTRAP_SERVERS != "localhost:9092":
        # Start analysis consumer in background thread
        consumer_thread = threading.Thread(
            target=start_analysis_consumer,
            daemon=True,
            name="analysis-consumer"
        )
        consumer_thread.start()
        logger.info("Analysis consumer started in background thread")
    else:
        logger.info("Kafka not configured, skipping consumer startup")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Audit Analytics Platform API")
    
    # Close streaming connections
    producer.close()
    consumer_manager.close_all()
    logger.info("Streaming services shut down")

# Create FastAPI app
app = FastAPI(
    title="Audit Analytics Platform API",
    description="AI-Powered Audit Analytics Platform - Production Prototype",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api prefix
app.include_router(auth, prefix="/api")
app.include_router(dataset_upload, prefix="/api")
app.include_router(transactions, prefix="/api")
app.include_router(flagged_cases, prefix="/api")
app.include_router(review_actions, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(insights.router, prefix="/api")

# Add WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket):
    await websocket_endpoint(websocket)

@app.get("/")
async def root():
    return {
        "message": "Audit Analytics Platform API",
        "version": "1.0.0",
        "status": "operational",
        "description": "AI-powered audit analytics with real-time monitoring",
        "endpoints": {
            "auth": "/auth",
            "upload": "/upload",
            "transactions": "/transactions",
            "cases": "/cases",
            "reviews": "/reviews"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "services": "operational"
    }

@app.get("/system-info")
async def system_info():
    # Get LLM provider status
    llm_providers = llm_service.get_available_providers()
    available_providers = [p for p in llm_providers if p.get("available", False)]
    
    # Get agent status
    agent_orchestrator = AgentOrchestrator()
    agents = agent_orchestrator.get_agent_status()
    available_agents = [name for name, status in agents.items() if status.get("available", False)]
    
    # Get pipeline configurations
    pipelines = agent_orchestrator.get_available_pipelines()
    
    return {
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "max_upload_size": settings.MAX_UPLOAD_SIZE,
        "upload_dir": settings.UPLOAD_DIR,
        "ai_services": {
            "llm_providers_available": len(available_providers),
            "llm_providers": available_providers,
            "agents_available": len(available_agents),
            "available_agents": available_agents,
            "agent_pipelines": list(pipelines.keys()),
            "pipeline_configs": pipelines
        },
        "audit_analysis": {
            "immediate_analysis_enabled": settings.ENABLE_IMMEDIATE_ANALYSIS,
            "llm_explanations_enabled": settings.ENABLE_LLM_EXPLANATIONS,
            "approval_threshold": settings.APPROVAL_THRESHOLD_DEFAULT,
            "flag_threshold_medium": settings.FLAG_THRESHOLD_MEDIUM,
            "flag_threshold_high": settings.FLAG_THRESHOLD_HIGH,
            "batch_analysis_limit": settings.BATCH_ANALYSIS_LIMIT
        },
        "streaming_services": {
            "kafka_enabled": True,
            "topics_configured": 8,  # From kafka_config.py
            "producer_status": "active",
            "consumer_groups": list(consumer_manager.consumers.keys())
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )