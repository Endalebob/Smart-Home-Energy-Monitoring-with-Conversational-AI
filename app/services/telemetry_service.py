from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import HTTPException, status
from app.models.telemetry import Telemetry, TelemetryCreate, TelemetryQuery
from app.models.device import Device
from app.models.user import User
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TelemetryService:
    
    @staticmethod
    def ingest_telemetry(db: Session, telemetry_data: TelemetryCreate) -> Telemetry:
        """Ingest telemetry data for a device"""
        # Find the device by device_id (UUID string)
        device = db.query(Device).filter(Device.device_id == telemetry_data.device_id).first()
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {telemetry_data.device_id} not found"
            )
        
        # Create telemetry record
        db_telemetry = Telemetry(
            device_id=device.id,  # Use the internal device ID
            timestamp=telemetry_data.timestamp,
            energy_watts=telemetry_data.energy_watts
        )
        
        try:
            db.add(db_telemetry)
            db.commit()
            db.refresh(db_telemetry)
            logger.info(f"Telemetry ingested for device {telemetry_data.device_id}: {telemetry_data.energy_watts}W")
            return db_telemetry
        except Exception as e:
            db.rollback()
            logger.error(f"Error ingesting telemetry: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving telemetry data"
            )
    
    @staticmethod
    def get_telemetry_by_device(
        db: Session, 
        device_id: str, 
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Telemetry]:
        """Get telemetry data for a specific device owned by the user"""
        # Find the device and verify ownership
        device = db.query(Device).filter(
            and_(
                Device.device_id == device_id,
                Device.user_id == user_id
            )
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found or access denied"
            )
        
        # Build query
        query = db.query(Telemetry).filter(Telemetry.device_id == device.id)
        
        if start_time:
            query = query.filter(Telemetry.timestamp >= start_time)
        if end_time:
            query = query.filter(Telemetry.timestamp <= end_time)
        
        # Order by timestamp and limit results
        telemetry_data = query.order_by(Telemetry.timestamp.desc()).limit(limit).all()
        
        return telemetry_data
    
    @staticmethod
    def get_user_devices_telemetry(
        db: Session,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get telemetry data for all devices owned by a user"""
        # Get all devices for the user
        devices = db.query(Device).filter(Device.user_id == user_id).all()
        
        if not devices:
            return []
        
        device_ids = [device.id for device in devices]
        
        # Build query for all user's devices
        query = db.query(Telemetry).filter(Telemetry.device_id.in_(device_ids))
        
        if start_time:
            query = query.filter(Telemetry.timestamp >= start_time)
        if end_time:
            query = query.filter(Telemetry.timestamp <= end_time)
        
        telemetry_data = query.order_by(Telemetry.timestamp.desc()).all()
        
        # Group by device
        result = []
        for device in devices:
            device_telemetry = [t for t in telemetry_data if t.device_id == device.id]
            result.append({
                "device_id": device.device_id,
                "device_name": device.name,
                "device_type": device.device_type,
                "telemetry_count": len(device_telemetry),
                "telemetry_data": device_telemetry
            })
        
        return result
    
    @staticmethod
    def get_energy_summary(
        db: Session,
        user_id: int,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get energy usage summary for devices"""
        # Build base query
        if device_id:
            # Specific device
            device = db.query(Device).filter(
                and_(
                    Device.device_id == device_id,
                    Device.user_id == user_id
                )
            ).first()
            
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Device not found or access denied"
                )
            
            query = db.query(Telemetry).filter(Telemetry.device_id == device.id)
        else:
            # All user devices
            devices = db.query(Device).filter(Device.user_id == user_id).all()
            if not devices:
                return {"total_energy": 0, "average_power": 0, "device_count": 0}
            
            device_ids = [device.id for device in devices]
            query = db.query(Telemetry).filter(Telemetry.device_id.in_(device_ids))
        
        # Apply time filters
        if start_time:
            query = query.filter(Telemetry.timestamp >= start_time)
        if end_time:
            query = query.filter(Telemetry.timestamp <= end_time)
        
        # Calculate aggregates
        result = query.with_entities(
            func.count(Telemetry.id).label('reading_count'),
            func.avg(Telemetry.energy_watts).label('average_power'),
            func.max(Telemetry.energy_watts).label('max_power'),
            func.min(Telemetry.energy_watts).label('min_power')
        ).first()
        
        return {
            "reading_count": result.reading_count or 0,
            "average_power_watts": float(result.average_power or 0),
            "max_power_watts": float(result.max_power or 0),
            "min_power_watts": float(result.min_power or 0),
            "device_id": device_id if device_id else "all_devices"
        }
    
    @staticmethod
    def get_top_consuming_devices(
        db: Session,
        user_id: int,
        limit: int = 5,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get top energy consuming devices for a user"""
        # Get user's devices with average power consumption
        query = db.query(
            Device.device_id,
            Device.name,
            Device.device_type,
            func.avg(Telemetry.energy_watts).label('average_power')
        ).join(Telemetry, Device.id == Telemetry.device_id).filter(Device.user_id == user_id)
        
        if start_time:
            query = query.filter(Telemetry.timestamp >= start_time)
        if end_time:
            query = query.filter(Telemetry.timestamp <= end_time)
        
        # Group by device and order by average power
        devices = query.group_by(Device.id).order_by(
            func.avg(Telemetry.energy_watts).desc()
        ).limit(limit).all()
        
        return [
            {
                "device_id": device.device_id,
                "name": device.name,
                "type": device.device_type,
                "average_power_watts": float(device.average_power or 0)
            }
            for device in devices
        ] 