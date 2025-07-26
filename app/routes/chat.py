from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from pydantic import BaseModel
import logging
from app.utils.db import get_db
from app.utils.jwt import get_current_active_user
from app.services.chat_service import ChatService
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Conversational AI"])

# Initialize chat service
chat_service = ChatService()

# Request/Response models
class ChatQuery(BaseModel):
    query: str
    chat_id: Optional[str] = None

class ChatResponse(BaseModel):
    chat_id: str
    answer: str
    data: Optional[Dict[str, Any]] = None

@router.post("/query", response_model=ChatResponse)
def process_chat_query(
    chat_request: ChatQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process a natural language query about energy usage

    Send a natural language question about your energy consumption and receive
    an intelligent response with relevant data. The AI can understand various
    types of energy-related queries and provide contextual answers.

    **HTTP Method:** POST  
    **Path:** /api/chat/query

    **Headers:**
        - Authorization (str, required): Bearer token for authentication

    **Request Body (application/json):**
        - query (str, required): Natural language question about energy usage
        - chat_id (str, optional): Chat session ID for conversation continuity

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/chat/query"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "Content-Type": "application/json"
    }
    payload = {
        "query": "How much energy did my fridge use yesterday?",
        "chat_id": "optional-session-id"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/chat/query" \\
         -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \\
         -H "Content-Type: application/json" \\
         -d '{
           "query": "How much energy did my fridge use yesterday?",
           "chat_id": "optional-session-id"
         }'
    ```

    **Response Example (200 OK):**
    ```json
    {
      "chat_id": "session-12345",
      "answer": "Your refrigerator used 8.2 kWh of energy yesterday. This is about 15% of your total daily consumption. The average power consumption was 820 watts, with peak usage reaching 1200 watts during defrost cycles.",
      "data": {
        "device_name": "Kitchen Refrigerator",
        "energy_kwh": 8.2,
        "average_watts": 820.0,
        "peak_watts": 1200.0,
        "percentage_of_total": 15.2,
        "period": "yesterday"
      }
    }
    ```

    **Error Response Example (401 Unauthorized):**
    ```json
    {
      "detail": "Not authenticated"
    }
    ```

    **Error Response Example (500 Internal Server Error):**
    ```json
    {
      "detail": "Error processing your question. Please try again."
    }
    ```

    **Example Queries:**
    - "How much energy did my fridge use yesterday?"
    - "Which of my devices are using the most power?"
    - "Show me my energy summary for today"
    - "List my devices"
    - "Compare energy usage between my devices"
    - "What's the power consumption of my AC today?"
    - "How much energy did I use last month?"

    **Notes:**
    - Uses GPT-4o model for natural language understanding
    - Supports conversation continuity with chat_id
    - Returns structured data alongside natural language response
    - Can access real-time energy data from your devices
    - Understands various time periods (today, yesterday, last week, etc.)
    """
    try:
        result = chat_service.process_query(
            query=chat_request.query,
            user_id=current_user.id,
            db=db,
            chat_id=chat_request.chat_id
        )
        
        return ChatResponse(
            chat_id=result["chat_id"],
            answer=result["answer"],
            data=result.get("data")
        )
        
    except Exception as e:
        logger.error(f"Error processing chat query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing your question. Please try again."
        )

@router.get("/examples")
def get_chat_examples():
    """
    Get example queries that users can ask

    Retrieve a comprehensive list of example questions organized by category
    to help users understand what they can ask the conversational AI.

    **HTTP Method:** GET  
    **Path:** /api/chat/examples

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/chat/examples"
    response = requests.get(url)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/chat/examples"
    ```

    **Response Example (200 OK):**
    ```json
    {
      "message": "Here are some example questions you can ask:",
      "examples": {
        "energy_usage": [
          "How much energy did my fridge use yesterday?",
          "What's the power consumption of my AC today?",
          "Show me the energy usage for my TV",
          "How much power is my washing machine using?"
        ],
        "comparisons": [
          "Which of my devices are using the most power?",
          "Compare energy usage between my devices",
          "What are my top 3 energy consuming devices?",
          "Show me the most efficient devices"
        ],
        "summaries": [
          "Show me my energy summary for today",
          "What's my total energy usage this week?",
          "Give me an energy report for yesterday",
          "How much energy did I use last month?"
        ],
        "devices": [
          "List my devices",
          "Show me all my registered devices",
          "What devices do I have?",
          "Which devices are active?"
        ],
        "general": [
          "Hello",
          "What can you help me with?",
          "How can I save energy?",
          "Thank you"
        ]
      }
    }
    ```

    **Notes:**
    - No authentication required
    - Provides categorized examples for different use cases
    - Helps users understand the AI's capabilities
    - Examples cover energy usage, comparisons, summaries, and device management
    """
    examples = {
        "energy_usage": [
            "How much energy did my fridge use yesterday?",
            "What's the power consumption of my AC today?",
            "Show me the energy usage for my TV",
            "How much power is my washing machine using?"
        ],
        "comparisons": [
            "Which of my devices are using the most power?",
            "Compare energy usage between my devices",
            "What are my top 3 energy consuming devices?",
            "Show me the most efficient devices"
        ],
        "summaries": [
            "Show me my energy summary for today",
            "What's my total energy usage this week?",
            "Give me an energy report for yesterday",
            "How much energy did I use last month?"
        ],
        "devices": [
            "List my devices",
            "Show me all my registered devices",
            "What devices do I have?",
            "Which devices are active?"
        ],
        "general": [
            "Hello",
            "What can you help me with?",
            "How can I save energy?",
            "Thank you"
        ]
    }
    
    return {
        "message": "Here are some example questions you can ask:",
        "examples": examples
    }

@router.get("/capabilities")
def get_chat_capabilities():
    """
    Get information about what the chat assistant can do

    Retrieve detailed information about the conversational AI's capabilities,
    including supported intents, time periods, and features.

    **HTTP Method:** GET  
    **Path:** /api/chat/capabilities

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/chat/capabilities"
    response = requests.get(url)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/chat/capabilities"
    ```

    **Response Example (200 OK):**
    ```json
    {
      "intents": [
        {
          "name": "Energy Usage",
          "description": "Get energy consumption data for specific devices",
          "examples": ["How much energy did my fridge use?", "What's my AC power usage?"]
        },
        {
          "name": "Device Comparison", 
          "description": "Compare energy usage between devices",
          "examples": ["Which devices use the most power?", "Compare my devices"]
        },
        {
          "name": "Top Consumers",
          "description": "Find highest energy consuming devices",
          "examples": ["What are my top energy consumers?", "Show me the most power-hungry devices"]
        },
        {
          "name": "Energy Summary",
          "description": "Get overall energy usage summaries",
          "examples": ["Show me my energy summary", "What's my total usage today?"]
        },
        {
          "name": "Device Management",
          "description": "List and manage devices",
          "examples": ["List my devices", "Show me my registered devices"]
        }
      ],
      "time_periods": [
        "today", "yesterday", "last_week", "last_month"
      ],
      "features": [
        "Natural language processing",
        "Intent classification",
        "Parameter extraction",
        "Structured data responses",
        "Real-time energy data access"
      ]
    }
    ```

    **Notes:**
    - No authentication required
    - Provides comprehensive overview of AI capabilities
    - Lists supported intents and their descriptions
    - Shows supported time periods for queries
    - Details technical features and capabilities
    """
    capabilities = {
        "intents": [
            {
                "name": "Energy Usage",
                "description": "Get energy consumption data for specific devices",
                "examples": ["How much energy did my fridge use?", "What's my AC power usage?"]
            },
            {
                "name": "Device Comparison", 
                "description": "Compare energy usage between devices",
                "examples": ["Which devices use the most power?", "Compare my devices"]
            },
            {
                "name": "Top Consumers",
                "description": "Find highest energy consuming devices",
                "examples": ["What are my top energy consumers?", "Show me the most power-hungry devices"]
            },
            {
                "name": "Energy Summary",
                "description": "Get overall energy usage summaries",
                "examples": ["Show me my energy summary", "What's my total usage today?"]
            },
            {
                "name": "Device Management",
                "description": "List and manage devices",
                "examples": ["List my devices", "Show me my registered devices"]
            }
        ],
        "time_periods": [
            "today", "yesterday", "last_week", "last_month"
        ],
        "features": [
            "Natural language processing",
            "Intent classification",
            "Parameter extraction",
            "Structured data responses",
            "Real-time energy data access"
        ]
    }
    
    return capabilities

@router.get("/health")
def chat_health_check():
    """
    Health check for chat service

    Verify that the conversational AI service is operational and ready
    to process natural language queries about energy usage.

    **HTTP Method:** GET  
    **Path:** /api/chat/health

    **Python Example (requests):**
    ```python
    import requests

    url = "http://localhost:8000/api/chat/health"
    response = requests.get(url)
    print(response.json())
    ```

    **cURL Example:**
    ```bash
    curl -X GET "http://localhost:8000/api/chat/health"
    ```

    **Response Example (200 OK):**
    ```json
    {
      "status": "healthy", 
      "service": "conversational_ai",
      "model": "gpt-4o",
      "capabilities": "energy_monitoring_queries"
    }
    ```

    **Notes:**
    - No authentication required
    - Used for monitoring and health checks
    - Returns service status and model information
    - Useful for load balancers and monitoring systems
    - Indicates AI model being used (GPT-4o)
    """
    return {
        "status": "healthy", 
        "service": "conversational_ai",
        "model": "gpt-4o",
        "capabilities": "energy_monitoring_queries"
    } 