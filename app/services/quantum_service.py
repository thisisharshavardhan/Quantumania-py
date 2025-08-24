import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx

# Try to import Qiskit components with graceful fallback
try:
    from qiskit_ibm_runtime import QiskitRuntimeService
    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("qiskit_ibm_runtime not available")

try:
    from qiskit_ibm_provider import IBMProvider
    PROVIDER_AVAILABLE = True
except ImportError:
    PROVIDER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("qiskit_ibm_provider not available")

from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.quantum_models import QuantumJob, QuantumBackend, JobQueue
from app.schemas.quantum_schemas import QuantumJobSchema, QuantumBackendSchema, JobQueueSchema

logger = logging.getLogger(__name__)

class QuantumService:
    def __init__(self):
        self.service = None
        self.provider = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize IBM Quantum connections - REAL DATA ONLY"""
        if not settings.ibm_quantum_token or settings.ibm_quantum_token == "your_ibm_quantum_token_here":
            raise Exception("IBM Quantum token is required. Please set IBM_QUANTUM_TOKEN in .env file")
            
        if not RUNTIME_AVAILABLE:
            raise Exception("qiskit_ibm_runtime is required but not available. Please install: pip install qiskit-ibm-runtime")
            
        try:
            # Initialize IBM Quantum Runtime Service
            self.service = QiskitRuntimeService(
                channel=settings.ibm_quantum_channel,
                token=settings.ibm_quantum_token
            )
            
            # Test the connection by trying to get backends
            test_backends = self.service.backends()
            if not test_backends:
                raise Exception("No backends available - invalid token or connection failed")
                
            self.initialized = True
            logger.info(f"IBM Quantum Runtime service initialized successfully with {len(test_backends)} backends")
            
        except Exception as e:
            logger.error(f"Failed to initialize IBM Quantum service: {e}")
            raise Exception(f"Cannot connect to IBM Quantum: {e}. Real data connection required.")
            
    async def get_all_backends(self) -> List[Dict[str, Any]]:
        """Get all available backends from IBM Quantum - REAL DATA ONLY"""
        if not self.initialized:
            raise Exception("IBM Quantum service not initialized. Real connection required.")
            
        backends_data = []
        
        try:
            # Get backends from Runtime Service
            runtime_backends = self.service.backends()
            logger.info(f"Retrieved {len(runtime_backends)} backends from IBM Quantum")
            
            for backend in runtime_backends:
                try:
                    config = backend.configuration()
                    status = backend.status()
                    properties = None
                    
                    try:
                        properties = backend.properties()
                    except:
                        logger.warning(f"Could not get properties for backend {backend.name}")
                        
                    # Map IBM status to our schema
                    status_msg = status.status_msg if hasattr(status, 'status_msg') else 'unknown'
                    if status_msg == 'active':
                        status_msg = 'operational'
                    elif status_msg not in ['operational', 'maintenance', 'internal', 'off']:
                        status_msg = 'maintenance'  # Default fallback
                    
                    # Get additional real-time data
                    queue_length = status.pending_jobs if hasattr(status, 'pending_jobs') else 0
                    operational_status = status.operational if hasattr(status, 'operational') else True
                    
                    # Get processor information from config
                    processor_type = getattr(config, 'processor_type', {})
                    if isinstance(processor_type, dict):
                        processor_family = processor_type.get('family', 'unknown')
                        processor_revision = processor_type.get('revision', 'unknown')
                    else:
                        processor_family = 'unknown'
                        processor_revision = 'unknown'
                    
                    # Get error rates if available from properties
                    error_rate = None
                    gate_time = None
                    if properties:
                        try:
                            # Get average gate error rate
                            if hasattr(properties, 'gates') and properties.gates:
                                total_error = sum(gate.parameters[0].value for gate in properties.gates if gate.parameters)
                                error_rate = total_error / len(properties.gates) if properties.gates else None
                            
                            # Get average gate time
                            if hasattr(properties, 'gates') and properties.gates:
                                total_time = sum(gate.parameters[1].value for gate in properties.gates if len(gate.parameters) > 1)
                                gate_time = total_time / len(properties.gates) if properties.gates else None
                        except:
                            pass
                    
                    backend_data = {
                        "name": backend.name,
                        "n_qubits": config.n_qubits,
                        "status": status_msg,
                        "simulator": getattr(config, 'simulator', False),
                        "local": getattr(config, 'local', False),
                        "pending_jobs": queue_length,
                        "operational": operational_status,
                        "basis_gates": getattr(config, 'basis_gates', []),
                        "coupling_map": getattr(config, 'coupling_map', []),
                        "description": getattr(config, 'description', ''),
                        "online_date": getattr(config, 'online_date', None),
                        "max_shots": getattr(config, 'max_shots', None),
                        "max_experiments": getattr(config, 'max_experiments', None),
                        "processor_type": {
                            "family": processor_family,
                            "revision": processor_revision
                        },
                        "supported_instructions": getattr(config, 'supported_instructions', []),
                        "memory": getattr(config, 'memory', False),
                        "open_pulse": getattr(config, 'open_pulse', False),
                        "dynamic_reprate_enabled": getattr(config, 'dynamic_reprate_enabled', False),
                        "credits_required": getattr(config, 'credits_required', True),
                        "rep_delay_range": getattr(config, 'rep_delay_range', []),
                        "default_rep_delay": getattr(config, 'default_rep_delay', None),
                        "max_rep_delay": getattr(config, 'max_rep_delay', None),
                        "parametric_pulses": getattr(config, 'parametric_pulses', []),
                        "dt": getattr(config, 'dt', None),
                        "dtm": getattr(config, 'dtm', None),
                        "conditional": getattr(config, 'conditional', False)
                    }
                    backends_data.append(backend_data)
                    logger.info(f"Processed backend: {backend.name} ({backend_data['n_qubits']} qubits)")
                except Exception as e:
                    logger.error(f"Error processing backend {backend.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error fetching backends from IBM Quantum: {e}")
            raise Exception(f"Failed to get real backend data: {e}")
            
        return backends_data
    
    async def get_backend_status(self, backend_name: str) -> Dict[str, Any]:
        """Get live status for a specific backend"""
        if not self.initialized:
            raise Exception("IBM Quantum service not initialized")
            
        try:
            backend = self.service.backend(backend_name)
            config = backend.configuration()
            status = backend.status()
            
            # Get real-time status information
            live_status = {
                "name": backend.name,
                "status": status.status_msg if hasattr(status, 'status_msg') else 'unknown',
                "operational": status.operational if hasattr(status, 'operational') else True,
                "pending_jobs": status.pending_jobs if hasattr(status, 'pending_jobs') else 0,
                "num_qubits": config.n_qubits,
                "last_update": status.status_msg if hasattr(status, 'status_msg') else None,
                "credits_required": getattr(config, 'credits_required', True),
                "max_shots": getattr(config, 'max_shots', None),
                "simulator": getattr(config, 'simulator', False)
            }
            
            return live_status
            
        except Exception as e:
            logger.error(f"Error getting status for backend {backend_name}: {e}")
            return None
    
    async def get_jobs(self, limit: int = 100, backend: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get jobs from IBM Quantum - REAL DATA ONLY"""
        if not self.initialized:
            raise Exception("IBM Quantum service not initialized. Real connection required.")
            
        jobs_data = []
        
        try:
            # Get jobs from Runtime Service
            job_filter = {}
            if backend:
                job_filter['backend'] = backend
                
            jobs = self.service.jobs(limit=limit, **job_filter)
            logger.info(f"Retrieved {len(jobs)} jobs from IBM Quantum")
            
            for job in jobs:
                try:
                    job_data = {
                        'job_id': job.job_id(),
                        'name': getattr(job, 'name', None),
                        'backend_name': job.backend().name if job.backend() else 'unknown',
                        'status': job.status().name if hasattr(job.status(), 'name') else str(job.status()),
                        'creation_date': job.creation_date,
                        'tags': getattr(job, 'tags', []),
                        'user_id': getattr(job, 'user_id', None),
                        'program_id': getattr(job, 'program_id', None),
                        'usage': job.usage() if hasattr(job, 'usage') else {},
                        'error_message': job.error_message() if hasattr(job, 'error_message') else None,
                        'queue_position': getattr(job, 'queue_position', None),
                        'result': job.result().to_dict() if hasattr(job, 'result') and job.status().name == 'DONE' else None
                    }
                    jobs_data.append(job_data)
                    logger.info(f"Processed job: {job.job_id()} - {job_data['status']}")
                except Exception as e:
                    logger.error(f"Error processing job {job.job_id()}: {e}")
                    
        except Exception as e:
            logger.error(f"Error fetching jobs from IBM Quantum: {e}")
            raise Exception(f"Failed to get real job data: {e}")
        
        return jobs_data
    
    def _get_mock_jobs(self) -> List[Dict[str, Any]]:
        """Generate mock job data for demo purposes"""
        import random
        from datetime import datetime, timedelta
        
        statuses = ['INITIALIZING', 'QUEUED', 'VALIDATING', 'RUNNING', 'DONE', 'ERROR', 'CANCELLED']
        backends = ['ibm_sherbrooke', 'ibm_kyiv', 'ibm_torino', 'ibmq_qasm_simulator']
        
        mock_jobs = []
        for i in range(50):
            status = random.choice(statuses)
            backend = random.choice(backends)
            creation_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            job_data = {
                'job_id': f'job_{i:06d}_{random.randint(1000, 9999)}',
                'name': f'quantum_job_{i}',
                'backend_name': backend,
                'status': status,
                'creation_date': creation_date,
                'tags': [f'tag_{random.randint(1, 5)}'],
                'user_id': f'user_{random.randint(1, 100)}',
                'shots': random.randint(100, 10000),
                'circuits': random.randint(1, 10),
                'queue_position': random.randint(1, 50) if status == 'QUEUED' else None,
                'cost': round(random.uniform(0.1, 10.0), 2),
                'usage': {
                    'quantum_seconds': round(random.uniform(0.01, 1.0), 4),
                    'billed_units': random.randint(1, 100)
                }
            }
            mock_jobs.append(job_data)
            
        return mock_jobs
    
    async def get_queue_info(self) -> List[Dict[str, Any]]:
        """Get queue information for all backends - REAL DATA ONLY"""
        if not self.initialized:
            raise Exception("IBM Quantum service not initialized. Real connection required.")
            
        queue_data = []
        
        try:
            backends = await self.get_all_backends()
            
            for backend_info in backends:
                try:
                    # Get the actual backend object
                    backend = self.service.backend(backend_info['name'])
                    status = backend.status()
                    
                    queue_info = {
                        'backend_name': backend_info['name'],
                        'queue_length': getattr(status, 'pending_jobs', 0),
                        'pending_jobs': getattr(status, 'pending_jobs', 0),
                        'running_jobs': 1 if getattr(status, 'status_msg', '') == 'active' else 0,
                        'average_wait_time': None,  # IBM doesn't provide this directly
                        'estimated_wait_time': None,  # IBM doesn't provide this directly
                        'status': getattr(status, 'status_msg', 'unknown'),
                        'last_updated': datetime.now()
                    }
                    queue_data.append(queue_info)
                    logger.info(f"Queue info for {backend_info['name']}: {queue_info['queue_length']} pending jobs")
                except Exception as e:
                    logger.error(f"Error getting queue info for {backend_info['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error fetching queue info: {e}")
            raise Exception(f"Failed to get real queue data: {e}")
            
        return queue_data
    
    async def get_system_status(self) -> List[Dict[str, Any]]:
        """Get system status information - REAL DATA ONLY"""
        if not self.initialized:
            raise Exception("IBM Quantum service not initialized. Real connection required.")
            
        status_data = []
        
        try:
            # Test IBM Quantum Runtime service
            start_time = datetime.now()
            backends = self.service.backends()
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            status_info = {
                'service_name': 'IBM Quantum Runtime',
                'status': 'operational' if len(backends) > 0 else 'degraded',
                'message': f'Service responding with {len(backends)} backends available',
                'response_time': response_time,
                'last_check': datetime.now()
            }
            status_data.append(status_info)
            
            # Check individual backend status
            operational_count = 0
            for backend in backends[:5]:  # Check first 5 backends
                try:
                    start_time = datetime.now()
                    status = backend.status()
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    if getattr(status, 'operational', True):
                        operational_count += 1
                    
                    backend_status = {
                        'service_name': f'Backend: {backend.name}',
                        'status': 'operational' if getattr(status, 'operational', True) else 'maintenance',
                        'message': getattr(status, 'status_msg', 'Status unknown'),
                        'response_time': response_time,
                        'last_check': datetime.now()
                    }
                    status_data.append(backend_status)
                    
                except Exception as e:
                    logger.error(f"Error checking status for {backend.name}: {e}")
            
            logger.info(f"System status check complete: {operational_count} operational backends")
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise Exception(f"Failed to get real system status: {e}")
            
        return status_data

# Global instance
quantum_service = QuantumService()
