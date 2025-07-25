from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.utils.db import get_db
from app.utils.jwt import get_current_active_user
from app.services.device_service import DeviceService
from app.models.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.models.user import User

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    device_data: DeviceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new device for the current user
    
    - **name**: Device name
    - **device_type**: Type of device (e.g., fridge, ac, tv, etc.)
    """
    return DeviceService.create_device(db, device_data, current_user.id)

@router.get("/", response_model=List[DeviceResponse])
def get_my_devices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all devices owned by the current user
    """
    return DeviceService.get_user_devices(db, current_user.id)

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific device by ID
    
    - **device_id**: UUID of the device
    """
    device = DeviceService.get_device_by_id(db, device_id, current_user.id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or access denied"
        )
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a device
    
    - **device_id**: UUID of the device
    - **name**: Optional new device name
    - **device_type**: Optional new device type
    - **is_active**: Optional active status
    """
    return DeviceService.update_device(db, device_id, device_data, current_user.id)

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a device
    
    - **device_id**: UUID of the device
    """
    DeviceService.delete_device(db, device_id, current_user.id)
    return None 