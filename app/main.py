from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.services.quantum_service import quantum_service
from app.api import jobs, backends, queue, dashboard, analytics, websockets

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Quantum Jobs Tracker API")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Initialize quantum service
    await quantum_service.initialize()
    logger.info("Quantum service initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Quantum Jobs Tracker API")

# Create FastAPI app
app = FastAPI(
    title="Quantum Jobs Tracker API",
    description="""
    A comprehensive backend API for tracking live/public quantum computing jobs from IBM Quantum.
    
    This API provides real-time access to:
    - Quantum job tracking and monitoring
    - Backend status and information
    - Queue management and analytics
    - Performance metrics and insights
    - Dashboard data for visualization
    
    Built for hackathons and quantum computing research.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(backends.router, prefix="/api/v1")
app.include_router(queue.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(websockets.router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Quantum Jobs Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "jobs": "/api/v1/jobs",
            "backends": "/api/v1/backends",
            "queue": "/api/v1/queue",
            "dashboard": "/api/v1/dashboard",
            "analytics": "/api/v1/analytics",
            "websockets": {
                "dashboard": "/api/v1/ws/dashboard",
                "jobs": "/api/v1/ws/jobs",
                "queue": "/api/v1/ws/queue"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "quantum_service": "connected" if quantum_service.initialized else "disconnected",
        "database": "connected",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "internal_error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
