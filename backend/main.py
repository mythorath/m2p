"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from server.routes import leaderboard_router
from server.websocket import websocket_endpoint
from server.tasks import start_leaderboard_scheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting M2P application...")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Start background scheduler
    logger.info("Starting background scheduler...")
    scheduler = start_leaderboard_scheduler(
        interval_minutes=settings.LEADERBOARD_UPDATE_INTERVAL // 60
    )

    yield

    # Shutdown
    logger.info("Shutting down M2P application...")
    scheduler.shutdown()


# Create FastAPI app
app = FastAPI(
    title="M2P - Mining to Prosperity",
    description="Leaderboard and achievement system for M2P mining game",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leaderboard_router)


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket_endpoint(websocket)


@app.websocket("/ws/{wallet_address}")
async def websocket_user_route(websocket: WebSocket, wallet_address: str):
    """WebSocket endpoint with user-specific notifications."""
    await websocket_endpoint(websocket, wallet_address)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "m2p-backend",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "M2P Backend API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
