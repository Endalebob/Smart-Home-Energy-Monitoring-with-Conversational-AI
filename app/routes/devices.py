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

    Register a new smart home device that will be associated with the authenticated user.
    The device will be automatically assigned a unique device_id if not provided.

    **HTTP Method:** POST  
    **Path:** /api/devices/

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Request Body (application/json):**
        - name (str, required): Device name (e.g., "Living Room TV", "Kitchen Fridge")
        - device_type (str, required): Type of device (e.g., "fridge", "ac", "tv", "washer", "dryer")
        - device_id (str, optional): Custom device UUID (will be auto-generated if not provided)

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/devices/"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Living Room Air Conditioner",
        "device_type": "ac",
        "device_id": "optional-custom-uuid"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/devices/" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \\
         -H "Content-Type: application/json" \\
         -d '{
           "name": "Living Room Air Conditioner",
           "device_type": "ac",
           "device_id": "optional-custom-uuid"
         }'
    ```

    **Response Example (201 Created):**
    ```json
    {
      "id": 1,
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Living Room Air Conditioner",
      "device_type": "ac",
      "user_id": 1,
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

    **Error Response Example (422 Validation Error):**
    ```json
    {
      "detail": [
        {
          "loc": ["body", "name"],
          "msg": "field required",
          "type": "value_error.missing"
        }
      ]
    }
    ```

    **Notes:**
    - Device is automatically associated with the authenticated user
    - Device is set as active by default
    - If device_id is not provided, a UUID will be auto-generated
    - Device types should be consistent (e.g., "ac", "tv", "fridge", "washer")
    """
    return DeviceService.create_device(db, device_data, current_user.id)

@router.get("/", response_model=List[DeviceResponse])
def get_my_devices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all devices owned by the current user

    Retrieve a list of all smart home devices associated with the authenticated user.
    Returns both active and inactive devices.

    **HTTP Method:** GET  
    **Path:** /api/devices/

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/devices/"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/devices/" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    [
      {
        "id": 1,
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Living Room Air Conditioner",
        "device_type": "ac",
        "user_id": 1,
        "is_active": true,
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": 2,
        "device_id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Kitchen Refrigerator",
        "device_type": "fridge",
        "user_id": 1,
        "is_active": true,
        "created_at": "2024-01-15T11:00:00Z"
      }
    ]
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Notes:**
    - Returns all devices owned by the authenticated user
    - Includes both active and inactive devices
    - Empty array is returned if user has no devices
    - Devices are sorted by creation date (newest first)
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

    Retrieve detailed information about a specific device owned by the authenticated user.
    Only returns devices that belong to the requesting user.

    **HTTP Method:** GET  
    **Path:** /api/devices/{device_id}

    **Path Parameters:**
        - device_id (str, required): UUID of the device to retrieve

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests

    device_id = "550e8400-e29b-41d4-a716-446655440000"
    url = f"http://localhost:8000/api/devices/{device_id}"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/devices/550e8400-e29b-41d4-a716-446655440000" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    {
      "id": 1,
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Living Room Air Conditioner",
      "device_type": "ac",
      "user_id": 1,
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

    **Error Response Example (404 Not Found):**
    ```json
    {
      "detail": "Device not found or access denied"
    }
    ```

    **Notes:**
    - Only returns devices owned by the authenticated user
    - Returns 404 if device doesn't exist or belongs to another user
    - Device ID must be a valid UUID format
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

    Modify the properties of an existing device owned by the authenticated user.
    Only the provided fields will be updated; omitted fields remain unchanged.

    **HTTP Method:** PUT  
    **Path:** /api/devices/{device_id}

    **Path Parameters:**
        - device_id (str, required): UUID of the device to update

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Request Body (application/json):**
        - name (str, optional): New device name
        - device_type (str, optional): New device type
        - is_active (bool, optional): New active status

    **Python Example (requests):**
    ```python
    import requests

    device_id = "550e8400-e29b-41d4-a716-446655440000"
    url = f"http://localhost:8000/api/devices/{device_id}"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Updated Living Room AC",
        "is_active": False
    }
    response = requests.put(url, json=payload, headers=headers)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X PUT "http://localhost:8000/api/devices/550e8400-e29b-41d4-a716-446655440000" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \\
         -H "Content-Type: application/json" \\
         -d '{
           "name": "Updated Living Room AC",
           "is_active": false
         }'
    ```

    **Response Example (200 OK):**
    ```json
    {
      "id": 1,
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Updated Living Room AC",
      "device_type": "ac",
      "user_id": 1,
      "is_active": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Error Response Example (404 Not Found):**
    ```json
    {
      "detail": "Device not found or access denied"
    }
    ```

    **Notes:**
    - Only updates the fields provided in the request body
    - Device must be owned by the authenticated user
    - Returns 404 if device doesn't exist or belongs to another user
    - Device ID cannot be changed after creation
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

    Permanently remove a device and all associated telemetry data.
    This action cannot be undone.

    **HTTP Method:** DELETE  
    **Path:** /api/devices/{device_id}

    **Path Parameters:**
        - device_id (str, required): UUID of the device to delete

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests

    device_id = "550e8400-e29b-41d4-a716-446655440000"
    url = f"http://localhost:8000/api/devices/{device_id}"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    response = requests.delete(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    ```

    **cURL Example:**
    ```bash
    curl -X DELETE "http://localhost:8000/api/devices/550e8400-e29b-41d4-a716-446655440000" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (204 No Content):**
    ```
    (Empty response body)
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Error Response Example (404 Not Found):**
    ```json
    {
      "detail": "Device not found or access denied"
    }
    ```

    **Notes:**
    - Device must be owned by the authenticated user
    - This action permanently deletes the device and all associated data
    - Returns 204 No Content on successful deletion
    - Returns 404 if device doesn't exist or belongs to another user
    """
    DeviceService.delete_device(db, device_id, current_user.id)
    return None 