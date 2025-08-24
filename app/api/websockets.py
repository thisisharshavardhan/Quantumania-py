from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import asyncio
import json
import logging
from typing import List

from app.core.database import get_db
from app.services.database_service import DatabaseService

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(10)  # Update every 10 seconds
            
            # Get fresh data (this would normally use a database session)
            dashboard_data = {
                "type": "dashboard_update",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "total_jobs": 1250,
                    "running_jobs": 45,
                    "queued_jobs": 120,
                    "completed_jobs": 1085
                }
            }
            
            await manager.send_personal_message(json.dumps(dashboard_data), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/ws/jobs")
async def jobs_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time job updates"""
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(5)  # Update every 5 seconds
            
            job_update = {
                "type": "job_update",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "new_jobs": 3,
                    "status_changes": [
                        {"job_id": "job_123", "old_status": "QUEUED", "new_status": "RUNNING"},
                        {"job_id": "job_456", "old_status": "RUNNING", "new_status": "DONE"}
                    ]
                }
            }
            
            await manager.send_personal_message(json.dumps(job_update), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.websocket("/ws/queue")
async def queue_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time queue updates"""
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(15)  # Update every 15 seconds
            
            queue_update = {
                "type": "queue_update",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {
                    "backend_updates": [
                        {"backend": "ibm_sherbrooke", "queue_length": 25, "estimated_wait": 120},
                        {"backend": "ibm_kyiv", "queue_length": 18, "estimated_wait": 95}
                    ]
                }
            }
            
            await manager.send_personal_message(json.dumps(queue_update), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
