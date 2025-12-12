"""
FastAPI server for ScheduleAI - Italian Appointment Scheduling Agent.

This module provides a REST API server for the Pydantic AI scheduling agent,
enabling integration with web applications and the frontend chat interface.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Try to import the agent
try:
    from agent import ScheduleAIAgent
    from dependencies import create_dependencies
    from settings import load_settings
    from conversation_history import conversation_manager
    AGENT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Could not import ScheduleAI agent: {e}")
    AGENT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global agent instance
schedule_agent: Optional[ScheduleAIAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global schedule_agent

    # Startup
    logger.info("🚀 Starting ScheduleAI server...")

    try:
        if AGENT_AVAILABLE:
            # Load settings
            try:
                settings = load_settings()
                logger.info(f"✅ Settings loaded for environment: {settings.app_env}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load settings: {e}")

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

                # Test agent functionality
                if hasattr(schedule_agent, 'process_message'):
                    test_response = await schedule_agent.process_message(
                        "Ciao, test di inizializzazione",
                        session_id="test-session"
                    )
                    logger.info(f"✅ Agent test successful: {str(test_response)[:50]}...")
                else:
                    logger.warning("⚠️ Agent doesn't have process_message method")
            except Exception as e:
                logger.error(f"❌ Failed to initialize ScheduleAI agent: {e}")
                schedule_agent = None
        else:
            logger.warning("⚠️ Agent not available, running with limited functionality")
            schedule_agent = None

    except Exception as e:
        logger.error(f"❌ Unexpected error during startup: {e}")
        schedule_agent = None

    yield

    # Shutdown
    logger.info("🛑 Shutting down ScheduleAI server...")


# Initialize FastAPI app
app = FastAPI(
    title="ScheduleAI API",
    description="Italian Appointment Scheduling AI Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",
        "https://your-production-domain.com",  # Add your production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class ChatMessage(BaseModel):
    message: str = Field(..., description="User message to process")
    session_id: str = Field(default="default", description="Session identifier")
    business_id: Optional[str] = Field(None, description="Business identifier")
    consultant_id: Optional[str] = Field(None, description="Consultant identifier")
    stream: bool = Field(default=True, description="Whether to stream response")


class ChatResponse(BaseModel):
    response: str = Field(..., description="AI agent response")
    session_id: str = Field(..., description="Session identifier")
    timestamp: datetime = Field(..., description="Response timestamp")
    appointments: Optional[List[Dict[str, Any]]] = Field(None, description="Related appointments")
    agent_ready: bool = Field(True, description="Whether the AI agent is available")


class AppointmentRequest(BaseModel):
    client_name: str = Field(..., description="Client name")
    service_type: str = Field(..., description="Type of service")
    datetime_request: str = Field(..., description="Requested date/time")
    duration_minutes: int = Field(default=30, description="Appointment duration")
    notes: Optional[str] = Field(None, description="Additional notes")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    agent_ready: bool = Field(..., description="Whether AI agent is ready")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")


# Helper functions
async def generate_streaming_response(
    message: str,
    session_id: str,
    business_id: Optional[str] = None,
    consultant_id: Optional[str] = None
):
    """Generate streaming response from the agent."""
    if not schedule_agent:
        yield "data: {'error': 'Agent not available'}\n\n"
        return

    try:
        # Get response from agent
        response = await schedule_agent.process_message(
            message,
            session_id=session_id,
            business_id=business_id,
            consultant_id=consultant_id
        )

        # Extract clean response from AgentRunResult format
        clean_response = extract_clean_response(str(response))

        # Store assistant response in conversation history
        try:
            conversation_manager.add_message(
                session_id=session_id,
                role="assistant",
                content=clean_response,
                message_type="text"
            )
            logger.info(f"💾 Saved assistant response to conversation history: {session_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to save assistant response to history: {e}")

        # Stream the clean response
        for char in clean_response:
            chunk = json.dumps({"content": char})
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0.01)  # Small delay for streaming effect

        # Send final message
        final_chunk = json.dumps({"done": True})
        yield f"data: {final_chunk}\n\n"

    except Exception as e:
        error_chunk = json.dumps({"error": str(e)})
        yield f"data: {error_chunk}\n\n"


# API Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    return HealthResponse(
        status="healthy",
        agent_ready=schedule_agent is not None,
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check endpoint."""
    return HealthResponse(
        status="healthy",
        agent_ready=schedule_agent is not None,
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.post("/chat")
async def chat_endpoint(message_data: ChatMessage):
    """
    Main chat endpoint for interacting with ScheduleAI.

    Supports both streaming and non-streaming responses with conversation history tracking.

    - **message**: User message to process
    - **session_id**: Session identifier for conversation context and memory
    - **stream**: Whether to stream response (default: true)

    Returns AI agent response in Italian for appointment scheduling.
    """
    if not schedule_agent:
        # Provide mock response when agent is not available
        mock_response = get_mock_response(message_data.message)
        return {
            "response": mock_response,
            "session_id": message_data.session_id,
            "timestamp": datetime.now().isoformat(),
            "agent_ready": False
        }

    logger.info(f"💬 Received message: {message_data.message[:50]}...")

    # Store user message in conversation history
    try:
        conversation_manager.add_message(
            session_id=message_data.session_id,
            role="user",
            content=message_data.message,
            message_type="text"
        )
        logger.info(f"💾 Saved user message to conversation history: {message_data.session_id}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to save user message to history: {e}")

    if message_data.stream:
        return StreamingResponse(
            generate_streaming_response(
                message_data.message,
                message_data.session_id,
                message_data.business_id,
                message_data.consultant_id
            ),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )
    else:
        # Non-streaming response
        try:
            response = await schedule_agent.process_message(
                message_data.message,
                session_id=message_data.session_id,
                business_id=message_data.business_id,
                consultant_id=message_data.consultant_id
            )

            # Extract clean response from AgentRunResult format
            clean_response = extract_clean_response(str(response))

            return {
                "response": clean_response,
                "session_id": message_data.session_id,
                "timestamp": datetime.now().isoformat(),
                "agent_ready": True
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing message: {str(e)}"
            )


@app.post("/appointments")
async def create_appointment(appointment_data: AppointmentRequest):
    """
    Create a new appointment.

    This endpoint integrates with the agent to create appointments
    with validation and business logic.
    """
    if not schedule_agent:
        # Create a mock appointment when agent is not available
        mock_appointment = {
            "id": f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "client_name": appointment_data.client_name,
            "service_type": appointment_data.service_type,
            "datetime": appointment_data.datetime_request,
            "duration_minutes": appointment_data.duration_minutes,
            "notes": appointment_data.notes,
            "status": "confirmed",
            "agent_ready": False,
            "message": "Appuntamento creato con sistema base (agente non disponibile)"
        }

        logger.info(f"📅 Mock appointment created: {appointment_data.client_name}")
        return {
            "success": True,
            "appointment": mock_appointment,
            "timestamp": datetime.now(),
            "agent_ready": False
        }

    try:
        # Use the agent to create the appointment
        result = await schedule_agent.create_appointment(
            client_name=appointment_data.client_name,
            service_type=appointment_data.service_type,
            datetime_request=appointment_data.datetime_request,
            duration_minutes=appointment_data.duration_minutes,
            notes=appointment_data.notes
        )

        # Clean the response if it contains AgentRunResult format
        if "response" in result and result["response"]:
            result["response"] = extract_clean_response(str(result["response"]))

        logger.info(f"📅 Appointment created: {appointment_data.client_name}")

        return {
            "success": True,
            "appointment": result,
            "timestamp": datetime.now(),
            "agent_ready": True
        }

    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating appointment: {str(e)}"
        )


@app.get("/appointments")
async def get_appointments():
    """Get list of appointments."""
    # TODO: Implement real appointment retrieval from database
    return {
        "appointments": [],
        "timestamp": datetime.now(),
        "agent_ready": schedule_agent is not None
    }


@app.get("/services")
async def get_services():
    """Get list of available services with Italian service types."""
    return {
        "services": [
            {"id": "consulenza", "name": "Consulenza", "duration": 60, "description": "Consulenza generica"},
            {"id": "consulenza_fiscale", "name": "Consulenza Fiscale", "duration": 90, "description": "Consulenza specialistica fiscale"},
            {"id": "consulenza_legale", "name": "Consulenza Legale", "duration": 90, "description": "Consulenza legal e normativa"},
            {"id": "appunto", "name": "Appunto", "duration": 30, "description": "Breve appunto o chiarimento"},
            {"id": "riunione", "name": "Riunione", "duration": 60, "description": "Riunione di lavoro"},
            {"id": "incontro", "name": "Incontro", "duration": 45, "description": "Incontro conoscitivo"},
            {"id": "visita", "name": "Visita", "duration": 60, "description": "Visita o sopralluogo"},
            {"id": "seduta", "name": "Seduta", "duration": 50, "description": "Seduta di terapia o consulenza"},
            {"id": "colloquio", "name": "Colloquio", "duration": 30, "description": "Colloquio informativo"},
            {"id": "intervista", "name": "Intervista", "duration": 45, "description": "Intervista o valutazione"},
        ]
    }


@app.get("/availability")
async def check_availability(
    date: str,
    service: Optional[str] = None,
    consultant: Optional[str] = None
):
    """
    Check availability for a specific date.

    Query parameters:
    - date: Date to check (YYYY-MM-DD)
    - service: Optional service type
    - consultant: Optional consultant ID
    """
    if not schedule_agent:
        # Provide fallback availability when agent is not available
        return {
            "date": date,
            "available_slots": generate_fallback_slots(date),
            "timestamp": datetime.now(),
            "agent_ready": False
        }

    try:
        # Use the agent to check availability
        availability_result = await schedule_agent.check_availability(
            datetime_request=f"disponibilità per {date}",
            consultant_id=consultant
        )

        # Extract available slots from agent response or provide fallback
        available_slots = extract_time_slots(availability_result.get("response", ""))
        if not available_slots:
            available_slots = generate_fallback_slots(date)

        return {
            "date": date,
            "available_slots": available_slots,
            "timestamp": datetime.now(),
            "agent_ready": True,
            "service_type": service,
            "consultant_id": consultant
        }

    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        # Provide fallback slots even on error
        return {
            "date": date,
            "available_slots": generate_fallback_slots(date),
            "timestamp": datetime.now(),
            "agent_ready": False,
            "error": str(e)
        }


@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: Optional[int] = 50):
    """Get chat history for a specific session."""
    try:
        # Get conversation history from the manager
        messages = conversation_manager.get_conversation_history(session_id, limit=limit)

        # Convert messages to dict format
        message_dicts = []
        for msg in messages:
            message_dict = {
                "timestamp": msg.timestamp,
                "role": msg.role,
                "content": msg.content,
                "message_type": msg.message_type,
                "metadata": msg.metadata
            }
            message_dicts.append(message_dict)

        # Get appointment info from the conversation
        appointment_info = conversation_manager.extract_appointment_info(session_id)

        return {
            "session_id": session_id,
            "messages": message_dicts,
            "appointment_info": appointment_info,
            "timestamp": datetime.now(),
            "message_count": len(message_dicts)
        }

    except Exception as e:
        logger.error(f"Error retrieving session history: {e}")
        return {
            "session_id": session_id,
            "messages": [],
            "appointment_info": {},
            "timestamp": datetime.now(),
            "message_count": 0,
            "error": str(e)
        }


@app.get("/sessions/{session_id}/context")
async def get_session_context(session_id: str, message_count: int = 10):
    """Get formatted conversation context for agent input."""
    try:
        context = conversation_manager.get_recent_context(session_id, message_count)
        return {
            "session_id": session_id,
            "context": context,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error retrieving session context: {e}")
        return {
            "session_id": session_id,
            "context": "Nessuna conversazione precedente.",
            "timestamp": datetime.now(),
            "error": str(e)
        }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session."""
    try:
        success = conversation_manager.delete_session(session_id)
        if success:
            return {
                "session_id": session_id,
                "deleted": True,
                "timestamp": datetime.now()
            }
        else:
            return {
                "session_id": session_id,
                "deleted": False,
                "timestamp": datetime.now(),
                "error": "Session not found"
            }
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        return {
            "session_id": session_id,
            "deleted": False,
            "timestamp": datetime.now(),
            "error": str(e)
        }


@app.get("/sessions")
async def list_sessions():
    """List all conversation sessions."""
    try:
        sessions = conversation_manager.get_all_sessions()
        return {
            "sessions": sessions,
            "total_count": len(sessions),
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return {
            "sessions": {},
            "total_count": 0,
            "timestamp": datetime.now(),
            "error": str(e)
        }


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


def generate_fallback_slots(date_str: str) -> List[str]:
    """Generate fallback time slots for a given date."""
    try:
        from datetime import datetime, timedelta
        import calendar

        # Parse the date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Check if it's a weekend
        if target_date.weekday() >= 5:  # Saturday (5) or Sunday (6)
            return []  # No slots on weekends

        # Generate business hour slots
        slots = []
        for hour in range(9, 18):  # 9 AM to 5 PM
            for minute in [0, 30]:  # On the hour and half hour
                if hour == 17 and minute == 30:  # Skip 5:30 PM
                    continue
                slots.append(f"{hour:02d}:{minute:02d}")

        return slots
    except:
        # Fallback to default slots if date parsing fails
        return [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
        ]


def extract_time_slots(text: str) -> List[str]:
    """Extract time slots from agent response text."""
    import re

    # Look for time patterns like "09:00", "14:30", etc.
    time_pattern = r'\b([0-1]?[0-9]|2[0-3]):[0-5][0-9]\b'
    matches = re.findall(time_pattern, text)

    # Filter for reasonable business hours
    valid_slots = []
    for match in matches:
        hour, minute = match.split(':')
        hour = int(hour)
        minute = int(minute)

        # Business hours: 8 AM - 7 PM
        if 8 <= hour <= 19 and minute in [0, 15, 30, 45]:
            valid_slots.append(f"{hour:02d}:{minute:02d}")

    return sorted(list(set(valid_slots)))  # Remove duplicates and sort


def extract_clean_response(agent_response: str) -> str:
    """Extract clean text response from AgentRunResult format."""
    import re

    if not agent_response:
        return "Risposta non disponibile."

    # If response is already clean text, return as is
    if not agent_response.startswith("AgentRunResult("):
        return agent_response

    # Extract text from AgentRunResult(output='...')
    pattern = r"AgentRunResult\(output=['\"](.*?)['\"](?:,\s*.*?)?\)"
    match = re.search(pattern, agent_response, re.DOTALL)

    if match:
        extracted_text = match.group(1)
        # Clean up escaped characters
        extracted_text = extracted_text.replace(r"\'", "'")
        extracted_text = extracted_text.replace(r'\"', '"')
        extracted_text = extracted_text.replace(r'\n', '\n')
        extracted_text = extracted_text.replace(r'\t', '\t')
        extracted_text = extracted_text.replace(r'\\', '\\')
        return extracted_text

    # Fallback: try to extract content between first and last quote
    if "'" in agent_response:
        parts = agent_response.split("'")
        if len(parts) >= 3:
            return parts[1]

    # Final fallback: return original if no extraction worked
    return agent_response


@app.get("/consultants")
async def get_consultants():
    """Get list of available consultants."""
    return {
        "consultants": [
            {
                "id": "dr_rossi",
                "name": "Dr. Mario Rossi",
                "services": ["consulenza", "consulenza_fiscale"],
                "specialization": "Consulenza fiscale e aziendale"
            },
            {
                "id": "dr_bianchi",
                "name": "Dr. Laura Bianchi",
                "services": ["consulenza_legale", "appunto"],
                "specialization": "Consulenza legale e contrattuale"
            },
            {
                "id": "dr_verdi",
                "name": "Dr. Giuseppe Verdi",
                "services": ["consulenza", "riunione"],
                "specialization": "Consulenza strategica e riunioni"
            },
            {
                "id": "dr_ferrari",
                "name": "Dott.ssa Anna Ferrari",
                "services": ["colloquio", "intervista"],
                "specialization": "Colloqui e selezione personale"
            },
        ]
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle global exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": "Internal server error",
        "detail": str(exc),
        "timestamp": datetime.now()
    }


if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )