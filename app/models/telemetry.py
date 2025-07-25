from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from app.utils.db import Base
from datetime import datetime
from typing import Optional

class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    energy_watts = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    device = relationship("Device", back_populates="telemetry_data")
    
    # Composite index for efficient time-series queries
    __table_args__ = (
        Index('idx_device_timestamp', 'device_id', 'timestamp'),
    )

# Pydantic models for API
class TelemetryBase(BaseModel):
    device_id: str  # UUID string
    timestamp: datetime
    energy_watts: float

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryResponse(BaseModel):
    id: int
    device_id: str  # UUID string
    timestamp: datetime
    energy_watts: float
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        # Get the device UUID from the relationship
        device_uuid = obj.device.device_id if obj.device else "unknown"
        return cls(
            id=obj.id,
            device_id=device_uuid,
            timestamp=obj.timestamp,
            energy_watts=obj.energy_watts,
            created_at=obj.created_at
        )

class TelemetryQuery(BaseModel):
    device_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = 100 