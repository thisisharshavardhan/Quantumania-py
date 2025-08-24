from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    RUNNING = "RUNNING"
    CANCELLED = "CANCELLED"
    DONE = "DONE"
    ERROR = "ERROR"

class BackendStatus(str, Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    INTERNAL = "internal"
    OFF = "off"

class QuantumJobSchema(BaseModel):
    id: Optional[int] = None
    job_id: str
    name: Optional[str] = None
    backend_name: str
    backend_version: Optional[str] = None
    backend_status: Optional[str] = None
    backend_basis_gates: Optional[List[str]] = None
    backend_coupling_map: Optional[List[List[int]]] = None
    backend_n_qubits: Optional[int] = None
    status: JobStatus
    creation_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    user_id: Optional[str] = None
    program_id: Optional[str] = None
    hub: Optional[str] = None
    group: Optional[str] = None
    project: Optional[str] = None
    cost: Optional[float] = None
    usage: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    queue_position: Optional[int] = None
    estimated_start_time: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    shots: Optional[int] = None
    circuits: Optional[int] = None
    transpiled_circuits: Optional[Dict[str, Any]] = None
    qobj: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QuantumBackendSchema(BaseModel):
    id: Optional[int] = None
    name: str
    backend_version: Optional[str] = None
    backend_type: Optional[str] = None
    status: Optional[BackendStatus] = None
    max_shots: Optional[int] = None
    max_experiments: Optional[int] = None
    n_qubits: Optional[int] = None
    pending_jobs: Optional[int] = 0
    basis_gates: Optional[List[str]] = None
    coupling_map: Optional[List[List[int]]] = None
    supported_instructions: Optional[List[str]] = None
    local: Optional[bool] = False
    simulator: Optional[bool] = False
    conditional: Optional[bool] = False
    open_pulse: Optional[bool] = False
    memory: Optional[bool] = False
    credits_required: Optional[bool] = True
    description: Optional[str] = None
    online_date: Optional[datetime] = None
    dt: Optional[float] = None
    dtm: Optional[float] = None
    processor_type: Optional[Dict[str, Any]] = None
    parametric_pulses: Optional[List[str]] = None
    default_rep_delay: Optional[float] = None
    max_rep_delay: Optional[float] = None
    rep_delay_range: Optional[List[float]] = None
    default_meas_level: Optional[int] = None
    meas_levels: Optional[List[int]] = None
    qubit_lo_range: Optional[List[List[float]]] = None
    meas_lo_range: Optional[List[List[float]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobQueueSchema(BaseModel):
    id: Optional[int] = None
    backend_name: str
    queue_length: int = 0
    pending_jobs: int = 0
    running_jobs: int = 0
    average_wait_time: Optional[float] = None
    estimated_wait_time: Optional[float] = None
    status: Optional[str] = None
    last_updated: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SystemStatusSchema(BaseModel):
    id: Optional[int] = None
    service_name: str
    status: str
    message: Optional[str] = None
    response_time: Optional[float] = None
    last_check: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobStatsSchema(BaseModel):
    total_jobs: int
    running_jobs: int
    queued_jobs: int
    completed_jobs: int
    error_jobs: int
    cancelled_jobs: int
    average_queue_time: Optional[float] = None
    average_execution_time: Optional[float] = None

class BackendStatsSchema(BaseModel):
    total_backends: int
    operational_backends: int
    maintenance_backends: int
    offline_backends: int
    simulators: int
    real_devices: int
    total_qubits: int
    average_queue_length: Optional[float] = None

class DashboardDataSchema(BaseModel):
    job_stats: JobStatsSchema
    backend_stats: BackendStatsSchema
    recent_jobs: List[QuantumJobSchema]
    queue_info: List[JobQueueSchema]
    system_status: List[SystemStatusSchema]
    backend_utilization: Dict[str, Any]
    
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

class FilterParams(BaseModel):
    status: Optional[str] = None
    backend: Optional[str] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=1000)
