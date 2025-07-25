from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.utils.jwt import get_current_active_user
from app.services.auth_service import AuthService
from app.models.user import UserCreate, UserLogin, UserResponse, User
from typing import Dict

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User's email address (must be unique)
    - **username**: User's username (must be unique)
    - **password**: User's password (will be hashed)
    """
    return AuthService.register_user(db, user_data)

@router.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and get access token
    
    - **email**: User's email address
    - **password**: User's password
    """
    return AuthService.login_user(db, user_credentials.email, user_credentials.password)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout user (client-side token invalidation)
    
    Note: This endpoint logs the logout action. The actual token invalidation
    should be handled on the client side by removing the token from storage.
    """

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    
    Returns the profile information of the currently authenticated user.
    """
    return UserResponse.from_orm(current_user)
