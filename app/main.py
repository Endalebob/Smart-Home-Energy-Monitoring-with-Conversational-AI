from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from app.utils.db import init_users_table, init_devices_table, init_telemetry_table, get_db_context
from app.utils.seeder import seed_database
from app.routes import auth, telemetry, devices, chat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag to track if database has been initialized
_db_initialized = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _db_initialized
    
    # Startup
    print("Starting Smart Home Energy Monitoring API...")
    
    # Initialize database tables only once
    if not _db_initialized:
        try:
            logger.info("Initializing database tables...")
            init_users_table()
            init_devices_table()
            init_telemetry_table()
            logger.info("Database tables initialized successfully")
            
            # Seed database with initial data only once
            logger.info("Seeding database with initial data...")
            with get_db_context() as db:
                seed_database(db)
            logger.info("Database seeding completed successfully")
            
            _db_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    else:
        logger.info("Database already initialized, skipping initialization")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Home Energy Monitoring API...")

app = FastAPI(
    title="Smart Home Energy Monitoring API",
    description="API for monitoring home energy consumption with conversational AI",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router)
app.include_router(telemetry.router)
app.include_router(devices.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Smart Home Energy Monitoring API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


# allow CORS from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

