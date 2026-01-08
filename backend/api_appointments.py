"""
Enhanced appointment API endpoints with database integration.

This module provides database-backed endpoints for appointment management,
client management, and consultant management integrated with the main FastAPI app.
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from fastapi import HTTPException, Depends, Query
from pydantic import BaseModel, Field

from .database import DatabaseManager, get_database
from .models import (
    Appointment, Client, Consultant, Business,
    AppointmentStatus, ServiceType,
    AppointmentCreate, AppointmentUpdate, ClientCreate, ClientUpdate,
    AppointmentInDB, ClientInDB, ConsultantInDB, BusinessInDB
)

logger = logging.getLogger(__name__)


# Enhanced Pydantic models for API
class ClientAppointmentRequest(BaseModel):
    """Enhanced appointment request with client creation support."""
    client_name: str = Field(..., min_length=1, max_length=255)
    client_email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    client_phone: Optional[str] = Field(None, max_length=50)
    consultant_id: str = Field(..., min_length=1)
    business_id: str = Field(default="default-business", min_length=1)
    service_type: ServiceType
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    start_time: datetime
    duration_minutes: int = Field(default=30, gt=0, le=480)
    notes: Optional[str] = None

    class Config:
        use_enum_values = True


class AppointmentResponse(BaseModel):
    """Response model for appointment operations."""
    success: bool
    appointment: Optional[AppointmentInDB] = None
    message: str
    timestamp: datetime
    agent_ready: bool = True


class ClientResponse(BaseModel):
    """Response model for client operations."""
    success: bool
    client: Optional[ClientInDB] = None
    message: str
    timestamp: datetime


class AvailabilityResponse(BaseModel):
    """Response model for availability checks."""
    available: bool
    consultant_id: str
    requested_slot: dict
    conflicting_appointments: Optional[List[AppointmentInDB]] = None
    message: str


# Database dependency
async def get_db_manager() -> DatabaseManager:
    """FastAPI dependency for database manager."""
    return await get_database()


# === Appointment Endpoints ===

async def create_appointment_db(
    appointment_data: ClientAppointmentRequest,
    db: DatabaseManager = Depends(get_db_manager)
) -> AppointmentResponse:
    """
    Create a new appointment with database persistence.

    This endpoint creates or updates client information and creates
    a new appointment with full validation and conflict checking.
    """
    logger.info(f"📅 Creating appointment for {appointment_data.client_name}")

    try:
        # Validate consultant exists and is available
        consultant = await db.get_consultant(appointment_data.consultant_id)
        if not consultant:
            raise HTTPException(
                status_code=404,
                detail=f"Consultant not found: {appointment_data.consultant_id}"
            )

        # Validate business exists
        business = await db.get_business(appointment_data.business_id)
        if not business:
            raise HTTPException(
                status_code=404,
                detail=f"Business not found: {appointment_data.business_id}"
            )

        # Calculate end time
        end_time = appointment_data.start_time + timedelta(minutes=appointment_data.duration_minutes)

        # Check availability
        is_available = await db.check_availability(
            consultant_id=appointment_data.consultant_id,
            start_time=appointment_data.start_time,
            end_time=end_time
        )

        if not is_available:
            # Get conflicting appointments for detailed response
            conflicting = await db.list_appointments(
                consultant_id=appointment_data.consultant_id,
                start_date=appointment_data.start_time,
                end_date=end_time,
                status=AppointmentStatus.SCHEDULED,
                limit=10
            )

            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Consultant not available at requested time",
                    "conflicting_appointments": [
                        {
                            "id": apt.id,
                            "start_time": apt.start_time.isoformat(),
                            "end_time": apt.end_time.isoformat(),
                            "title": apt.title
                        } for apt in conflicting
                    ]
                }
            )

        # Create or update client
        client_data = ClientCreate(
            email=appointment_data.client_email,
            name=appointment_data.client_name,
            phone=appointment_data.client_phone
        )
        client = await db.create_client(client_data)

        # Create appointment
        appointment_data_db = AppointmentCreate(
            id=str(uuid.uuid4()),
            business_id=appointment_data.business_id,
            consultant_id=appointment_data.consultant_id,
            client_email=appointment_data.client_email,
            service_type=appointment_data.service_type,
            title=appointment_data.title,
            description=appointment_data.description,
            start_time=appointment_data.start_time,
            duration_minutes=appointment_data.duration_minutes,
            notes=appointment_data.notes,
            client_phone=appointment_data.client_phone
        )

        appointment = await db.create_appointment(appointment_data_db)

        logger.info(f"✅ Appointment created: {appointment.id} for {appointment_data.client_name}")

        return AppointmentResponse(
            success=True,
            appointment=appointment,
            message=f"Appuntamento creato con successo per {appointment_data.client_name}",
            timestamp=datetime.now(),
            agent_ready=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create appointment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create appointment: {str(e)}"
        )


async def get_appointments_db(
    business_id: Optional[str] = Query(None),
    consultant_id: Optional[str] = Query(None),
    client_email: Optional[str] = Query(None),
    status: Optional[AppointmentStatus] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: DatabaseManager = Depends(get_db_manager)
) -> List[AppointmentInDB]:
    """
    Get appointments with optional filtering.

    Supports filtering by business, consultant, client, status, and date range.
    """
    try:
        appointments = await db.list_appointments(
            business_id=business_id,
            consultant_id=consultant_id,
            client_email=client_email,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        logger.info(f"📋 Retrieved {len(appointments)} appointments")
        return appointments

    except Exception as e:
        logger.error(f"❌ Failed to get appointments: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve appointments: {str(e)}"
        )


async def get_appointment_db(
    appointment_id: str,
    db: DatabaseManager = Depends(get_db_manager)
) -> AppointmentInDB:
    """Get a specific appointment by ID."""
    try:
        appointment = await db.get_appointment(appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment not found: {appointment_id}"
            )

        return appointment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve appointment: {str(e)}"
        )


async def update_appointment_db(
    appointment_id: str,
    appointment_data: AppointmentUpdate,
    db: DatabaseManager = Depends(get_db_manager)
) -> AppointmentResponse:
    """Update an existing appointment."""
    try:
        # Check if appointment exists
        existing = await db.get_appointment(appointment_id)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment not found: {appointment_id}"
            )

        # If time is being updated, check availability
        if appointment_data.start_time or appointment_data.duration_minutes:
            # Get current appointment data for availability check
            start_time = appointment_data.start_time or existing.start_time
            duration = appointment_data.duration_minutes or existing.duration_minutes
            end_time = start_time + timedelta(minutes=duration)

            # Check availability (exclude current appointment from conflict check)
            is_available = await db.check_availability(
                consultant_id=existing.consultant_id,
                start_time=start_time,
                end_time=end_time,
                exclude_appointment_id=appointment_id
            )

            if not is_available:
                raise HTTPException(
                    status_code=409,
                    detail="Consultant not available at requested time"
                )

        # Update appointment
        appointment = await db.update_appointment(appointment_id, appointment_data)
        if not appointment:
            raise HTTPException(
                status_code=500,
                detail="Failed to update appointment"
            )

        logger.info(f"✅ Appointment updated: {appointment_id}")

        return AppointmentResponse(
            success=True,
            appointment=appointment,
            message="Appuntamento aggiornato con successo",
            timestamp=datetime.now(),
            agent_ready=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update appointment: {str(e)}"
        )


async def cancel_appointment_db(
    appointment_id: str,
    db: DatabaseManager = Depends(get_db_manager)
) -> AppointmentResponse:
    """Cancel an appointment."""
    try:
        # Update appointment status to cancelled
        cancel_data = AppointmentUpdate(status=AppointmentStatus.CANCELLED)
        appointment = await db.update_appointment(appointment_id, cancel_data)

        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment not found: {appointment_id}"
            )

        logger.info(f"❌ Appointment cancelled: {appointment_id}")

        return AppointmentResponse(
            success=True,
            appointment=appointment,
            message="Appuntamento cancellato con successo",
            timestamp=datetime.now(),
            agent_ready=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to cancel appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel appointment: {str(e)}"
        )


# === Client Endpoints ===

async def create_client_db(
    client_data: ClientCreate,
    db: DatabaseManager = Depends(get_db_manager)
) -> ClientResponse:
    """Create a new client."""
    try:
        client = await db.create_client(client_data)
        logger.info(f"👤 Client created: {client.email}")

        return ClientResponse(
            success=True,
            client=client,
            message=f"Cliente {client.name} creato con successo",
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"❌ Failed to create client: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create client: {str(e)}"
        )


async def get_client_db(
    email: str,
    db: DatabaseManager = Depends(get_db_manager)
) -> ClientInDB:
    """Get a client by email."""
    try:
        client = await db.get_client(email)
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client not found: {email}"
            )

        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get client {email}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve client: {str(e)}"
        )


async def list_clients_db(
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    db: DatabaseManager = Depends(get_db_manager)
) -> List[ClientInDB]:
    """List clients with pagination."""
    try:
        clients = await db.list_clients(limit=limit, offset=offset)
        logger.info(f"👥 Retrieved {len(clients)} clients")
        return clients

    except Exception as e:
        logger.error(f"❌ Failed to list clients: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve clients: {str(e)}"
        )


# === Availability Check ===

async def check_availability_db(
    consultant_id: str,
    start_time: datetime,
    duration_minutes: int = 30,
    db: DatabaseManager = Depends(get_db_manager)
) -> AvailabilityResponse:
    """Check consultant availability for a time slot."""
    try:
        # Validate consultant exists
        consultant = await db.get_consultant(consultant_id)
        if not consultant:
            raise HTTPException(
                status_code=404,
                detail=f"Consultant not found: {consultant_id}"
            )

        # Calculate end time
        end_time = start_time + timedelta(minutes=duration_minutes)

        # Check availability
        is_available = await db.check_availability(
            consultant_id=consultant_id,
            start_time=start_time,
            end_time=end_time
        )

        # Get conflicting appointments if not available
        conflicting_appointments = None
        if not is_available:
            conflicting_appointments = await db.list_appointments(
                consultant_id=consultant_id,
                start_date=start_time,
                end_date=end_time,
                status=AppointmentStatus.SCHEDULED,
                limit=5
            )

        message = (
            f"Consultant {consultant.name} is available at {start_time.strftime('%Y-%m-%d %H:%M')}"
            if is_available
            else f"Consultant {consultant.name} is not available at requested time"
        )

        return AvailabilityResponse(
            available=is_available,
            consultant_id=consultant_id,
            requested_slot={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": duration_minutes
            },
            conflicting_appointments=conflicting_appointments,
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to check availability: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check availability: {str(e)}"
        )


# === Statistics ===

async def get_appointment_stats_db(
    business_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: DatabaseManager = Depends(get_db_manager)
) -> dict:
    """Get appointment statistics for a business."""
    try:
        stats = await db.get_appointment_stats(
            business_id=business_id,
            start_date=start_date,
            end_date=end_date
        )

        logger.info(f"📊 Retrieved stats for business {business_id}")
        return stats

    except Exception as e:
        logger.error(f"❌ Failed to get appointment stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )