#!/usr/bin/env python3
"""
Quantum Jobs Tracker - Startup Script
"""
import asyncio
import logging
import uvicorn
from app.main import app
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("quantum_jobs_tracker.log")
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    logger.info("Starting Quantum Jobs Tracker API Server")
    logger.info(f"Host: {settings.api_host}")
    logger.info(f"Port: {settings.api_port}")
    logger.info(f"Debug: {settings.debug}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        workers=1  # Single worker for SQLite
    )

if __name__ == "__main__":
    main()
