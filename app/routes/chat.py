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
    
    Examples:
    - "How much energy did my fridge use yesterday?"
    - "Which of my devices are using the most power?"
    - "Show me my energy summary for today"
    - "List my devices"
    - "Compare energy usage between my devices"
    
    - **query**: Natural language question about energy usage
    - **chat_id**: Optional chat session ID for conversation continuity
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
    """Health check for chat service"""
    return {
        "status": "healthy", 
        "service": "conversational_ai",
        "model": "gpt-4o",
        "capabilities": "energy_monitoring_queries"
    } 