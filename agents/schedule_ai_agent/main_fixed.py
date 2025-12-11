"""
Fixed FastAPI server for ScheduleAI - Italian Appointment Scheduling Agent.

This version fixes all communication issues with the frontend.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global agent instance
schedule_agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global schedule_agent

    logger.info("🚀 Starting ScheduleAI server...")

    # Try to initialize agent
    try:
        from agent import ScheduleAIAgent
        from dependencies import create_dependencies
        from settings import load_settings

        # Load settings
        try:
            settings = load_settings()
            logger.info(f"✅ Settings loaded: {settings.app_env}")
        except Exception as e:
            logger.warning(f"⚠️ Could not load settings: {e}")
            settings = None

        # Create dependencies
        try:
            dependencies = create_dependencies()
            logger.info("✅ Dependencies created")
        except Exception as e:
            logger.warning(f"⚠️ Could not create dependencies: {e}")
            dependencies = None

        # Initialize agent
        try:
            schedule_agent = ScheduleAIAgent(dependencies)
            logger.info("✅ ScheduleAI agent initialized")

            # Test agent
            test_response = await schedule_agent.process_message(
                "Ciao, test di inizializzazione",
                session_id="test-session"
            )
            logger.info(f"✅ Agent test successful")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            schedule_agent = None

    except ImportError as e:
        logger.warning(f"⚠️ Could not import agent components: {e}")
        schedule_agent = None

    yield

    logger.info("🛑 Shutting down ScheduleAI server...")

# Initialize FastAPI app
app = FastAPI(
    title="ScheduleAI API",
    description="Italian Appointment Scheduling AI Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS properly for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str = Field(..., description="User message to process")
    session_id: str = Field(default="default", description="Session identifier")
    business_id: Optional[str] = Field(None, description="Business identifier")
    consultant_id: Optional[str] = Field(None, description="Consultant identifier")
    stream: bool = Field(default=False, description="Whether to stream response")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI agent response")
    session_id: str = Field(..., description="Session identifier")
    timestamp: str = Field(..., description="Response timestamp")
    agent_ready: bool = Field(True, description="Whether the AI agent is available")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    agent_ready: bool = Field(..., description="Whether AI agent is ready")
    timestamp: str = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")

def get_mock_response(message: str) -> str:
    """Generate mock response for testing when agent is not available."""
    message_lower = message.lower()

    if 'ciao' in message_lower or 'buongiorno' in message_lower:
        return "Buongiorno! Sono ScheduleAI, il tuo assistente per le prenotazioni. Come posso aiutarti oggi?"
    elif 'appuntamento' in message_lower or 'prenotare' in message_lower:
        return "Certamente! Posso aiutarti a prenotare un appuntamento. Che tipo di servizio desideri e quando preferiresti?"
    elif 'disponibile' in message_lower or 'quando' in message_lower:
        return "Posso controllare le disponibilità per te. Che giorno ti interessa e di che tipo di servizio hai bisogno?"
    elif 'grazie' in message_lower:
        return "Prego! Sono qui per aiutarti con qualsiasi altra domanda o prenotazione."
    else:
        return "Sono ScheduleAI, il tuo assistente per prenotazioni. Posso aiutarti a prenotare appuntamenti, controllare disponibilità e gestire la tua agenda. Come posso assisterti?"

# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return HealthResponse(
        status="healthy",
        agent_ready=schedule_agent is not None,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return HealthResponse(
        status="healthy",
        agent_ready=schedule_agent is not None,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/chat")
async def chat_endpoint(message_data: ChatMessage):
    """
    Main chat endpoint for interacting with ScheduleAI.

    Fixed version that handles all edge cases properly.
    """
    logger.info(f"💬 Received message: {message_data.message[:50]}...")
    logger.info(f"🔑 Session ID: {message_data.session_id}")
    logger.info(f"🤖 Agent ready: {schedule_agent is not None}")

    try:
        if not schedule_agent:
            # Provide mock response when agent is not available
            logger.warning("⚠️ Agent not available, using mock response")
            mock_response = get_mock_response(message_data.message)

            return JSONResponse(
                status_code=200,
                content={
                    "response": mock_response,
                    "session_id": message_data.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "agent_ready": False
                }
            )

        # Process message with real agent
        try:
            response = await schedule_agent.process_message(
                message_data.message,
                session_id=message_data.session_id,
                business_id=message_data.business_id,
                consultant_id=message_data.consultant_id
            )

            logger.info(f"✅ Agent response: {str(response)[:50]}...")

            # Handle different response formats from Pydantic AI
            if hasattr(response, 'output'):
                # New Pydantic AI format
                response_text = response.output
            elif hasattr(response, 'data'):
                # Alternative format
                response_text = response.data
            elif isinstance(response, str):
                # String response
                response_text = response
            else:
                # Fallback
                response_text = str(response)

            return JSONResponse(
                status_code=200,
                content={
                    "response": response_text,
                    "session_id": message_data.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "agent_ready": True
                }
            )

        except Exception as agent_error:
            logger.error(f"❌ Agent processing error: {agent_error}")

            # Fallback to mock response on agent error
            mock_response = get_mock_response(message_data.message)
            return JSONResponse(
                status_code=200,
                content={
                    "response": mock_response,
                    "session_id": message_data.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "agent_ready": False,
                    "error": str(agent_error)
                }
            )

    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")

        return JSONResponse(
            status_code=500,
            content={
                "response": f"Mi dispiace, si è verificato un errore: {str(e)}",
                "session_id": message_data.session_id,
                "timestamp": datetime.now().isoformat(),
                "agent_ready": False,
                "error": str(e)
            }
        )

@app.get("/test")
async def test_endpoint():
    """Test endpoint for debugging."""
    logger.info("🧪 Test endpoint called")
    return {
        "message": "ScheduleAI test endpoint working",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": schedule_agent is not None,
        "backend_status": "healthy"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions gracefully."""
    logger.error(f"❌ Unhandled exception: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "response": "Internal server error occurred",
            "error": str(exc),
            "timestamp": datetime.now().isoformat(),
            "agent_ready": False
        }
    )

if __name__ == "__main__":
    print("🚀 Starting ScheduleAI Agent (Fixed Version)...")
    print("📋 Available endpoints:")
    print("   GET  /           - Root endpoint")
    print("   GET  /health     - Health check")
    print("   GET  /test       - Test endpoint")
    print("   POST /chat       - Chat with agent")
    print("   GET  /docs       - API documentation")
    print()

    uvicorn.run(
        "main_fixed:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )