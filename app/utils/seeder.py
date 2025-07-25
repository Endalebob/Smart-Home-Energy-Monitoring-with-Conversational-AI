from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.hashing import get_password_hash
import logging

logger = logging.getLogger(__name__)

def create_admin_user(db: Session, username: str = "admin", password: str = "admin123", email: str = "admin@smart-home.com") -> User:
    """Create admin user if it doesn't exist"""
    # Check if admin user already exists
    existing_admin = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_admin:
        logger.info(f"Admin user already exists: {existing_admin.username}")
        return existing_admin
    
    # Create admin user
    hashed_password = get_password_hash(password)
    admin_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=True
    )
    
    try:
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"Admin user created successfully: {username}")
        return admin_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating admin user: {e}")
        raise

def seed_database(db: Session):
    """Seed the database with initial data"""
    logger.info("Starting database seeding...")
    
    # Create admin user
    admin_user = create_admin_user(db)
    
    logger.info("Database seeding completed successfully")
    return {
        "admin_user": admin_user
    } 