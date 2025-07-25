from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.device import Device, DeviceCreate, DeviceUpdate, DeviceResponse
from app.models.user import User
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class DeviceService:
    
    @staticmethod
    def create_device(db: Session, device_data: DeviceCreate, user_id: int) -> DeviceResponse:
        """Create a new device for a user"""
        # Generate a unique device ID (UUID)
        device_uuid = str(uuid.uuid4())
        
        # Create device
        db_device = Device(
            device_id=device_uuid,
            name=device_data.name,
            device_type=device_data.device_type,
            user_id=user_id
        )
        
        try:
            db.add(db_device)
            db.commit()
            db.refresh(db_device)
            logger.info(f"Device created: {device_data.name} for user {user_id}")
            return DeviceResponse.from_orm(db_device)
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating device: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating device"
            )
    
    @staticmethod
    def get_user_devices(db: Session, user_id: int) -> List[DeviceResponse]:
        """Get all devices for a user"""
        devices = db.query(Device).filter(Device.user_id == user_id).all()
        return [DeviceResponse.from_orm(device) for device in devices]
    
    @staticmethod
    def get_device_by_id(db: Session, device_id: str, user_id: int) -> Optional[DeviceResponse]:
        """Get a specific device by ID for a user"""
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user_id
        ).first()
        
        if not device:
            return None
        
        return DeviceResponse.from_orm(device)
    
    @staticmethod
    def update_device(
        db: Session, 
        device_id: str, 
        device_data: DeviceUpdate, 
        user_id: int
    ) -> DeviceResponse:
        """Update a device"""
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user_id
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found or access denied"
            )
        
        # Update fields
        if device_data.name is not None:
            device.name = device_data.name
        if device_data.device_type is not None:
            device.device_type = device_data.device_type
        if device_data.is_active is not None:
            device.is_active = device_data.is_active
        
        try:
            db.commit()
            db.refresh(device)
            logger.info(f"Device updated: {device_id}")
            return DeviceResponse.from_orm(device)
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating device: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating device"
            )
    
    @staticmethod
    def delete_device(db: Session, device_id: str, user_id: int) -> bool:
        """Delete a device"""
        device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user_id
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found or access denied"
            )
        
        try:
            db.delete(device)
            db.commit()
            logger.info(f"Device deleted: {device_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting device: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting device"
            )
        