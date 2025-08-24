from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.database_service import DatabaseService
from app.schemas.quantum_schemas import JobQueueSchema

router = APIRouter(prefix="/queue", tags=["Queue"])

@router.get("/", response_model=List[JobQueueSchema])
async def get_all_queue_info(db: Session = Depends(get_db)):
    """Get queue information for all backends"""
    db_service = DatabaseService(db)
    queue_info = await db_service.get_queue_info()
    return [JobQueueSchema.from_orm(queue) for queue in queue_info]

@router.get("/summary")
async def get_queue_summary(db: Session = Depends(get_db)):
    """Get a summary of queue statistics"""
    db_service = DatabaseService(db)
    queue_info = await db_service.get_queue_info()
    
    total_queued = sum(q.queue_length for q in queue_info)
    total_pending = sum(q.pending_jobs for q in queue_info)
    total_running = sum(q.running_jobs for q in queue_info)
    
    avg_wait_time = None
    if queue_info:
        wait_times = [q.average_wait_time for q in queue_info if q.average_wait_time is not None]
        if wait_times:
            avg_wait_time = sum(wait_times) / len(wait_times)
    
    return {
        "total_queued_jobs": total_queued,
        "total_pending_jobs": total_pending,
        "total_running_jobs": total_running,
        "average_wait_time": avg_wait_time,
        "backends_count": len(queue_info),
        "operational_backends": len([q for q in queue_info if q.status == 'operational'])
    }

@router.get("/longest-wait")
async def get_longest_wait_times(db: Session = Depends(get_db)):
    """Get backends with longest wait times"""
    db_service = DatabaseService(db)
    queue_info = await db_service.get_queue_info()
    
    # Sort by estimated wait time
    sorted_queues = sorted(
        [q for q in queue_info if q.estimated_wait_time is not None],
        key=lambda x: x.estimated_wait_time,
        reverse=True
    )
    
    return [JobQueueSchema.from_orm(queue) for queue in sorted_queues[:10]]

@router.get("/shortest-wait")
async def get_shortest_wait_times(db: Session = Depends(get_db)):
    """Get backends with shortest wait times"""
    db_service = DatabaseService(db)
    queue_info = await db_service.get_queue_info()
    
    # Sort by estimated wait time (ascending)
    sorted_queues = sorted(
        [q for q in queue_info if q.estimated_wait_time is not None and q.status == 'operational'],
        key=lambda x: x.estimated_wait_time
    )
    
    return [JobQueueSchema.from_orm(queue) for queue in sorted_queues[:10]]

@router.get("/by-backend/{backend_name}")
async def get_backend_queue(
    backend_name: str,
    db: Session = Depends(get_db)
):
    """Get queue information for a specific backend"""
    db_service = DatabaseService(db)
    queue_info = await db_service.get_queue_info()
    backend_queue = next((q for q in queue_info if q.backend_name == backend_name), None)
    
    if not backend_queue:
        return {"message": "No queue information found for this backend"}
    
    return JobQueueSchema.from_orm(backend_queue)
