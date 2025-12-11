"""
Simplified FastAPI-like server for ScheduleAI - Italian Appointment Scheduling Agent.

This is a simplified version that works without FastAPI dependencies.
Uses basic HTTP server with JSON responses.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import the agent
try:
    from agent import ScheduleAIAgent
    from dependencies import create_dependencies
    AGENT_AVAILABLE = True
    logger.info("✅ ScheduleAI agent imports successful")
except ImportError as e:
    logger.warning(f"⚠️ Could not import ScheduleAI agent: {e}")
    AGENT_AVAILABLE = False

# Global agent instance
schedule_agent: Optional[ScheduleAIAgent] = None


async def initialize_agent():
    """Initialize the ScheduleAI agent."""
    global schedule_agent

    if not AGENT_AVAILABLE:
        logger.warning("⚠️ Agent not available, using mock responses")
        return False

    try:
        # Create dependencies
        dependencies = create_dependencies()
        logger.info("✅ Dependencies created")

        # Initialize agent
        schedule_agent = ScheduleAIAgent(dependencies)
        logger.info("✅ ScheduleAI agent initialized")

        # Test agent functionality
        if hasattr(schedule_agent, 'process_message'):
            test_response = await schedule_agent.process_message(
                "Ciao, test di inizializzazione",
                session_id="test-session"
            )
            logger.info(f"✅ Agent test successful: {str(test_response)[:50]}...")
            return True
        else:
            logger.warning("⚠️ Agent doesn't have process_message method")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to initialize ScheduleAI agent: {e}")
        schedule_agent = None
        return False


class ScheduleAIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ScheduleAI API."""

    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json_response(self, data: Dict, status_code: int = 200):
        """Send JSON response with proper headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        response_data = {
            **data,
            'timestamp': datetime.now().isoformat()
        }

        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))

    def _parse_json_body(self):
        """Parse JSON body from request."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            return json.loads(post_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error parsing JSON body: {e}")
            return None

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self._send_json_response({
                "status": "healthy",
                "agent_ready": schedule_agent is not None,
                "version": "1.0.0",
                "message": "ScheduleAI API is running"
            })
        elif self.path == '/health':
            self._send_json_response({
                "status": "healthy",
                "agent_ready": schedule_agent is not None,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })
        elif self.path == '/services':
            self._send_json_response({
                "services": [
                    {"id": "consulting", "name": "Consulenza", "duration": 60},
                    {"id": "followup", "name": "Follow-up", "duration": 30},
                    {"id": "evaluation", "name": "Valutazione", "duration": 90},
                ]
            })
        else:
            self._send_json_response({"error": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/chat':
            self.handle_chat_request()
        elif self.path == '/appointments':
            self.handle_appointment_request()
        else:
            self._send_json_response({"error": "Not found"}, 404)

    def handle_chat_request(self):
        """Handle chat endpoint."""
        try:
            data = self._parse_json_body()
            if not data:
                self._send_json_response({"error": "Invalid JSON"}, 400)
                return

            message = data.get('message', '')
            session_id = data.get('session_id', 'default')

            if not message:
                self._send_json_response({"error": "Message is required"}, 400)
                return

            logger.info(f"💬 Received message: {message[:50]}...")

            # Process message with agent or use mock response
            if schedule_agent and hasattr(schedule_agent, 'process_message'):
                # Use real agent - handle properly for sync context
                try:
                    # Create or get event loop for this thread
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is running, we need to run in a separate thread
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(
                                    lambda: asyncio.run(schedule_agent.process_message(message, session_id=session_id))
                                )
                                response = future.result(timeout=30)
                        else:
                            # If loop is not running, run normally
                            response = loop.run_until_complete(
                                schedule_agent.process_message(message, session_id=session_id)
                            )
                    except RuntimeError:
                        # No event loop, create new one
                        response = asyncio.run(schedule_agent.process_message(message, session_id=session_id))

                except Exception as e:
                    logger.error(f"Error processing message with agent: {e}")
                    response = f"Mi dispiace, si è verificato un errore: {str(e)}"
            else:
                # Mock response
                response = self.get_mock_response(message)

            self._send_json_response({
                "response": response,
                "session_id": session_id,
                "agent_used": schedule_agent is not None
            })

        except Exception as e:
            logger.error(f"Error handling chat request: {e}")
            self._send_json_response({
                "error": "Internal server error",
                "detail": str(e)
            }, 500)

    def handle_appointment_request(self):
        """Handle appointment creation request."""
        try:
            data = self._parse_json_body()
            if not data:
                self._send_json_response({"error": "Invalid JSON"}, 400)
                return

            # Mock appointment creation
            appointment = {
                "id": f"apt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "client_name": data.get('client_name', 'Cliente'),
                "service_type": data.get('service_type', 'Consulenza'),
                "datetime": data.get('datetime_request', datetime.now().isoformat()),
                "duration_minutes": data.get('duration_minutes', 30),
                "status": "pending",
                "notes": data.get('notes', '')
            }

            logger.info(f"📅 Appointment created: {appointment['client_name']}")

            self._send_json_response({
                "success": True,
                "appointment": appointment
            })

        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            self._send_json_response({
                "error": "Failed to create appointment",
                "detail": str(e)
            }, 500)

    def get_mock_response(self, message: str) -> str:
        """Generate mock response for testing."""
        message_lower = message.lower()

        if 'ciao' in message_lower or 'buongiorno' in message_lower:
            return "Buongiorno! Sono ScheduleAI, il tuo assistente per le prenotazioni. Come posso aiutarti oggi?"
        elif 'appuntamento' in message_lower or 'prenotare' in message_lower:
            return "Certamente! Posso aiutarti a prenotare un appuntamento. Che tipo di servizio desideri e quando preferiresti?"
        elif 'disponibile' in message_lower or 'quando' in message_lower:
            return "Posso controllare le disponibilità per te. Che giorno ti interessa e di che tipo di servizio hai bisogno?"
        else:
            return "Sono ScheduleAI, il tuo assistente per prenotazioni. Posso aiutarti a prenotare appuntamenti, controllare disponibilità e gestire la tua agenda. Come posso assisterti?"

    def log_message(self, format, *args):
        """Override logging to use proper format."""
        logger.info(f"{self.address_string} - {format % args}")


async def main():
    """Main function to start the server."""
    # Initialize agent
    await initialize_agent()

    # Start HTTP server
    server_address = ('127.0.0.1', 8000)
    httpd = HTTPServer(server_address, ScheduleAIHandler)

    logger.info("🚀 Starting ScheduleAI server...")
    logger.info(f"📍 Server running on http://{server_address[0]}:{server_address[1]}")
    logger.info("📚 API endpoints:")
    logger.info("   GET  /        - Health check")
    logger.info("   GET  /health  - Detailed health status")
    logger.info("   POST /chat    - Chat with ScheduleAI")
    logger.info("   POST /appointments - Create appointment")
    logger.info("   GET  /services - List available services")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())