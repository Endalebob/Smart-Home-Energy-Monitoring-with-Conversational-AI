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

    Store energy consumption data for a specific device. This endpoint is typically
    used by IoT devices or data collection systems to report real-time energy usage.

    **HTTP Method:** POST  
    **Path:** /api/telemetry/ingest

    **Request Body (application/json):**
        - device_id (str, required): UUID of the device reporting data
        - timestamp (datetime, required): When the reading was taken (ISO 8601 format)
        - energy_watts (float, required): Energy consumption in watts

    **Python Example (requests):**
    ```python
    import requests
    from datetime import datetime

    url = "http://localhost:8000/api/telemetry/ingest"
    payload = {
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2024-01-15T10:30:00Z",
        "energy_watts": 1250.5
    }
    response = requests.post(url, json=payload)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/telemetry/ingest" \\
         -H "Content-Type: application/json" \\
         -d '{
           "device_id": "550e8400-e29b-41d4-a716-446655440000",
           "timestamp": "2024-01-15T10:30:00Z",
           "energy_watts": 1250.5
         }'
    ```

    **Response Example (201 Created):**
    ```json
    {
      "id": 1,
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2024-01-15T10:30:00Z",
      "energy_watts": 1250.5,
      "created_at": "2024-01-15T10:30:00Z"
    }
    ```

    **Error Response Example (422 Validation Error):**
    ```json
    {
      "detail": [
        {
          "loc": ["body", "energy_watts"],
          "msg": "field required",
          "type": "value_error.missing"
        }
      ]
    }
    ```

    **Notes:**
    - No authentication required for data ingestion (IoT devices)
    - Timestamp should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
    - Energy consumption should be a positive number in watts
    - Device must exist in the system before data can be ingested
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

    Retrieve historical energy consumption data for a specific device with optional
    time filtering and pagination. Only returns data for devices owned by the user.

    **HTTP Method:** GET  
    **Path:** /api/telemetry/device/{device_id}

    **Path Parameters:**
        - device_id (str, required): UUID of the device to retrieve data for

    **Query Parameters:**
        - start_time (datetime, optional): Start time filter (ISO 8601 format)
        - end_time (datetime, optional): End time filter (ISO 8601 format)
        - limit (int, optional): Maximum number of records to return (default: 100)

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests
    from datetime import datetime

    device_id = "550e8400-e29b-41d4-a716-446655440000"
    url = f"http://localhost:8000/api/telemetry/device/{device_id}"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    params = {
        "start_time": "2024-01-15T00:00:00Z",
        "end_time": "2024-01-15T23:59:59Z",
        "limit": 50
    }
    response = requests.get(url, headers=headers, params=params)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/telemetry/device/550e8400-e29b-41d4-a716-446655440000?start_time=2024-01-15T00:00:00Z&end_time=2024-01-15T23:59:59Z&limit=50" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    [
      {
        "id": 1,
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2024-01-15T10:30:00Z",
        "energy_watts": 1250.5,
        "created_at": "2024-01-15T10:30:00Z"
      },
      {
        "id": 2,
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2024-01-15T10:35:00Z",
        "energy_watts": 1280.2,
        "created_at": "2024-01-15T10:35:00Z"
      }
    ]
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
    - Only returns data for devices owned by the authenticated user
    - Data is sorted by timestamp (newest first)
    - Time filters use ISO 8601 format
    - Maximum limit is 1000 records per request
    - Returns empty array if no data found for the specified criteria
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

    Retrieve energy consumption data for all devices owned by the authenticated user
    with optional time filtering. Returns aggregated data per device.

    **HTTP Method:** GET  
    **Path:** /api/telemetry/my-devices

    **Query Parameters:**
        - start_time (datetime, optional): Start time filter (ISO 8601 format)
        - end_time (datetime, optional): End time filter (ISO 8601 format)

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests
    from datetime import datetime

    url = "http://localhost:8000/api/telemetry/my-devices"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    params = {
        "start_time": "2024-01-15T00:00:00Z",
        "end_time": "2024-01-15T23:59:59Z"
    }
    response = requests.get(url, headers=headers, params=params)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/telemetry/my-devices?start_time=2024-01-15T00:00:00Z&end_time=2024-01-15T23:59:59Z" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    {
      "devices": [
        {
          "device_id": "550e8400-e29b-41d4-a716-446655440000",
          "device_name": "Living Room AC",
          "device_type": "ac",
          "total_energy_kwh": 12.5,
          "average_watts": 1250.5,
          "peak_watts": 1800.0,
          "data_points": 288
        },
        {
          "device_id": "550e8400-e29b-41d4-a716-446655440001",
          "device_name": "Kitchen Fridge",
          "device_type": "fridge",
          "total_energy_kwh": 8.2,
          "average_watts": 820.0,
          "peak_watts": 1200.0,
          "data_points": 288
        }
      ],
      "summary": {
        "total_devices": 2,
        "total_energy_kwh": 20.7,
        "period": {
          "start": "2024-01-15T00:00:00Z",
          "end": "2024-01-15T23:59:59Z"
        }
      }
    }
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Notes:**
    - Returns aggregated data for all user's devices
    - Energy consumption is converted to kWh for easier understanding
    - Includes device metadata (name, type) for context
    - Returns summary statistics for the entire period
    - Empty response if user has no devices or no data in time range
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

    Retrieve comprehensive energy usage statistics including total consumption,
    averages, peaks, and trends. Can be filtered by specific device or time period.

    **HTTP Method:** GET  
    **Path:** /api/telemetry/summary

    **Query Parameters:**
        - device_id (str, optional): Specific device UUID to filter by
        - start_time (datetime, optional): Start time filter (ISO 8601 format)
        - end_time (datetime, optional): End time filter (ISO 8601 format)

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests
    from datetime import datetime

    url = "http://localhost:8000/api/telemetry/summary"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    params = {
        "device_id": "550e8400-e29b-41d4-a716-446655440000",
        "start_time": "2024-01-01T00:00:00Z",
        "end_time": "2024-01-31T23:59:59Z"
    }
    response = requests.get(url, headers=headers, params=params)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/telemetry/summary?device_id=550e8400-e29b-41d4-a716-446655440000&start_time=2024-01-01T00:00:00Z&end_time=2024-01-31T23:59:59Z" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    {
      "period": {
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-31T23:59:59Z",
        "duration_days": 31
      },
      "consumption": {
        "total_kwh": 450.5,
        "average_daily_kwh": 14.5,
        "peak_hourly_kwh": 2.8,
        "lowest_hourly_kwh": 0.2
      },
      "cost_estimate": {
        "total_cost": 67.58,
        "currency": "USD",
        "rate_per_kwh": 0.15
      },
      "trends": {
        "daily_average": [14.2, 14.8, 15.1, 14.5, 14.9, 15.2, 14.7],
        "peak_hours": ["18:00", "19:00", "20:00"],
        "lowest_hours": ["03:00", "04:00", "05:00"]
      },
      "device_breakdown": [
        {
          "device_id": "550e8400-e29b-41d4-a716-446655440000",
          "device_name": "Living Room AC",
          "percentage": 45.2,
          "kwh": 203.6
        }
      ]
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
    - If device_id is not provided, returns summary for all user's devices
    - Cost estimates are based on default rate (configurable)
    - Trends include daily averages for the last 7 days
    - Peak/lowest hours are based on 24-hour cycle
    - Device breakdown shows percentage contribution to total consumption
    """
    return TelemetryService.get_energy_summary(
        db, current_user.id, device_id, start_time, end_time
    )

@router.get("/top-consuming")
def get_top_consuming_devices(
    limit: int = Query(3, description="Number of top devices to return"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get top energy consuming devices for the current user

    Retrieve a ranked list of the most energy-intensive devices owned by the user,
    sorted by total energy consumption in descending order.

    **HTTP Method:** GET  
    **Path:** /api/telemetry/top-consuming

    **Query Parameters:**
        - limit (int, optional): Number of top devices to return (default: 3, max: 10)
        - start_time (datetime, optional): Start time filter (ISO 8601 format)
        - end_time (datetime, optional): End time filter (ISO 8601 format)

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Python Example (requests):**
    ```python
    import requests
    from datetime import datetime

    url = "http://localhost:8000/api/telemetry/top-consuming"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    params = {
        "limit": 5,
        "start_time": "2024-01-01T00:00:00Z",
        "end_time": "2024-01-31T23:59:59Z"
    }
    response = requests.get(url, headers=headers, params=params)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/telemetry/top-consuming?limit=5&start_time=2024-01-01T00:00:00Z&end_time=2024-01-31T23:59:59Z" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    ```

    **Response Example (200 OK):**
    ```json
    {
      "period": {
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-31T23:59:59Z"
      },
      "devices": [
        {
          "rank": 1,
          "device_id": "550e8400-e29b-41d4-a716-446655440000",
          "device_name": "Living Room Air Conditioner",
          "device_type": "ac",
          "total_kwh": 203.6,
          "average_watts": 1250.5,
          "peak_watts": 1800.0,
          "percentage_of_total": 45.2,
          "cost_estimate": 30.54
        },
        {
          "rank": 2,
          "device_id": "550e8400-e29b-41d4-a716-446655440001",
          "device_name": "Kitchen Refrigerator",
          "device_type": "fridge",
          "total_kwh": 98.4,
          "average_watts": 820.0,
          "peak_watts": 1200.0,
          "percentage_of_total": 21.8,
          "cost_estimate": 14.76
        },
        {
          "rank": 3,
          "device_id": "550e8400-e29b-41d4-a716-446655440002",
          "device_name": "Living Room TV",
          "device_type": "tv",
          "total_kwh": 45.2,
          "average_watts": 150.0,
          "peak_watts": 200.0,
          "percentage_of_total": 10.0,
          "cost_estimate": 6.78
        }
      ],
      "summary": {
        "total_devices_analyzed": 8,
        "total_energy_kwh": 450.5,
        "top_devices_energy_kwh": 347.2,
        "top_devices_percentage": 77.1
      }
    }
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Notes:**
    - Devices are ranked by total energy consumption (kWh)
    - Percentage shows contribution to total household consumption
    - Cost estimates use default electricity rate
    - Returns empty array if user has no devices or no data
    - Maximum limit is 10 devices for performance reasons
    """
    return TelemetryService.get_top_consuming_devices(
        db, current_user.id, limit, start_time, end_time
    )

@router.get("/health")
def telemetry_health_check():
    """
    Health check for telemetry service

    Simple endpoint to verify that the telemetry service is operational.
    No authentication required.

    **HTTP Method:** GET  
    **Path:** /api/telemetry/health

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/telemetry/health"
    response = requests.get(url)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/telemetry/health"
    ```

    **Response Example (200 OK):**
    ```json
    {
      "status": "healthy",
      "service": "telemetry",
      "timestamp": "2024-01-15T10:30:00Z"
    }
    ```

    **Notes:**
    - No authentication required
    - Used for monitoring and health checks
    - Returns basic service status information
    - Useful for load balancers and monitoring systems
    """
    return {"status": "healthy", "service": "telemetry"} 