"""
Database-integrated tools for Italian Appointment Scheduling AI Agent.

This module provides enhanced tools that integrate with the PostgreSQL database
for appointment management, client operations, and business analytics.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic_ai import RunContext
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import logging
import json
import uuid

# Handle both relative and absolute imports
try:
    from .dependencies import ScheduleAgentDependencies
    from .models import (
        AppointmentCreate, AppointmentUpdate, ClientCreate,
        AppointmentStatus, ServiceType,
        AppointmentInDB, ClientInDB, ConsultantInDB
    )
except ImportError:
    try:
        from dependencies import ScheduleAgentDependencies
        from models import (
            AppointmentCreate, AppointmentUpdate, ClientCreate,
            AppointmentStatus, ServiceType,
            AppointmentInDB, ClientInDB, ConsultantInDB
        )
    except ImportError:
        # Try adding current directory to path
        import os
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from dependencies import ScheduleAgentDependencies
        from models import (
            AppointmentCreate, AppointmentUpdate, ClientCreate,
            AppointmentStatus, ServiceType,
            AppointmentInDB, ClientInDB, ConsultantInDB
        )

logger = logging.getLogger(__name__)


# Pydantic models for tool inputs
class CreateAppointmentInput(BaseModel):
    """Input for creating appointment with database."""
    client_name: str = Field(..., description="Nome completo del cliente")
    client_email: str = Field(..., description="Email del cliente")
    client_phone: Optional[str] = Field(None, description="Numero di telefono del cliente")
    consultant_id: str = Field(..., description="ID del consulente")
    business_id: str = Field(default="default-business", description="ID dell'azienda")
    service_type: ServiceType = Field(..., description="Tipo di servizio")
    title: str = Field(..., description="Titolo dell'appuntamento")
    description: Optional[str] = Field(None, description="Descrizione dell'appuntamento")
    datetime_request: str = Field(..., description="Data e ora richieste (formato: YYYY-MM-DD HH:MM)")
    duration_minutes: int = Field(default=30, description="Durata in minuti")
    notes: Optional[str] = Field(None, description="Note aggiuntive")

    class Config:
        use_enum_values = True


class CheckAvailabilityInput(BaseModel):
    """Input for checking availability."""
    consultant_id: str = Field(..., description="ID del consulente")
    datetime_request: str = Field(..., description="Data e ora richieste (formato: YYYY-MM-DD HH:MM)")
    duration_minutes: int = Field(default=30, description="Durata in minuti")


class CreateClientInput(BaseModel):
    """Input for creating client."""
    name: str = Field(..., description="Nome completo del cliente")
    email: str = Field(..., description="Email del cliente")
    phone: Optional[str] = Field(None, description="Numero di telefono del cliente")
    notes: Optional[str] = Field(None, description="Note sul cliente")


class ListAppointmentsInput(BaseModel):
    """Input for listing appointments."""
    business_id: Optional[str] = Field(None, description="ID dell'azienda")
    consultant_id: Optional[str] = Field(None, description="ID del consulente")
    client_email: Optional[str] = Field(None, description="Email del cliente")
    status: Optional[AppointmentStatus] = Field(None, description="Stato degli appuntamenti")
    start_date: Optional[str] = Field(None, description="Data di inizio (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Data di fine (YYYY-MM-DD)")
    limit: int = Field(default=50, description="Numero massimo di risultati")

    class Config:
        use_enum_values = True


class UpdateAppointmentInput(BaseModel):
    """Input for updating appointment."""
    appointment_id: str = Field(..., description="ID dell'appuntamento")
    title: Optional[str] = Field(None, description="Nuovo titolo")
    description: Optional[str] = Field(None, description="Nuova descrizione")
    datetime_request: Optional[str] = Field(None, description="Nuova data e ora (formato: YYYY-MM-DD HH:MM)")
    duration_minutes: Optional[int] = Field(None, description="Nuova durata in minuti")
    status: Optional[AppointmentStatus] = Field(None, description="Nuovo stato")
    notes: Optional[str] = Field(None, description="Note aggiuntive")

    class Config:
        use_enum_values = True


# Database tool functions
async def db_create_appointment(
    ctx: RunContext[ScheduleAgentDependencies],
    input_data: CreateAppointmentInput
) -> Dict[str, Any]:
    """
    Create a new appointment in the database.

    Crea un nuovo appuntamento nel database con validazione e controllo disponibilità.
    """
    try:
        # Get database client
        db = await ctx.deps.get_db_client()

        # Parse datetime
        try:
            start_time = datetime.strptime(input_data.datetime_request, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Formato data e ora non valido. Usare: YYYY-MM-DD HH:MM")

        # Check if consultant exists
        consultant = await db.get_consultant(input_data.consultant_id)
        if not consultant:
            return {
                "success": False,
                "error": f"Consulente non trovato: {input_data.consultant_id}",
                "message": "Il consulente selezionato non esiste nel sistema."
            }

        # Check availability
        end_time = start_time + timedelta(minutes=input_data.duration_minutes)
        is_available = await db.check_availability(
            consultant_id=input_data.consultant_id,
            start_time=start_time,
            end_time=end_time
        )

        if not is_available:
            # Get conflicting appointments
            conflicting = await db.list_appointments(
                consultant_id=input_data.consultant_id,
                start_date=start_time,
                end_date=end_time,
                status=AppointmentStatus.SCHEDULED,
                limit=3
            )

            return {
                "success": False,
                "error": "Consulente non disponibile",
                "message": f"Il Dott. {consultant.name} non è disponibile all'orario richiesto.",
                "conflicting_appointments": [
                    {
                        "datetime": apt.start_time.strftime("%Y-%m-%d %H:%M"),
                        "title": apt.title
                    } for apt in conflicting
                ]
            }

        # Create or update client
        client_data = ClientCreate(
            email=input_data.client_email,
            name=input_data.client_name,
            phone=input_data.client_phone
        )
        client = await db.create_client(client_data)

        # Create appointment
        appointment_data = AppointmentCreate(
            id=str(uuid.uuid4()),
            business_id=input_data.business_id,
            consultant_id=input_data.consultant_id,
            client_email=client.email,
            service_type=input_data.service_type,
            title=input_data.title,
            description=input_data.description,
            start_time=start_time,
            duration_minutes=input_data.duration_minutes,
            notes=input_data.notes,
            client_phone=input_data.client_phone
        )

        appointment = await db.create_appointment(appointment_data)

        # Format response in Italian
        response = {
            "success": True,
            "message": f"Appuntamento creato con successo per {input_data.client_name}",
            "appointment": {
                "id": appointment.id,
                "title": appointment.title,
                "datetime": appointment.start_time.strftime("%d/%m/%Y alle %H:%M"),
                "duration": f"{appointment.duration_minutes} minuti",
                "consultant": consultant.name,
                "client": client.name,
                "status": appointment.status
            }
        }

        logger.info(f"✅ Appointment created via agent: {appointment.id}")
        return response

    except Exception as e:
        logger.error(f"❌ Failed to create appointment via agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Si è verificato un errore durante la creazione dell'appuntamento."
        }


async def db_check_availability(
    ctx: RunContext[ScheduleAgentDependencies],
    input_data: CheckAvailabilityInput
) -> Dict[str, Any]:
    """
    Check consultant availability for a time slot.

    Controlla la disponibilità di un consulente per un determinato orario.
    """
    try:
        db = await ctx.deps.get_db_client()

        # Parse datetime
        try:
            start_time = datetime.strptime(input_data.datetime_request, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Formato data e ora non valido. Usare: YYYY-MM-DD HH:MM")

        # Get consultant info
        consultant = await db.get_consultant(input_data.consultant_id)
        if not consultant:
            return {
                "available": False,
                "message": f"Consulente non trovato: {input_data.consultant_id}",
                "consultant_name": None
            }

        # Check availability
        end_time = start_time + timedelta(minutes=input_data.duration_minutes)
        is_available = await db.check_availability(
            consultant_id=input_data.consultant_id,
            start_time=start_time,
            end_time=end_time
        )

        # Get next available slots if not available
        next_slots = []
        if not is_available:
            # Find next 3 available slots (same duration, 30-minute intervals)
            current_time = start_time + timedelta(hours=1)
            found_slots = 0

            while found_slots < 3 and current_time.date() == start_time.date():
                slot_end = current_time + timedelta(minutes=input_data.duration_minutes)
                if await db.check_availability(input_data.consultant_id, current_time, slot_end):
                    next_slots.append(current_time.strftime("%H:%M"))
                    found_slots += 1
                current_time += timedelta(minutes=30)

        response = {
            "available": is_available,
            "message": (
                f"Il Dott. {consultant.name} è disponibile il {start_time.strftime('%d/%m/%Y alle %H:%M')}"
                if is_available
                else f"Il Dott. {consultant.name} non è disponibile il {start_time.strftime('%d/%m/%Y alle %H:%M')}"
            ),
            "consultant_name": consultant.name,
            "requested_time": start_time.strftime("%d/%m/%Y alle %H:%M"),
            "duration": f"{input_data.duration_minutes} minuti"
        }

        if not is_available and next_slots:
            response["next_available_slots"] = next_slots
            response["suggestion"] = f"Orari successivi disponibili: {', '.join(next_slots)}"

        return response

    except Exception as e:
        logger.error(f"❌ Failed to check availability via agent: {e}")
        return {
            "available": False,
            "message": f"Errore durante il controllo disponibilità: {str(e)}",
            "consultant_name": None
        }


async def db_create_client(
    ctx: RunContext[ScheduleAgentDependencies],
    input_data: CreateClientInput
) -> Dict[str, Any]:
    """
    Create a new client in the database.

    Crea un nuovo cliente nel database.
    """
    try:
        db = await ctx.deps.get_db_client()

        client_data = ClientCreate(
            email=input_data.email,
            name=input_data.name,
            phone=input_data.phone,
            notes=input_data.notes
        )

        client = await db.create_client(client_data)

        return {
            "success": True,
            "message": f"Cliente {input_data.name} creato con successo",
            "client": {
                "email": client.email,
                "name": client.name,
                "phone": client.phone
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to create client via agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Si è verificato un errore durante la creazione del cliente."
        }


async def db_list_appointments(
    ctx: RunContext[ScheduleAgentDependencies],
    input_data: ListAppointmentsInput
) -> Dict[str, Any]:
    """
    List appointments with optional filtering.

    Elenca gli appuntamenti con filtri opzionali.
    """
    try:
        db = await ctx.deps.get_db_client()

        # Parse dates if provided
        start_date = None
        end_date = None
        if input_data.start_date:
            try:
                start_date = datetime.strptime(input_data.start_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Formato data inizio non valido. Usare: YYYY-MM-DD")

        if input_data.end_date:
            try:
                end_date = datetime.strptime(input_data.end_date, "%Y-%m-%d")
                # Add one day to make it inclusive
                end_date = end_date + timedelta(days=1)
            except ValueError:
                raise ValueError("Formato data fine non valido. Usare: YYYY-MM-DD")

        appointments = await db.list_appointments(
            business_id=input_data.business_id,
            consultant_id=input_data.consultant_id,
            client_email=input_data.client_email,
            status=input_data.status,
            start_date=start_date,
            end_date=end_date,
            limit=input_data.limit
        )

        # Format appointments for response
        formatted_appointments = []
        for apt in appointments:
            formatted_appointments.append({
                "id": apt.id,
                "title": apt.title,
                "datetime": apt.start_time.strftime("%d/%m/%Y alle %H:%M"),
                "duration": f"{apt.duration_minutes} minuti",
                "client": apt.client.name if apt.client else "Sconosciuto",
                "consultant": apt.consultant.name if apt.consultant else "Sconosciuto",
                "status": apt.status,
                "service_type": apt.service_type
            })

        return {
            "success": True,
            "message": f"Trovati {len(formatted_appointments)} appuntamenti",
            "appointments": formatted_appointments,
            "count": len(formatted_appointments)
        }

    except Exception as e:
        logger.error(f"❌ Failed to list appointments via agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Si è verificato un errore durante il recupero degli appuntamenti."
        }


async def db_update_appointment(
    ctx: RunContext[ScheduleAgentDependencies],
    input_data: UpdateAppointmentInput
) -> Dict[str, Any]:
    """
    Update an existing appointment.

    Aggiorna un appuntamento esistente.
    """
    try:
        db = await ctx.deps.get_db_client()

        # Check if appointment exists
        existing = await db.get_appointment(input_data.appointment_id)
        if not existing:
            return {
                "success": False,
                "error": "Appuntamento non trovato",
                "message": "L'appuntamento specificato non esiste nel sistema."
            }

        # Prepare update data
        update_data = AppointmentUpdate()

        if input_data.title:
            update_data.title = input_data.title
        if input_data.description is not None:
            update_data.description = input_data.description
        if input_data.status:
            update_data.status = input_data.status
        if input_data.notes is not None:
            update_data.notes = input_data.notes

        # Handle datetime and duration updates
        if input_data.datetime_request:
            try:
                start_time = datetime.strptime(input_data.datetime_request, "%Y-%m-%d %H:%M")
                update_data.start_time = start_time
            except ValueError:
                raise ValueError("Formato data e ora non valido. Usare: YYYY-MM-DD HH:MM")

        if input_data.duration_minutes:
            update_data.duration_minutes = input_data.duration_minutes

        # Check availability if time is being updated
        if input_data.datetime_request or input_data.duration_minutes:
            start_time = input_data.start_time or existing.start_time
            duration = input_data.duration_minutes or existing.duration_minutes
            end_time = start_time + timedelta(minutes=duration)

            is_available = await db.check_availability(
                consultant_id=existing.consultant_id,
                start_time=start_time,
                end_time=end_time,
                exclude_appointment_id=input_data.appointment_id
            )

            if not is_available:
                return {
                    "success": False,
                    "error": "Consulente non disponibile",
                    "message": "Il consulente non è disponibile al nuovo orario richiesto."
                }

        # Update appointment
        appointment = await db.update_appointment(input_data.appointment_id, update_data)

        return {
            "success": True,
            "message": f"Appuntamento {appointment.id} aggiornato con successo",
            "appointment": {
                "id": appointment.id,
                "title": appointment.title,
                "datetime": appointment.start_time.strftime("%d/%m/%Y alle %H:%M"),
                "duration": f"{appointment.duration_minutes} minuti",
                "status": appointment.status
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to update appointment via agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Si è verificato un errore durante l'aggiornamento dell'appuntamento."
        }


async def db_get_consultants(
    ctx: RunContext[ScheduleAgentDependencies],
    business_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of consultants for a business.

    Ottieni l'elenco dei consulenti per un'azienda.
    """
    try:
        db = await ctx.deps.get_db_client()

        consultants = await db.list_consultants(
            business_id=business_id or "default-business",
            is_active=True
        )

        formatted_consultants = []
        for consultant in consultants:
            formatted_consultants.append({
                "id": consultant.id,
                "name": consultant.name,
                "email": consultant.email,
                "specializations": consultant.specializations,
                "business_id": consultant.business_id
            })

        return {
            "success": True,
            "message": f"Trovati {len(formatted_consultants)} consulenti disponibili",
            "consultants": formatted_consultants
        }

    except Exception as e:
        logger.error(f"❌ Failed to get consultants via agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Si è verificato un errore durante il recupero dei consulenti."
        }


# Tool registration function for agent integration
def register_db_tools(agent):
    """Register database tools with the agent."""

    # Note: In a real implementation, you would register these with the Pydantic AI agent
    # This is a placeholder showing how tools would be integrated
    tools_mapping = {
        "db_create_appointment": db_create_appointment,
        "db_check_availability": db_check_availability,
        "db_create_client": db_create_client,
        "db_list_appointments": db_list_appointments,
        "db_update_appointment": db_update_appointment,
        "db_get_consultants": db_get_consultants,
    }

    return tools_mapping