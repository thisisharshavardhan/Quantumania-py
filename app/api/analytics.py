from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.services.database_service import DatabaseService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/job-trends")
async def get_job_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get job trends over time"""
    db_service = DatabaseService(db)
    return await db_service.get_job_trends(days)

@router.get("/backend-utilization")
async def get_backend_utilization(db: Session = Depends(get_db)):
    """Get backend utilization data"""
    db_service = DatabaseService(db)
    return await db_service.get_backend_utilization()

@router.get("/status-distribution")
async def get_status_distribution(db: Session = Depends(get_db)):
    """Get distribution of job statuses"""
    db_service = DatabaseService(db)
    stats = await db_service.get_job_statistics()
    
    total = stats['total_jobs']
    if total == 0:
        return {"distribution": []}
    
    distribution = [
        {"status": "RUNNING", "count": stats['running_jobs'], "percentage": (stats['running_jobs'] / total) * 100},
        {"status": "QUEUED", "count": stats['queued_jobs'], "percentage": (stats['queued_jobs'] / total) * 100},
        {"status": "DONE", "count": stats['completed_jobs'], "percentage": (stats['completed_jobs'] / total) * 100},
        {"status": "ERROR", "count": stats['error_jobs'], "percentage": (stats['error_jobs'] / total) * 100},
        {"status": "CANCELLED", "count": stats['cancelled_jobs'], "percentage": (stats['cancelled_jobs'] / total) * 100},
    ]
    
    return {"distribution": distribution, "total_jobs": total}

@router.get("/backend-comparison")
async def get_backend_comparison(db: Session = Depends(get_db)):
    """Compare backends by various metrics"""
    db_service = DatabaseService(db)
    
    backends = await db_service.get_all_backends()
    queue_info = await db_service.get_queue_info()
    utilization = await db_service.get_backend_utilization()
    
    # Create comparison data
    comparison = []
    utilization_map = {item['backend']: item for item in utilization.get('weekly_utilization', [])}
    queue_map = {q.backend_name: q for q in queue_info}
    
    for backend in backends:
        util_data = utilization_map.get(backend.name, {})
        queue_data = queue_map.get(backend.name)
        
        comparison.append({
            "name": backend.name,
            "n_qubits": backend.n_qubits or 0,
            "status": backend.status,
            "simulator": backend.simulator,
            "job_count": util_data.get('job_count', 0),
            "total_shots": util_data.get('total_shots', 0),
            "queue_length": backend.pending_jobs or 0,  # Use real IBM queue data
            "pending_jobs": backend.pending_jobs or 0,  # Add pending_jobs field for consistency
            "estimated_wait_time": queue_data.estimated_wait_time if queue_data else None
        })
    
    return {"backends": comparison}

@router.get("/performance-metrics")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """Get performance metrics and KPIs"""
    db_service = DatabaseService(db)
    
    job_stats = await db_service.get_job_statistics()
    backend_stats = await db_service.get_backend_statistics()
    
    # Calculate success rate
    total_completed = job_stats['completed_jobs'] + job_stats['error_jobs']
    success_rate = (job_stats['completed_jobs'] / total_completed * 100) if total_completed > 0 else 0
    
    # Calculate system utilization
    total_backends = backend_stats['total_backends']
    active_backends = backend_stats['operational_backends']
    system_availability = (active_backends / total_backends * 100) if total_backends > 0 else 0
    
    return {
        "success_rate": round(success_rate, 2),
        "system_availability": round(system_availability, 2),
        "average_queue_time": job_stats.get('average_queue_time'),
        "average_execution_time": job_stats.get('average_execution_time'),
        "total_quantum_time": sum([
            job_stats['completed_jobs'] * (job_stats.get('average_execution_time', 0) or 0)
        ]),
        "throughput": {
            "jobs_per_day": job_stats['total_jobs'] / 30,  # Assuming 30-day average
            "jobs_per_hour": job_stats['total_jobs'] / (30 * 24)
        }
    }

@router.get("/cost-analysis")
async def get_cost_analysis(db: Session = Depends(get_db)):
    """Get cost analysis data"""
    # This would require actual cost data from IBM Quantum
    # For now, return mock data
    return {
        "total_cost": 1250.75,
        "average_job_cost": 2.34,
        "cost_by_backend": [
            {"backend": "ibm_sherbrooke", "cost": 450.25},
            {"backend": "ibm_kyiv", "cost": 380.50},
            {"backend": "ibm_torino", "cost": 420.00}
        ],
        "cost_trends": [
            {"date": "2024-01-01", "cost": 45.50},
            {"date": "2024-01-02", "cost": 52.25},
            {"date": "2024-01-03", "cost": 38.75}
        ]
    }

@router.get("/user-activity")
async def get_user_activity(db: Session = Depends(get_db)):
    """Get user activity analytics"""
    # Mock user activity data
    return {
        "active_users": 245,
        "new_users_this_week": 15,
        "top_users": [
            {"user_id": "user_123", "job_count": 45, "total_shots": 125000},
            {"user_id": "user_456", "job_count": 38, "total_shots": 98000},
            {"user_id": "user_789", "job_count": 32, "total_shots": 87500}
        ],
        "user_distribution": [
            {"category": "Research", "count": 120},
            {"category": "Education", "count": 85},
            {"category": "Industry", "count": 40}
        ]
    }

@router.get("/regional-stats")
async def get_regional_statistics(db: Session = Depends(get_db)):
    """Get regional usage statistics"""
    # Mock regional data
    return {
        "regions": [
            {"region": "North America", "users": 125, "jobs": 2450},
            {"region": "Europe", "users": 89, "jobs": 1890},
            {"region": "Asia Pacific", "users": 67, "jobs": 1340},
            {"region": "Other", "users": 12, "jobs": 180}
        ],
        "peak_hours": [
            {"hour": 14, "job_count": 45},
            {"hour": 15, "job_count": 52},
            {"hour": 16, "job_count": 38}
        ]
    }
