"""
Main Italian Appointment Scheduling AI Agent implementation.

This module provides the complete Pydantic AI agent for managing appointments
in Italian professional consulting contexts with Google Calendar integration.
"""

from pydantic_ai import Agent, RunContext
from typing import Optional, Dict

# Handle both relative and absolute imports
try:
    from .providers import get_llm_model, is_test_environment, create_test_model
    from .dependencies import ScheduleAgentDependencies, create_dependencies
    from .prompts import SYSTEM_PROMPT_WITH_MEMORY, get_dynamic_context
    from .tools import register_tools
    from .conversation_history import conversation_manager
except ImportError:
    # Running as script directly
    try:
        from providers import get_llm_model, is_test_environment, create_test_model
        from dependencies import ScheduleAgentDependencies, create_dependencies
        from prompts import SYSTEM_PROMPT_WITH_MEMORY, get_dynamic_context
        from tools import register_tools
        from conversation_history import conversation_manager
    except ImportError:
        # Try adding current directory to path
        import os
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from providers import get_llm_model, is_test_environment, create_test_model
        from dependencies import ScheduleAgentDependencies, create_dependencies
        from prompts import SYSTEM_PROMPT_WITH_MEMORY, get_dynamic_context
        from tools import register_tools
        from conversation_history import conversation_manager
import logging

logger = logging.getLogger(__name__)


class ScheduleAIAgent:
    """
    Main agent class for Italian appointment scheduling.

    This agent handles natural Italian conversations for appointment management,
    integrates with Google Calendar, and enforces business rules.
    """

    def __init__(self, dependencies: Optional[ScheduleAgentDependencies] = None):
        """
        Initialize the scheduling AI agent.

        Args:
            dependencies: Optional pre-configured dependencies
        """
        self.dependencies = dependencies or create_dependencies()
        self.model = self._get_model()
        self.agent = self._create_agent()

    def _get_model(self):
        """Get the appropriate model based on environment."""
        if is_test_environment():
            return create_test_model()
        return get_llm_model()

    def _create_agent(self) -> Agent:
        """Create and configure the Pydantic AI agent with memory capabilities."""
        agent = Agent(
            self.model,
            deps_type=ScheduleAgentDependencies,
            system_prompt=SYSTEM_PROMPT_WITH_MEMORY
        )

        # Add dynamic context prompt (includes conversation history)
        agent.system_prompt(get_dynamic_context)

        # Register tools
        register_tools(agent, ScheduleAgentDependencies)

        logger.info("Schedule AI Agent initialized successfully with memory capabilities")
        return agent

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        business_id: Optional[str] = None,
        consultant_id: Optional[str] = None
    ) -> str:
        """
        Process a user message and return the agent response with conversation memory.

        Args:
            message: Italian message from user
            session_id: Optional session identifier for conversation memory
            business_id: Optional business identifier
            consultant_id: Optional consultant identifier

        Returns:
            Agent response in Italian
        """
        try:
            # Add conversation history context if available
            enhanced_message = message
            if session_id:
                try:
                    # Get recent conversation context
                    context = conversation_manager.get_recent_context(session_id, message_count=10)
                    if context and "Nessuna conversazione precedente" not in context:
                        enhanced_message = f"{context}\n\n\nMESSAGGIO ATTUALE: {message}"
                        logger.info(f"Added conversation context for session {session_id}")
                except Exception as e:
                    logger.warning(f"Failed to get conversation context for {session_id}: {e}")

            # Update dependencies with runtime context
            if session_id or business_id or consultant_id:
                # Create updated dependencies for this request
                deps = create_dependencies(
                    session_id=session_id,
                    business_id=business_id,
                    consultant_id=consultant_id
                )
            else:
                deps = self.dependencies

            # Run the agent with enhanced message including context
            result = await self.agent.run(enhanced_message, deps=deps)

            logger.info(f"Processed message for session {session_id}: {message[:50]}...")

            # Handle different Pydantic AI versions
            try:
                # Try newer Pydantic AI versions
                return str(result)
            except AttributeError:
                try:
                    # Fallback for different attribute names
                    return result.data
                except AttributeError:
                    # Final fallback
                    return result.output if hasattr(result, 'output') else str(result)

        except Exception as e:
            error_msg = f"Mi dispiace, si è verificato un errore: {str(e)}"
            logger.error(f"Error processing message: {e}")
            return error_msg

    async def create_appointment(
        self,
        client_name: str,
        service_type: str,
        datetime_request: str,
        client_email: Optional[str] = None,
        consultant_id: Optional[str] = None,
        duration_minutes: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Create an appointment through the agent.

        Args:
            client_name: Name of the client
            service_type: Type of service
            datetime_request: Natural language date/time request in Italian
            client_email: Optional client email
            consultant_id: Optional consultant identifier

        Returns:
            Dictionary with appointment creation result
        """
        try:
            # Create appointment request message
            message = f"Vorrei prenotare un appuntamento per {service_type}. {datetime_request}. Cliente: {client_name}"
            if client_email:
                message += f", Email: {client_email}"
            if duration_minutes:
                message += f", Durata: {duration_minutes} minuti"
            if notes:
                message += f", Note: {notes}"

            # Process through agent
            response = await self.process_message(
                message=message,
                consultant_id=consultant_id
            )

            return {
                "success": True,
                "response": response,
                "client_name": client_name,
                "service_type": service_type
            }

        except Exception as e:
            logger.error(f"Failed to create appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def check_availability(
        self,
        datetime_request: str,
        consultant_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Check availability for a given time.

        Args:
            datetime_request: Natural language date/time request in Italian
            consultant_id: Optional consultant identifier

        Returns:
            Dictionary with availability information
        """
        try:
            message = f"Controlla la disponibilità per {datetime_request}"
            if consultant_id:
                message += f" con il consulente {consultant_id}"

            response = await self.process_message(
                message=message,
                consultant_id=consultant_id
            )

            return {
                "success": True,
                "response": response,
                "datetime_request": datetime_request
            }

        except Exception as e:
            logger.error(f"Failed to check availability: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def modify_appointment(
        self,
        modification_request: str,
        consultant_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Modify an existing appointment.

        Args:
            modification_request: Natural language modification request in Italian
            consultant_id: Optional consultant identifier

        Returns:
            Dictionary with modification result
        """
        try:
            message = f"Vorrei modificare un appuntamento: {modification_request}"

            response = await self.process_message(
                message=message,
                consultant_id=consultant_id
            )

            return {
                "success": True,
                "response": response,
                "modification_request": modification_request
            }

        except Exception as e:
            logger.error(f"Failed to modify appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def cancel_appointment(
        self,
        cancellation_request: str,
        consultant_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Cancel an existing appointment.

        Args:
            cancellation_request: Natural language cancellation request in Italian
            consultant_id: Optional consultant identifier

        Returns:
            Dictionary with cancellation result
        """
        try:
            message = f"Vorrei cancellare un appuntamento: {cancellation_request}"

            response = await self.process_message(
                message=message,
                consultant_id=consultant_id
            )

            return {
                "success": True,
                "response": response,
                "cancellation_request": cancellation_request
            }

        except Exception as e:
            logger.error(f"Failed to cancel appointment: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global agent instance
_agent_instance: Optional[ScheduleAIAgent] = None


def get_agent(dependencies: Optional[ScheduleAgentDependencies] = None) -> ScheduleAIAgent:
    """
    Get or create the global agent instance.

    Args:
        dependencies: Optional dependencies for the agent

    Returns:
        ScheduleAIAgent instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ScheduleAIAgent(dependencies)
    return _agent_instance


async def process_appointment_request(
    message: str,
    session_id: Optional[str] = None,
    business_id: Optional[str] = None,
    consultant_id: Optional[str] = None
) -> str:
    """
    Convenience function to process appointment requests.

    Args:
        message: Italian message from user
        session_id: Optional session identifier
        business_id: Optional business identifier
        consultant_id: Optional consultant identifier

    Returns:
        Agent response in Italian
    """
    agent = get_agent()
    return await agent.process_message(
        message=message,
        session_id=session_id,
        business_id=business_id,
        consultant_id=consultant_id
    )