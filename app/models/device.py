from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from app.utils.db import Base
from datetime import datetime
from typing import Optional

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)  # UUID for device
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)  # fridge, ac, tv, etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="devices")
    telemetry_data = relationship("Telemetry", back_populates="device")

# Pydantic models for API
class DeviceBase(BaseModel):
    device_id: str
    name: str
    device_type: str

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[str] = None
    is_active: Optional[bool] = None

class DeviceResponse(DeviceBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            device_id=obj.device_id,
            name=obj.name,
            device_type=obj.device_type,
            user_id=obj.user_id,
            is_active=obj.is_active,
            created_at=obj.created_at
        ) 