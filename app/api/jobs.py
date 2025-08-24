from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.services.quantum_service import quantum_service
from app.services.database_service import DatabaseService
from app.schemas.quantum_schemas import (
    QuantumJobSchema, FilterParams, PaginatedResponse
)

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=PaginatedResponse)
async def get_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    backend: Optional[str] = Query(None, description="Filter by backend name"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get paginated list of quantum jobs with filtering options"""
    filters = FilterParams(
        status=status,
        backend=backend,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page
    )
    
    db_service = DatabaseService(db)
    return await db_service.get_jobs(filters)

@router.get("/recent", response_model=List[QuantumJobSchema])
async def get_recent_jobs(
    limit: int = Query(20, ge=1, le=100, description="Number of recent jobs to fetch"),
    db: Session = Depends(get_db)
):
    """Get recently created jobs"""
    db_service = DatabaseService(db)
    jobs = await db_service.get_recent_jobs(limit)
    return [QuantumJobSchema.from_orm(job) for job in jobs]

@router.get("/{job_id}", response_model=QuantumJobSchema)
async def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific job by ID"""
    db_service = DatabaseService(db)
    job = await db_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return QuantumJobSchema.from_orm(job)

@router.post("/sync")
async def sync_jobs_from_ibm(
    background_tasks: BackgroundTasks,
    limit: int = Query(100, ge=1, le=1000, description="Number of jobs to sync"),
    backend: Optional[str] = Query(None, description="Specific backend to sync"),
    db: Session = Depends(get_db)
):
    """Sync jobs from IBM Quantum (runs in background)"""
    background_tasks.add_task(sync_jobs_task, db, limit, backend)
    return {"message": "Job sync started in background"}

async def sync_jobs_task(db: Session, limit: int, backend: Optional[str]):
    """Background task to sync jobs from IBM Quantum"""
    try:
        jobs_data = await quantum_service.get_jobs(limit=limit, backend=backend)
        
        db_service = DatabaseService(db)
        await db_service.bulk_create_jobs(jobs_data)
        
        print(f"Successfully synced {len(jobs_data)} jobs")
    except Exception as e:
        print(f"Error syncing jobs: {e}")

@router.get("/stats/overview")
async def get_job_statistics(db: Session = Depends(get_db)):
    """Get job statistics overview"""
    db_service = DatabaseService(db)
    return await db_service.get_job_statistics()

@router.get("/trends/daily")
async def get_job_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get job trends over time"""
    db_service = DatabaseService(db)
    return await db_service.get_job_trends(days)

@router.get("/by-backend/{backend_name}")
async def get_jobs_by_backend(
    backend_name: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs filtered by specific backend"""
    filters = FilterParams(backend=backend_name, page=page, per_page=per_page)
    db_service = DatabaseService(db)
    return await db_service.get_jobs(filters)

@router.get("/by-status/{status}")
async def get_jobs_by_status(
    status: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get jobs filtered by status"""
    filters = FilterParams(status=status, page=page, per_page=per_page)
    db_service = DatabaseService(db)
    return await db_service.get_jobs(filters)
