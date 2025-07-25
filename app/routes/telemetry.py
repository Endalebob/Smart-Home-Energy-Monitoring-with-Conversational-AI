from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.utils.db import get_db
from app.utils.jwt import get_current_active_user
from app.services.telemetry_service import TelemetryService
from app.models.telemetry import TelemetryCreate, TelemetryResponse, TelemetryQuery
from app.models.user import User

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

@router.post("/ingest", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
def ingest_telemetry(
    telemetry_data: TelemetryCreate,
    db: Session = Depends(get_db)
):
    """
    Ingest telemetry data for a device
    
    - **device_id**: UUID of the device
    - **timestamp**: When the reading was taken
    - **energy_watts**: Energy consumption in watts
    """
    telemetry = TelemetryService.ingest_telemetry(db, telemetry_data)
    return TelemetryResponse.from_orm(telemetry)

@router.get("/device/{device_id}", response_model=List[TelemetryResponse])
def get_device_telemetry(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    limit: int = Query(100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get telemetry data for a specific device owned by the current user
    
    - **device_id**: UUID of the device
    - **start_time**: Optional start time filter
    - **end_time**: Optional end time filter
    - **limit**: Maximum number of records to return
    """
    telemetry_data = TelemetryService.get_telemetry_by_device(
        db, device_id, current_user.id, start_time, end_time, limit
    )
    return [TelemetryResponse.from_orm(t) for t in telemetry_data]

@router.get("/my-devices")
def get_my_devices_telemetry(
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get telemetry data for all devices owned by the current user
    
    - **start_time**: Optional start time filter
    - **end_time**: Optional end time filter
    """
    return TelemetryService.get_user_devices_telemetry(
        db, current_user.id, start_time, end_time
    )

@router.get("/summary")
def get_energy_summary(
    device_id: Optional[str] = Query(None, description="Specific device ID (optional)"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get energy usage summary for devices
    
    - **device_id**: Optional specific device ID
    - **start_time**: Optional start time filter
    - **end_time**: Optional end time filter
    """
    return TelemetryService.get_energy_summary(
        db, current_user.id, device_id, start_time, end_time
    )

@router.get("/top-consuming")
def get_top_consuming_devices(
    limit: int = Query(5, description="Number of top devices to return"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get top energy consuming devices for the current user
    
    - **limit**: Number of top devices to return
    - **start_time**: Optional start time filter
    - **end_time**: Optional end time filter
    """
    return TelemetryService.get_top_consuming_devices(
        db, current_user.id, limit, start_time, end_time
    )

@router.get("/health")
def telemetry_health_check():
    """Health check for telemetry service"""
    return {"status": "healthy", "service": "telemetry"} 