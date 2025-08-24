from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.quantum_service import quantum_service
from app.services.database_service import DatabaseService
from app.schemas.quantum_schemas import QuantumBackendSchema

router = APIRouter(prefix="/backends", tags=["Backends"])

@router.get("/live-metrics")
async def get_all_backends_live_metrics():
    """Get comprehensive live metrics for all backends"""
    try:
        backends = await quantum_service.get_all_backends()
        
        # Calculate comprehensive metrics
        total_qubits = sum(b.get('n_qubits', 0) for b in backends)
        total_pending = sum(b.get('pending_jobs', 0) for b in backends if b.get('pending_jobs'))
        operational_count = len([b for b in backends if b.get('status') == 'operational'])
        
        # Get queue information
        queue_data = []
        for backend in backends:
            if backend.get('status') == 'operational':
                queue_data.append({
                    'backend_name': backend['name'],
                    'queue_length': backend.get('pending_jobs', 0),
                    'max_shots': backend.get('max_shots', 0),
                    'qubits': backend.get('n_qubits', 0)
                })
        
        return {
            "timestamp": "2024-01-01T00:00:00Z",
            "total_backends": len(backends),
            "operational_backends": operational_count,
            "total_pending_jobs": total_pending,
            "real_devices": len([b for b in backends if not b.get('simulator', True)]),
            "simulators": len([b for b in backends if b.get('simulator', False)]),
            "total_qubits": total_qubits,
            "backends_with_queues": len([b for b in backends if b.get('pending_jobs', 0) > 0]),
            "average_qubits": total_qubits / len(backends) if backends else 0,
            "queue_info": queue_data,
            "backends": backends[:5],  # Limit for performance
            "system_status": "healthy",
            "last_sync": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting live metrics: {str(e)}")

@router.get("/", response_model=List[QuantumBackendSchema])
async def get_all_backends(db: Session = Depends(get_db)):
    """Get all quantum backends"""
    db_service = DatabaseService(db)
    backends = await db_service.get_all_backends()
    return [QuantumBackendSchema.from_orm(backend) for backend in backends]

@router.get("/{backend_name}", response_model=QuantumBackendSchema)
async def get_backend(
    backend_name: str,
    db: Session = Depends(get_db)
):
    """Get a specific backend by name"""
    db_service = DatabaseService(db)
    backend = await db_service.get_backend(backend_name)
    
    if not backend:
        raise HTTPException(status_code=404, detail="Backend not found")
    
    return QuantumBackendSchema.from_orm(backend)

@router.post("/sync")
async def sync_backends_from_ibm(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sync backends from IBM Quantum (runs in background)"""
    background_tasks.add_task(sync_backends_task, db)
    return {"message": "Backend sync started in background"}

async def sync_backends_task(db: Session):
    """Background task to sync backends from IBM Quantum"""
    try:
        backends_data = await quantum_service.get_all_backends()
        
        db_service = DatabaseService(db)
        await db_service.bulk_upsert_backends(backends_data)
        
        print(f"Successfully synced {len(backends_data)} backends")
    except Exception as e:
        print(f"Error syncing backends: {e}")

@router.get("/stats/overview")
async def get_backend_statistics(db: Session = Depends(get_db)):
    """Get backend statistics overview"""
    db_service = DatabaseService(db)
    return await db_service.get_backend_statistics()

@router.get("/utilization/weekly")
async def get_backend_utilization(db: Session = Depends(get_db)):
    """Get backend utilization data"""
    db_service = DatabaseService(db)
    return await db_service.get_backend_utilization()

@router.get("/filter/operational")
async def get_operational_backends(db: Session = Depends(get_db)):
    """Get only operational backends"""
    db_service = DatabaseService(db)
    backends = await db_service.get_all_backends()
    operational = [backend for backend in backends if backend.status == 'operational']
    return [QuantumBackendSchema.from_orm(backend) for backend in operational]

@router.get("/filter/simulators")
async def get_simulators(db: Session = Depends(get_db)):
    """Get only simulator backends"""
    db_service = DatabaseService(db)
    backends = await db_service.get_all_backends()
    simulators = [backend for backend in backends if backend.simulator]
    return [QuantumBackendSchema.from_orm(backend) for backend in simulators]

@router.get("/filter/real-devices")
async def get_real_devices(db: Session = Depends(get_db)):
    """Get only real quantum device backends"""
    db_service = DatabaseService(db)
    backends = await db_service.get_all_backends()
    real_devices = [backend for backend in backends if not backend.simulator]
    return [QuantumBackendSchema.from_orm(backend) for backend in real_devices]

@router.get("/{backend_name}/live-status")
async def get_backend_live_status(backend_name: str):
    """Get real-time live status for a specific backend directly from IBM"""
    try:
        # Get live data directly from IBM Quantum service
        backend_info = await quantum_service.get_backend_status(backend_name)
        if not backend_info:
            raise HTTPException(status_code=404, detail="Backend not found")
        return backend_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting live status: {str(e)}")

@router.get("/{backend_name}/queue")
async def get_backend_queue_info(
    backend_name: str,
    db: Session = Depends(get_db)
):
    """Get queue information for a specific backend"""
    db_service = DatabaseService(db)
    queue_info = await db_service.get_queue_info()
    backend_queue = next((q for q in queue_info if q.backend_name == backend_name), None)
    
    if not backend_queue:
        raise HTTPException(status_code=404, detail="Queue information not found for this backend")
    
    return backend_queue
