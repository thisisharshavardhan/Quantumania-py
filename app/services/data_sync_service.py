import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.services.quantum_service import quantum_service
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DataSyncService:
    """Background service for periodic data synchronization"""
    
    def __init__(self):
        self.running = False
        
    async def start(self):
        """Start the background sync service"""
        self.running = True
        logger.info("Starting data sync service")
        
        # Run sync tasks
        await asyncio.gather(
            self.sync_jobs_periodically(),
            self.sync_backends_periodically(),
            self.sync_queue_info_periodically(),
            self.sync_system_status_periodically()
        )
    
    async def stop(self):
        """Stop the background sync service"""
        self.running = False
        logger.info("Stopping data sync service")
    
    async def sync_jobs_periodically(self):
        """Sync jobs every 30 seconds"""
        while self.running:
            try:
                await self.sync_jobs()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Error syncing jobs: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def sync_backends_periodically(self):
        """Sync backends every 5 minutes"""
        while self.running:
            try:
                await self.sync_backends()
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Error syncing backends: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def sync_queue_info_periodically(self):
        """Sync queue info every 15 seconds"""
        while self.running:
            try:
                await self.sync_queue_info()
                await asyncio.sleep(15)
            except Exception as e:
                logger.error(f"Error syncing queue info: {e}")
                await asyncio.sleep(30)
    
    async def sync_system_status_periodically(self):
        """Sync system status every 2 minutes"""
        while self.running:
            try:
                await self.sync_system_status()
                await asyncio.sleep(120)  # 2 minutes
            except Exception as e:
                logger.error(f"Error syncing system status: {e}")
                await asyncio.sleep(240)
    
    async def sync_jobs(self):
        """Sync jobs from IBM Quantum"""
        try:
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            jobs_data = await quantum_service.get_jobs(limit=100)
            await db_service.bulk_create_jobs(jobs_data)
            
            logger.info(f"Synced {len(jobs_data)} jobs")
            db.close()
        except Exception as e:
            logger.error(f"Error in sync_jobs: {e}")
    
    async def sync_backends(self):
        """Sync backends from IBM Quantum"""
        try:
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            backends_data = await quantum_service.get_all_backends()
            await db_service.bulk_upsert_backends(backends_data)
            
            logger.info(f"Synced {len(backends_data)} backends")
            db.close()
        except Exception as e:
            logger.error(f"Error in sync_backends: {e}")
    
    async def sync_queue_info(self):
        """Sync queue information"""
        try:
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            queue_data = await quantum_service.get_queue_info()
            await db_service.update_queue_info(queue_data)
            
            logger.info(f"Synced queue info for {len(queue_data)} backends")
            db.close()
        except Exception as e:
            logger.error(f"Error in sync_queue_info: {e}")
    
    async def sync_system_status(self):
        """Sync system status"""
        try:
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            status_data = await quantum_service.get_system_status()
            await db_service.update_system_status(status_data)
            
            logger.info(f"Synced status for {len(status_data)} services")
            db.close()
        except Exception as e:
            logger.error(f"Error in sync_system_status: {e}")

# Global instance
data_sync_service = DataSyncService()
