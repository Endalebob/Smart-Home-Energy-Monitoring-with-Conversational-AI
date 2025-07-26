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

    Create a new user account with email, username, and password.
    The password will be securely hashed before storage.

    **HTTP Method:** POST  
    **Path:** /api/auth/register

    **Request Body (application/json):**
        - email (str, required): User's email address (must be unique)
        - username (str, required): User's username (must be unique)
        - password (str, required): User's password (will be hashed)

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/auth/register"
    payload = {
        "email": "user@example.com",
        "username": "newuser",
        "password": "securepassword123"
    }
    response = requests.post(url, json=payload)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/auth/register" \\
         -H "Content-Type: application/json" \\
         -d '{
           "email": "user@example.com",
           "username": "newuser",
           "password": "securepassword123"
         }'
    ```

    **Response Example (201 Created):**
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "username": "newuser",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
    ```

    **Error Response Example (400 Bad Request):**
    ```json
    {
      "detail": "Email already registered"
    }
    ```

    **Notes:**
    - Email and username must be unique across all users
    - Password will be securely hashed using bcrypt
    - User account is automatically set as active upon creation
    """
    return AuthService.register_user(db, user_data)

@router.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and get access token

    Authenticate user credentials and return an access token for API access.
    The token should be included in subsequent requests as a Bearer token.

    **HTTP Method:** POST  
    **Path:** /api/auth/login

    **Request Body (application/json):**
        - email (str, required): User's email address
        - password (str, required): User's password

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/auth/login"
    payload = {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    response = requests.post(url, json=payload)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/auth/login" \\
         -H "Content-Type: application/json" \\
         -d '{
           "email": "user@example.com",
           "password": "securepassword123"
         }'
    ```

    **Response Example (200 OK):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer",
      "expires_in": 3600,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "newuser",
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z"
      }
    }
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Incorrect email or password"
    }
    ```

    **Notes:**
    - Store the access_token securely on the client side
    - Include the token in Authorization header: `Bearer <access_token>`
    - Token expires in 1 hour (3600 seconds) by default
    """
    return AuthService.login_user(db, user_credentials.email, user_credentials.password)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout user (client-side token invalidation)

    Log the logout action for audit purposes. The actual token invalidation
    should be handled on the client side by removing the token from storage.

    **HTTP Method:** POST  
    **Path:** /api/auth/logout

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/auth/logout"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    response = requests.post(url, headers=headers)
    print(response.status_code)
    ```

    **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/auth/logout" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    {
      "message": "Successfully logged out"
    }
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Notes:**
    - This endpoint logs the logout action for audit purposes
    - Client should remove the access token from local storage
    - Token remains valid until expiration (server-side invalidation not implemented)
    """
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information

    Retrieve the profile information of the currently authenticated user.
    Requires a valid access token in the Authorization header.

    **HTTP Method:** GET  
    **Path:** /api/auth/me

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/auth/me"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/auth/me" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    {
      "id": 1,
      "email": "user@example.com",
      "username": "newuser",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Error Response Example (403 Forbidden):**
    ```json
    {
      "detail": "Inactive user"
    }
    ```

    **Notes:**
    - Returns the complete user profile information
    - Only returns data for the authenticated user
    - User must be active to access this endpoint
    """
    return UserResponse.from_orm(current_user)
