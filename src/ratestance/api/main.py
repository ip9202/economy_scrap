"""FastAPI application for RateStance Dashboard API."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from ratestance.api.routes import router

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

app = FastAPI(
    title="RateStance API",
    description="API for RateStance Dashboard - Financial news sentiment analysis",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "https://ip9202.site",  # Production server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/data", tags=["data"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "RateStance API", "version": "0.1.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event() -> None:
    """Log startup message."""
    logger.info("RateStance API starting up...")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Log shutdown message."""
    logger.info("RateStance API shutting down...")
