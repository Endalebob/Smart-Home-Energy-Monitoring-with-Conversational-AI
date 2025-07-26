from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from contextlib import contextmanager
from dotenv import load_dotenv
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/smart_home")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Metadata for table creation
metadata = MetaData()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def init_users_table():
    """Initialize users table"""
    from app.models.user import User
    User.__table__.create(bind=engine, checkfirst=True)

def init_devices_table():
    """Initialize devices table"""
    from app.models.device import Device
    Device.__table__.create(bind=engine, checkfirst=True)

def init_telemetry_table():
    """Initialize telemetry table"""
    from app.models.telemetry import Telemetry
    Telemetry.__table__.create(bind=engine, checkfirst=True) 