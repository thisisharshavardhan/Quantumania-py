from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
from app.models.quantum_models import QuantumJob, QuantumBackend, JobQueue, SystemStatus
from app.schemas.quantum_schemas import (
    QuantumJobSchema, QuantumBackendSchema, JobQueueSchema, 
    SystemStatusSchema, FilterParams, PaginatedResponse
)

class DatabaseService:
    
    def __init__(self, db: Session):
        self.db = db
    
    # Job operations
    async def create_job(self, job_data: Dict[str, Any]) -> QuantumJob:
        """Create a new quantum job record"""
        job = QuantumJob(**job_data)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    async def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Optional[QuantumJob]:
        """Update an existing quantum job"""
        job = self.db.query(QuantumJob).filter(QuantumJob.job_id == job_id).first()
        if job:
            for key, value in job_data.items():
                setattr(job, key, value)
            job.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(job)
        return job
    
    async def get_job(self, job_id: str) -> Optional[QuantumJob]:
        """Get a specific job by job_id"""
        return self.db.query(QuantumJob).filter(QuantumJob.job_id == job_id).first()
    
    async def get_jobs(self, filters: FilterParams) -> PaginatedResponse:
        """Get jobs with filtering and pagination"""
        query = self.db.query(QuantumJob)
        
        # Apply filters
        if filters.status:
            query = query.filter(QuantumJob.status == filters.status)
        if filters.backend:
            query = query.filter(QuantumJob.backend_name == filters.backend)
        if filters.user_id:
            query = query.filter(QuantumJob.user_id == filters.user_id)
        if filters.start_date:
            query = query.filter(QuantumJob.creation_date >= filters.start_date)
        if filters.end_date:
            query = query.filter(QuantumJob.creation_date <= filters.end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (filters.page - 1) * filters.per_page
        jobs = query.order_by(desc(QuantumJob.creation_date)).offset(offset).limit(filters.per_page).all()
        
        # Calculate pagination info
        pages = (total + filters.per_page - 1) // filters.per_page
        has_next = filters.page < pages
        has_prev = filters.page > 1
        
        return PaginatedResponse(
            items=[QuantumJobSchema.from_orm(job) for job in jobs],
            total=total,
            page=filters.page,
            per_page=filters.per_page,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
    
    async def get_recent_jobs(self, limit: int = 20) -> List[QuantumJob]:
        """Get recent jobs"""
        return self.db.query(QuantumJob).order_by(desc(QuantumJob.creation_date)).limit(limit).all()
    
    async def bulk_create_jobs(self, jobs_data: List[Dict[str, Any]]) -> List[QuantumJob]:
        """Bulk create jobs"""
        jobs = []
        for job_data in jobs_data:
            # Check if job already exists
            existing_job = self.db.query(QuantumJob).filter(QuantumJob.job_id == job_data['job_id']).first()
            if not existing_job:
                job = QuantumJob(**job_data)
                jobs.append(job)
        
        if jobs:
            self.db.add_all(jobs)
            self.db.commit()
        
        return jobs
    
    # Backend operations
    async def create_backend(self, backend_data: Dict[str, Any]) -> QuantumBackend:
        """Create a new backend record"""
        backend = QuantumBackend(**backend_data)
        self.db.add(backend)
        self.db.commit()
        self.db.refresh(backend)
        return backend
    
    async def update_backend(self, name: str, backend_data: Dict[str, Any]) -> Optional[QuantumBackend]:
        """Update an existing backend"""
        backend = self.db.query(QuantumBackend).filter(QuantumBackend.name == name).first()
        if backend:
            for key, value in backend_data.items():
                setattr(backend, key, value)
            backend.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(backend)
        return backend
    
    async def get_backend(self, name: str) -> Optional[QuantumBackend]:
        """Get a specific backend by name"""
        return self.db.query(QuantumBackend).filter(QuantumBackend.name == name).first()
    
    async def get_all_backends(self) -> List[QuantumBackend]:
        """Get all backends"""
        return self.db.query(QuantumBackend).all()
    
    async def bulk_upsert_backends(self, backends_data: List[Dict[str, Any]]) -> List[QuantumBackend]:
        """Bulk upsert backends"""
        backends = []
        for backend_data in backends_data:
            existing_backend = self.db.query(QuantumBackend).filter(QuantumBackend.name == backend_data['name']).first()
            if existing_backend:
                # Update existing
                for key, value in backend_data.items():
                    setattr(existing_backend, key, value)
                existing_backend.updated_at = datetime.now()
                backends.append(existing_backend)
            else:
                # Create new
                backend = QuantumBackend(**backend_data)
                self.db.add(backend)
                backends.append(backend)
        
        self.db.commit()
        return backends
    
    # Queue operations
    async def update_queue_info(self, queue_data: List[Dict[str, Any]]) -> List[JobQueue]:
        """Update queue information"""
        queues = []
        for data in queue_data:
            existing_queue = self.db.query(JobQueue).filter(JobQueue.backend_name == data['backend_name']).first()
            if existing_queue:
                for key, value in data.items():
                    setattr(existing_queue, key, value)
                existing_queue.last_updated = datetime.now()
                queues.append(existing_queue)
            else:
                queue = JobQueue(**data)
                self.db.add(queue)
                queues.append(queue)
        
        self.db.commit()
        return queues
    
    async def get_queue_info(self) -> List[JobQueue]:
        """Get all queue information"""
        return self.db.query(JobQueue).all()
    
    # System status operations
    async def update_system_status(self, status_data: List[Dict[str, Any]]) -> List[SystemStatus]:
        """Update system status"""
        statuses = []
        for data in status_data:
            existing_status = self.db.query(SystemStatus).filter(
                SystemStatus.service_name == data['service_name']
            ).first()
            
            if existing_status:
                for key, value in data.items():
                    setattr(existing_status, key, value)
                existing_status.last_check = datetime.now()
                statuses.append(existing_status)
            else:
                status = SystemStatus(**data)
                self.db.add(status)
                statuses.append(status)
        
        self.db.commit()
        return statuses
    
    async def get_system_status(self) -> List[SystemStatus]:
        """Get all system status"""
        return self.db.query(SystemStatus).all()
    
    # Analytics and statistics
    async def get_job_statistics(self) -> Dict[str, Any]:
        """Get job statistics"""
        total_jobs = self.db.query(QuantumJob).count()
        running_jobs = self.db.query(QuantumJob).filter(QuantumJob.status == 'RUNNING').count()
        queued_jobs = self.db.query(QuantumJob).filter(QuantumJob.status == 'QUEUED').count()
        completed_jobs = self.db.query(QuantumJob).filter(QuantumJob.status == 'DONE').count()
        error_jobs = self.db.query(QuantumJob).filter(QuantumJob.status == 'ERROR').count()
        cancelled_jobs = self.db.query(QuantumJob).filter(QuantumJob.status == 'CANCELLED').count()
        
        # Calculate average times
        avg_queue_time = self.db.query(func.avg(
            func.julianday(QuantumJob.start_time) - func.julianday(QuantumJob.creation_date)
        )).filter(
            and_(QuantumJob.start_time.isnot(None), QuantumJob.creation_date.isnot(None))
        ).scalar()
        
        avg_execution_time = self.db.query(func.avg(
            func.julianday(QuantumJob.end_time) - func.julianday(QuantumJob.start_time)
        )).filter(
            and_(QuantumJob.end_time.isnot(None), QuantumJob.start_time.isnot(None))
        ).scalar()
        
        return {
            'total_jobs': total_jobs,
            'running_jobs': running_jobs,
            'queued_jobs': queued_jobs,
            'completed_jobs': completed_jobs,
            'error_jobs': error_jobs,
            'cancelled_jobs': cancelled_jobs,
            'average_queue_time': avg_queue_time * 24 * 3600 if avg_queue_time else None,  # Convert to seconds
            'average_execution_time': avg_execution_time * 24 * 3600 if avg_execution_time else None
        }
    
    async def get_backend_statistics(self) -> Dict[str, Any]:
        """Get backend statistics"""
        total_backends = self.db.query(QuantumBackend).count()
        operational_backends = self.db.query(QuantumBackend).filter(QuantumBackend.status == 'operational').count()
        maintenance_backends = self.db.query(QuantumBackend).filter(QuantumBackend.status == 'maintenance').count()
        offline_backends = self.db.query(QuantumBackend).filter(QuantumBackend.status == 'off').count()
        simulators = self.db.query(QuantumBackend).filter(QuantumBackend.simulator == True).count()
        real_devices = self.db.query(QuantumBackend).filter(QuantumBackend.simulator == False).count()
        
        total_qubits = self.db.query(func.sum(QuantumBackend.n_qubits)).filter(
            QuantumBackend.simulator == False
        ).scalar() or 0
        
        avg_queue_length = self.db.query(func.avg(JobQueue.queue_length)).scalar()
        
        return {
            'total_backends': total_backends,
            'operational_backends': operational_backends,
            'maintenance_backends': maintenance_backends,
            'offline_backends': offline_backends,
            'simulators': simulators,
            'real_devices': real_devices,
            'total_qubits': int(total_qubits),
            'average_queue_length': avg_queue_length
        }
    
    async def get_backend_utilization(self) -> Dict[str, Any]:
        """Get backend utilization data"""
        # Get job counts per backend for the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        
        utilization_data = self.db.query(
            QuantumJob.backend_name,
            func.count(QuantumJob.id).label('job_count'),
            func.sum(QuantumJob.shots).label('total_shots')
        ).filter(
            QuantumJob.creation_date >= week_ago
        ).group_by(QuantumJob.backend_name).all()
        
        return {
            'weekly_utilization': [
                {
                    'backend': item.backend_name,
                    'job_count': item.job_count,
                    'total_shots': item.total_shots or 0
                }
                for item in utilization_data
            ]
        }
    
    async def get_job_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get job trends over time"""
        start_date = datetime.now() - timedelta(days=days)
        
        daily_jobs = self.db.query(
            func.date(QuantumJob.creation_date).label('date'),
            func.count(QuantumJob.id).label('count')
        ).filter(
            QuantumJob.creation_date >= start_date
        ).group_by(func.date(QuantumJob.creation_date)).order_by('date').all()
        
        return {
            'daily_jobs': [
                {'date': str(item.date), 'count': item.count}
                for item in daily_jobs
            ]
        }
