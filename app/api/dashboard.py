from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.quantum_service import quantum_service
from app.services.database_service import DatabaseService
from app.schemas.quantum_schemas import (
    SystemStatusSchema, JobStatsSchema, BackendStatsSchema, DashboardDataSchema
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/", response_model=DashboardDataSchema)
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get comprehensive dashboard data"""
    db_service = DatabaseService(db)
    
    # Get all dashboard data
    job_stats = await db_service.get_job_statistics()
    backend_stats = await db_service.get_backend_statistics()
    recent_jobs = await db_service.get_recent_jobs(limit=10)
    queue_info = await db_service.get_queue_info()
    system_status = await db_service.get_system_status()
    backend_utilization = await db_service.get_backend_utilization()
    
    return DashboardDataSchema(
        job_stats=JobStatsSchema(**job_stats),
        backend_stats=BackendStatsSchema(**backend_stats),
        recent_jobs=[job for job in recent_jobs],
        queue_info=queue_info,
        system_status=system_status,
        backend_utilization=backend_utilization
    )

@router.get("/stats/jobs", response_model=JobStatsSchema)
async def get_job_stats(db: Session = Depends(get_db)):
    """Get job statistics"""
    db_service = DatabaseService(db)
    stats = await db_service.get_job_statistics()
    return JobStatsSchema(**stats)

@router.get("/stats/backends", response_model=BackendStatsSchema)
async def get_backend_stats(db: Session = Depends(get_db)):
    """Get backend statistics"""
    db_service = DatabaseService(db)
    stats = await db_service.get_backend_statistics()
    return BackendStatsSchema(**stats)

@router.get("/system-status", response_model=List[SystemStatusSchema])
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status for all services"""
    db_service = DatabaseService(db)
    status = await db_service.get_system_status()
    return [SystemStatusSchema.from_orm(s) for s in status]

@router.post("/refresh")
async def refresh_dashboard_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Refresh all dashboard data from IBM Quantum"""
    background_tasks.add_task(refresh_data_task, db)
    return {"message": "Dashboard refresh started in background"}

async def refresh_data_task(db: Session):
    """Background task to refresh all data"""
    try:
        db_service = DatabaseService(db)
        
        # Sync backends
        backends_data = await quantum_service.get_all_backends()
        await db_service.bulk_upsert_backends(backends_data)
        
        # Sync jobs
        jobs_data = await quantum_service.get_jobs(limit=200)
        await db_service.bulk_create_jobs(jobs_data)
        
        # Update queue info
        queue_data = await quantum_service.get_queue_info()
        await db_service.update_queue_info(queue_data)
        
        # Update system status
        status_data = await quantum_service.get_system_status()
        await db_service.update_system_status(status_data)
        
        print("Dashboard data refreshed successfully")
    except Exception as e:
        print(f"Error refreshing dashboard data: {e}")

@router.get("/health")
async def get_health_status():
    """Get health status of the service"""
    try:
        # Check IBM Quantum connection
        quantum_status = "connected" if quantum_service.initialized else "disconnected"
        
        return {
            "status": "healthy",
            "quantum_service": quantum_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Get detailed metrics for monitoring"""
    db_service = DatabaseService(db)
    
    job_stats = await db_service.get_job_statistics()
    backend_stats = await db_service.get_backend_statistics()
    utilization = await db_service.get_backend_utilization()
    trends = await db_service.get_job_trends(days=7)
    
    return {
        "jobs": job_stats,
        "backends": backend_stats,
        "utilization": utilization,
        "trends": trends,
        "timestamp": "2024-01-01T00:00:00Z"
    }
