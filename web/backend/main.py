"""
Gamalta Web Backend - FastAPI application entry point.

Run with:
    uvicorn web.backend.main:app --reload --host 0.0.0.0 --port 8080

Or from the web directory:
    python -m backend.main
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import device, control, modes, effects
from .websocket import websocket_endpoint
from .services.device_manager import device_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    yield
    # Shutdown - disconnect cleanly
    await device_manager.disconnect()


app = FastAPI(
    title="Gamalta Web API",
    description="REST and WebSocket API for controlling Gamalta BLE aquarium lights",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routes
app.include_router(device.router, prefix="/api/device", tags=["device"])
app.include_router(control.router, prefix="/api/control", tags=["control"])
app.include_router(modes.router, prefix="/api/modes", tags=["modes"])
app.include_router(effects.router, prefix="/api/effects", tags=["effects"])

# WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Gamalta Web API",
        "version": "0.1.0",
        "docs": "/docs",
        "websocket": "/ws",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "connected": device_manager.is_connected,
        "device": device_manager.device_name,
    }


def run():
    """Run the server (for use as entry point)."""
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    run()
