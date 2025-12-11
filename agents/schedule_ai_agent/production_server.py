"""
Production-ready server for ScheduleAI API deployment on Railway.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import FastAPI for production deployment
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("FastAPI not available, falling back to simple HTTP server")
    FASTAPI_AVAILABLE = False

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

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="ScheduleAI API",
        description="Italian Appointment Scheduling Assistant",
        version="1.0.0"
    )

    # Configure CORS for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://your-frontend-domain.vercel.app",  # Replace with your Vercel domain
            "http://localhost:3000",
            "http://localhost:3001"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
        schedule_agent = ScheduleAIAgent(model=dependencies.model)
        logger.info("✅ ScheduleAI agent initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        return False

if FASTAPI_AVAILABLE:
    @app.on_event("startup")
    async def startup_event():
        """Initialize the agent on server startup."""
        await initialize_agent()

    @app.get("/")
    async def root():
        """Health check endpoint."""
        return {
            "message": "ScheduleAI API is running",
            "timestamp": datetime.now().isoformat(),
            "agent_available": AGENT_AVAILABLE and schedule_agent is not None
        }

    @app.post("/chat")
    async def chat_endpoint(request: dict):
        """Handle chat messages with the AI agent."""
        try:
            if not schedule_agent:
                raise HTTPException(
                    status_code=503,
                    detail="AI agent not available"
                )

            user_message = request.get("message", "")
            if not user_message:
                raise HTTPException(
                    status_code=400,
                    detail="Message is required"
                )

            # Process message with agent
            response = await schedule_agent.run(user_message)

            return {
                "response": response.data,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Chat endpoint error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health_check():
        """Detailed health check."""
        return {
            "status": "healthy",
            "agent_available": AGENT_AVAILABLE and schedule_agent is not None,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }

def run_server():
    """Run the server in production mode."""
    if FASTAPI_AVAILABLE:
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    else:
        logger.error("FastAPI is required for production deployment")
        return

if __name__ == "__main__":
    run_server()