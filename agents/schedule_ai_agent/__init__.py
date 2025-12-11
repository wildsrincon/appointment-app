"""
Italian Appointment Scheduling AI Agent

A Pydantic AI agent for autonomous appointment management in Italian
professional consulting contexts with Google Calendar integration.
"""

from .agent import ScheduleAIAgent, get_agent, process_appointment_request
from .dependencies import ScheduleAgentDependencies, create_dependencies
from .settings import ScheduleSettings, load_settings, get_settings
from .tools import register_tools
from .prompts import SYSTEM_PROMPT, get_dynamic_context

__version__ = "1.0.0"
__author__ = "Schedule AI Agent Team"
__description__ = "Italian AI Agent for Professional Appointment Scheduling"

__all__ = [
    "ScheduleAIAgent",
    "get_agent",
    "process_appointment_request",
    "ScheduleAgentDependencies",
    "create_dependencies",
    "ScheduleSettings",
    "load_settings",
    "get_settings",
    "register_tools",
    "SYSTEM_PROMPT",
    "get_dynamic_context"
]