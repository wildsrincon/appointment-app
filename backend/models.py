"""
SQLAlchemy database models for ScheduleAI appointment management.

This module defines the ORM models for appointments, clients, and related entities
using SQLAlchemy with async support for PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import (
    Column, String, Integer, DateTime, Text, Boolean,
    ForeignKey, Index, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from pydantic import BaseModel, Field, field_validator

Base = declarative_base()


class AppointmentStatus(str, Enum):
    """Appointment status enumeration."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class ServiceType(str, Enum):
    """Standard service types for Italian appointment scheduling."""
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    TREATMENT = "treatment"
    CHECKUP = "checkup"
    EMERGENCY = "emergency"
    OTHER = "other"


class Client(Base):
    """Client model representing appointment customers."""
    __tablename__ = "clients"

    email = Column(String(255), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(email='{self.email}', name='{self.name}')>"


class Consultant(Base):
    """Consultant model representing service providers."""
    __tablename__ = "consultants"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    specializations = Column(Text, nullable=True)  # JSON string of specializations
    business_id = Column(String(100), nullable=False, index=True)
    calendar_id = Column(String(255), nullable=True)  # Google Calendar ID
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="consultant", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Consultant(id='{self.id}', name='{self.name}')>"


class Business(Base):
    """Business model representing different business entities."""
    __tablename__ = "businesses"

    id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    timezone = Column(String(50), default="Europe/Rome", nullable=False)
    business_hours_start = Column(String(10), default="09:00", nullable=False)  # HH:MM format
    business_hours_end = Column(String(10), default="18:00", nullable=False)    # HH:MM format
    working_days = Column(String(20), default="1,2,3,4,5", nullable=False)     # Comma-separated days
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    consultants = relationship("Consultant", back_populates="business", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="business", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Business(id='{self.id}', name='{self.name}')>"


# Update relationships
Consultant.business = relationship("Business", back_populates="consultants")


class Appointment(Base):
    """Appointment model representing scheduled appointments."""
    __tablename__ = "appointments"

    id = Column(String(100), primary_key=True, index=True)
    business_id = Column(String(100), ForeignKey("businesses.id"), nullable=False, index=True)
    consultant_id = Column(String(100), ForeignKey("consultants.id"), nullable=False, index=True)
    client_email = Column(String(255), ForeignKey("clients.email"), nullable=False, index=True)

    # Appointment details
    service_type = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False)

    # Status and tracking
    status = Column(String(20), default=AppointmentStatus.SCHEDULED, nullable=False, index=True)
    calendar_event_id = Column(String(255), nullable=True, index=True)  # Google Calendar event ID
    meeting_link = Column(String(500), nullable=True)  # Google Meet/Zoom link

    # Additional information
    notes = Column(Text, nullable=True)
    client_phone = Column(String(50), nullable=True)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    follow_up_required = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("Client", back_populates="appointments")
    consultant = relationship("Consultant", back_populates="appointments")
    business = relationship("Business", back_populates="appointments")

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_appointment_business_time', 'business_id', 'start_time'),
        Index('idx_appointment_consultant_time', 'consultant_id', 'start_time'),
        Index('idx_appointment_client_time', 'client_email', 'start_time'),
        Index('idx_appointment_status_time', 'status', 'start_time'),
    )

    def __repr__(self):
        return f"<Appointment(id='{self.id}', title='{self.title}', start_time='{self.start_time}')>"


# Pydantic models for API serialization
class ClientBase(BaseModel):
    """Base Pydantic model for Client."""
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    """Pydantic model for creating a Client."""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class ClientUpdate(BaseModel):
    """Pydantic model for updating a Client."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class ClientInDB(ClientBase):
    """Pydantic model for Client as stored in database."""
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConsultantBase(BaseModel):
    """Base Pydantic model for Consultant."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = Field(None, max_length=50)
    specializations: Optional[str] = None
    business_id: str = Field(..., min_length=1)
    calendar_id: Optional[str] = None


class ConsultantCreate(ConsultantBase):
    """Pydantic model for creating a Consultant."""
    id: str = Field(..., min_length=1, max_length=100)


class ConsultantUpdate(BaseModel):
    """Pydantic model for updating a Consultant."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    phone: Optional[str] = Field(None, max_length=50)
    specializations: Optional[str] = None
    calendar_id: Optional[str] = None
    is_active: Optional[bool] = None


class ConsultantInDB(ConsultantBase):
    """Pydantic model for Consultant as stored in database."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessBase(BaseModel):
    """Base Pydantic model for Business."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    timezone: str = Field(default="Europe/Rome", max_length=50)
    business_hours_start: str = Field(default="09:00", pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    business_hours_end: str = Field(default="18:00", pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    working_days: str = Field(default="1,2,3,4,5", max_length=20)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class BusinessCreate(BusinessBase):
    """Pydantic model for creating a Business."""
    id: str = Field(..., min_length=1, max_length=100)


class BusinessUpdate(BaseModel):
    """Pydantic model for updating a Business."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    timezone: Optional[str] = Field(None, max_length=50)
    business_hours_start: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    business_hours_end: Optional[str] = Field(None, pattern=r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    working_days: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    is_active: Optional[bool] = None


class BusinessInDB(BusinessBase):
    """Pydantic model for Business as stored in database."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    """Base Pydantic model for Appointment."""
    business_id: str = Field(..., min_length=1)
    consultant_id: str = Field(..., min_length=1)
    client_email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    service_type: ServiceType
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    start_time: datetime
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours
    notes: Optional[str] = None
    client_phone: Optional[str] = Field(None, max_length=50)

    class Config:
        use_enum_values = True


class AppointmentCreate(AppointmentBase):
    """Pydantic model for creating an Appointment."""
    id: str = Field(..., min_length=1, max_length=100)


class AppointmentUpdate(BaseModel):
    """Pydantic model for updating an Appointment."""
    service_type: Optional[ServiceType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0, le=480)
    status: Optional[AppointmentStatus] = None
    calendar_event_id: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    client_phone: Optional[str] = Field(None, max_length=50)
    reminder_sent: Optional[bool] = None
    follow_up_required: Optional[bool] = None

    class Config:
        use_enum_values = True


class AppointmentInDB(AppointmentBase):
    """Pydantic model for Appointment as stored in database."""
    id: str
    end_time: datetime
    status: AppointmentStatus
    calendar_event_id: Optional[str]
    meeting_link: Optional[str]
    reminder_sent: bool
    follow_up_required: bool
    created_at: datetime
    updated_at: datetime

    # Optional relationships
    client: Optional[ClientInDB] = None
    consultant: Optional[ConsultantInDB] = None
    business: Optional[BusinessInDB] = None

    class Config:
        from_attributes = True
        use_enum_values = True


# Add missing import for timedelta
from datetime import timedelta