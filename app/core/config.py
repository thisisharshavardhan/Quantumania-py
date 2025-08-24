from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # IBM Quantum
    ibm_quantum_token: str = os.getenv("IBM_QUANTUM_TOKEN", "")
    ibm_quantum_instance: str = os.getenv("IBM_QUANTUM_INSTANCE", "ibm_quantum")
    ibm_quantum_channel: str = os.getenv("IBM_QUANTUM_CHANNEL", "ibm_quantum")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./quantum_jobs.db")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API Settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "quantum-jobs-secret-key-2024")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # External APIs
    quantum_computing_report_api: str = os.getenv("QUANTUM_COMPUTING_REPORT_API", "https://quantumcomputingreport.com/api")
    ibm_quantum_network_api: str = os.getenv("IBM_QUANTUM_NETWORK_API", "https://quantum-computing.ibm.com/api")
    
    # Background Jobs
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
