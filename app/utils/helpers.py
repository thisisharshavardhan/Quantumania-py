"""
Utility functions for data processing and formatting
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import json

def format_timestamp(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO string"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

def parse_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime"""
    if not timestamp_str:
        return None
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None

def safe_json_loads(json_str: Optional[str]) -> Optional[Dict[str, Any]]:
    """Safely parse JSON string"""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

def safe_json_dumps(obj: Any) -> Optional[str]:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return None

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)

def format_duration_seconds(seconds: Optional[float]) -> Optional[str]:
    """Format duration in seconds to human readable format"""
    if seconds is None:
        return None
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def calculate_wait_time_category(wait_time: Optional[float]) -> str:
    """Categorize wait time"""
    if wait_time is None:
        return "unknown"
    elif wait_time < 60:
        return "short"
    elif wait_time < 300:
        return "medium"
    else:
        return "long"

def sanitize_backend_name(name: str) -> str:
    """Sanitize backend name for safe usage"""
    return name.lower().replace(' ', '_').replace('-', '_')

def format_qubit_count(n_qubits: Optional[int]) -> str:
    """Format qubit count with appropriate suffix"""
    if n_qubits is None:
        return "N/A"
    return f"{n_qubits} qubits"

def validate_job_status(status: str) -> bool:
    """Validate if job status is valid"""
    valid_statuses = {
        'INITIALIZING', 'QUEUED', 'VALIDATING', 
        'RUNNING', 'CANCELLED', 'DONE', 'ERROR'
    }
    return status.upper() in valid_statuses

def validate_backend_status(status: str) -> bool:
    """Validate if backend status is valid"""
    valid_statuses = {'operational', 'maintenance', 'internal', 'off'}
    return status.lower() in valid_statuses

def extract_error_message(error_data: Any) -> Optional[str]:
    """Extract readable error message from various error formats"""
    if isinstance(error_data, str):
        return error_data
    elif isinstance(error_data, dict):
        # Try common error message fields
        for field in ['message', 'error', 'detail', 'description']:
            if field in error_data and error_data[field]:
                return str(error_data[field])
    return None

def format_cost(cost: Optional[float]) -> str:
    """Format cost with appropriate currency symbol"""
    if cost is None:
        return "N/A"
    return f"${cost:.2f}"

def calculate_efficiency_score(completed_jobs: int, error_jobs: int, cancelled_jobs: int) -> float:
    """Calculate efficiency score based on job outcomes"""
    total_jobs = completed_jobs + error_jobs + cancelled_jobs
    if total_jobs == 0:
        return 0.0
    
    # Weight completed jobs positively, errors negatively
    score = (completed_jobs * 1.0 - error_jobs * 0.5 - cancelled_jobs * 0.3) / total_jobs
    return max(0.0, min(1.0, score))  # Clamp between 0 and 1

def group_by_time_period(data: List[Dict[str, Any]], time_field: str, period: str = 'day') -> Dict[str, List[Dict[str, Any]]]:
    """Group data by time period"""
    grouped = {}
    
    for item in data:
        timestamp = item.get(time_field)
        if not timestamp:
            continue
            
        dt = parse_timestamp(timestamp) if isinstance(timestamp, str) else timestamp
        if not dt:
            continue
            
        if period == 'day':
            key = dt.strftime('%Y-%m-%d')
        elif period == 'hour':
            key = dt.strftime('%Y-%m-%d %H:00')
        elif period == 'week':
            key = dt.strftime('%Y-W%U')
        else:
            key = dt.strftime('%Y-%m-%d')
            
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    
    return grouped

def get_backend_type_category(backend_name: str, is_simulator: bool) -> str:
    """Categorize backend type"""
    if is_simulator:
        return "simulator"
    elif "ibm" in backend_name.lower():
        return "ibm_quantum"
    else:
        return "other"

def calculate_trend(current_value: float, previous_value: float) -> Dict[str, Any]:
    """Calculate trend direction and percentage"""
    if previous_value == 0:
        return {
            "direction": "neutral",
            "percentage": 0.0,
            "change": current_value
        }
    
    change = current_value - previous_value
    percentage = (change / previous_value) * 100
    
    if change > 0:
        direction = "up"
    elif change < 0:
        direction = "down"
    else:
        direction = "neutral"
    
    return {
        "direction": direction,
        "percentage": round(abs(percentage), 2),
        "change": round(change, 2)
    }
