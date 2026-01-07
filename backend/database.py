"""
Database manager for ScheduleAI using PostgreSQL with SQLAlchemy.

This module provides async database operations for appointments, clients,
consultants, and businesses using SQLAlchemy ORM with PostgreSQL backend.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

# Handle both relative and absolute imports
try:
    from .models import (
        Base, Appointment, Client, Consultant, Business,
        AppointmentStatus, ServiceType,
        AppointmentCreate, AppointmentUpdate, ClientCreate, ClientUpdate,
        ConsultantCreate, ConsultantUpdate, BusinessCreate, BusinessUpdate,
        AppointmentInDB, ClientInDB, ConsultantInDB, BusinessInDB
    )
    from .settings import get_settings
except ImportError:
    try:
        from models import (
            Base, Appointment, Client, Consultant, Business,
            AppointmentStatus, ServiceType,
            AppointmentCreate, AppointmentUpdate, ClientCreate, ClientUpdate,
            ConsultantCreate, ConsultantUpdate, BusinessCreate, BusinessUpdate,
            AppointmentInDB, ClientInDB, ConsultantInDB, BusinessInDB
        )
        from settings import get_settings
    except ImportError:
        # Try adding current directory to path
        import os
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        from models import (
            Base, Appointment, Client, Consultant, Business,
            AppointmentStatus, ServiceType,
            AppointmentCreate, AppointmentUpdate, ClientCreate, ClientUpdate,
            ConsultantCreate, ConsultantUpdate, BusinessCreate, BusinessUpdate,
            AppointmentInDB, ClientInDB, ConsultantInDB, BusinessInDB
        )
        from settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Async database manager for ScheduleAI using PostgreSQL.

    Provides high-level database operations with proper error handling
    and connection management.
    """

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database manager.

        Args:
            database_url: PostgreSQL connection URL. If None, loads from settings.
        """
        self.settings = get_settings()
        self.database_url = database_url or self._get_database_url()

        # Create async engine and session
        self.engine = create_async_engine(
            self.database_url,
            echo=self.settings.debug,
            future=True,
            pool_pre_ping=True,
            pool_recycle=300,
        )

        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info(f"Database manager initialized with URL: {self.database_url.split('@')[1] if '@' in self.database_url else 'local'}")

    def _get_database_url(self) -> str:
        """
        Construct database URL from environment variables.

        Returns:
            PostgreSQL connection URL
        """
        # Default to environment variables or localhost
        db_user = getattr(self.settings, 'db_user', 'postgres')
        db_password = getattr(self.settings, 'db_password', 'password')
        db_host = getattr(self.settings, 'db_host', 'localhost')
        db_port = getattr(self.settings, 'db_port', '5432')
        db_name = getattr(self.settings, 'db_name', 'scheduleai')

        return f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    async def initialize(self) -> None:
        """Create database tables if they don't exist."""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database tables: {e}")
            raise

    async def close(self) -> None:
        """Close the database connection."""
        await self.engine.dispose()
        logger.info("Database connections closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """
        Context manager for database sessions.

        Yields:
            AsyncSession: Database session
        """
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()

    # === Client Operations ===

    async def create_client(self, client_data: ClientCreate) -> ClientInDB:
        """
        Create a new client.

        Args:
            client_data: Client creation data

        Returns:
            Created client
        """
        async with self.get_session() as session:
            # Check if client already exists
            existing = await session.get(Client, client_data.email)
            if existing:
                logger.info(f"Client already exists: {client_data.email}")
                return ClientInDB.from_orm(existing)

            client = Client(**client_data.dict())
            session.add(client)
            await session.flush()  # Get the ID without committing
            await session.refresh(client)

            logger.info(f"Created client: {client.email}")
            return ClientInDB.from_orm(client)

    async def get_client(self, email: str) -> Optional[ClientInDB]:
        """
        Get a client by email.

        Args:
            email: Client email

        Returns:
            Client if found, None otherwise
        """
        async with self.get_session() as session:
            result = await session.execute(select(Client).where(Client.email == email))
            client = result.scalar_one_or_none()

            if client:
                return ClientInDB.from_orm(client)
            return None

    async def update_client(self, email: str, client_data: ClientUpdate) -> Optional[ClientInDB]:
        """
        Update a client.

        Args:
            email: Client email
            client_data: Update data

        Returns:
            Updated client if found, None otherwise
        """
        async with self.get_session() as session:
            client = await session.get(Client, email)
            if not client:
                return None

            # Update fields
            update_data = client_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(client, field, value)

            client.updated_at = datetime.utcnow()
            await session.flush()
            await session.refresh(client)

            logger.info(f"Updated client: {email}")
            return ClientInDB.from_orm(client)

    async def list_clients(self, limit: int = 100, offset: int = 0) -> List[ClientInDB]:
        """
        List clients with pagination.

        Args:
            limit: Maximum number of clients to return
            offset: Number of clients to skip

        Returns:
            List of clients
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Client)
                .order_by(Client.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            clients = result.scalars().all()

            return [ClientInDB.from_orm(client) for client in clients]

    # === Consultant Operations ===

    async def create_consultant(self, consultant_data: ConsultantCreate) -> ConsultantInDB:
        """
        Create a new consultant.

        Args:
            consultant_data: Consultant creation data

        Returns:
            Created consultant
        """
        async with self.get_session() as session:
            # Check if consultant already exists
            existing = await session.get(Consultant, consultant_data.id)
            if existing:
                logger.info(f"Consultant already exists: {consultant_data.id}")
                return ConsultantInDB.from_orm(existing)

            consultant = Consultant(**consultant_data.dict())
            session.add(consultant)
            await session.flush()
            await session.refresh(consultant)

            logger.info(f"Created consultant: {consultant.id}")
            return ConsultantInDB.from_orm(consultant)

    async def get_consultant(self, consultant_id: str) -> Optional[ConsultantInDB]:
        """
        Get a consultant by ID.

        Args:
            consultant_id: Consultant ID

        Returns:
            Consultant if found, None otherwise
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Consultant)
                .options(selectinload(Consultant.business))
                .where(Consultant.id == consultant_id)
            )
            consultant = result.scalar_one_or_none()

            if consultant:
                return ConsultantInDB.from_orm(consultant)
            return None

    async def list_consultants(
        self,
        business_id: Optional[str] = None,
        is_active: bool = True,
        limit: int = 100
    ) -> List[ConsultantInDB]:
        """
        List consultants with optional filtering.

        Args:
            business_id: Filter by business ID
            is_active: Filter by active status
            limit: Maximum number of consultants to return

        Returns:
            List of consultants
        """
        async with self.get_session() as session:
            query = select(Consultant).where(Consultant.is_active == is_active)

            if business_id:
                query = query.where(Consultant.business_id == business_id)

            query = query.order_by(Consultant.name).limit(limit)

            result = await session.execute(query)
            consultants = result.scalars().all()

            return [ConsultantInDB.from_orm(consultant) for consultant in consultants]

    # === Business Operations ===

    async def create_business(self, business_data: BusinessCreate) -> BusinessInDB:
        """
        Create a new business.

        Args:
            business_data: Business creation data

        Returns:
            Created business
        """
        async with self.get_session() as session:
            # Check if business already exists
            existing = await session.get(Business, business_data.id)
            if existing:
                logger.info(f"Business already exists: {business_data.id}")
                return BusinessInDB.from_orm(existing)

            business = Business(**business_data.dict())
            session.add(business)
            await session.flush()
            await session.refresh(business)

            logger.info(f"Created business: {business.id}")
            return BusinessInDB.from_orm(business)

    async def get_business(self, business_id: str) -> Optional[BusinessInDB]:
        """
        Get a business by ID.

        Args:
            business_id: Business ID

        Returns:
            Business if found, None otherwise
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Business).where(Business.id == business_id)
            )
            business = result.scalar_one_or_none()

            if business:
                return BusinessInDB.from_orm(business)
            return None

    # === Appointment Operations ===

    async def create_appointment(self, appointment_data: AppointmentCreate) -> AppointmentInDB:
        """
        Create a new appointment.

        Args:
            appointment_data: Appointment creation data

        Returns:
            Created appointment
        """
        async with self.get_session() as session:
            # Calculate end time
            end_time = appointment_data.start_time + timedelta(minutes=appointment_data.duration_minutes)

            appointment = Appointment(
                id=appointment_data.id,
                business_id=appointment_data.business_id,
                consultant_id=appointment_data.consultant_id,
                client_email=appointment_data.client_email,
                service_type=appointment_data.service_type,
                title=appointment_data.title,
                description=appointment_data.description,
                start_time=appointment_data.start_time,
                end_time=end_time,
                duration_minutes=appointment_data.duration_minutes,
                notes=appointment_data.notes,
                client_phone=appointment_data.client_phone,
                status=AppointmentStatus.SCHEDULED
            )

            session.add(appointment)
            await session.flush()
            await session.refresh(appointment)

            # Load relationships
            await session.refresh(appointment, ["client", "consultant", "business"])

            logger.info(f"Created appointment: {appointment.id}")
            return AppointmentInDB.from_orm(appointment)

    async def get_appointment(self, appointment_id: str) -> Optional[AppointmentInDB]:
        """
        Get an appointment by ID.

        Args:
            appointment_id: Appointment ID

        Returns:
            Appointment if found, None otherwise
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Appointment)
                .options(
                    selectinload(Appointment.client),
                    selectinload(Appointment.consultant),
                    selectinload(Appointment.business)
                )
                .where(Appointment.id == appointment_id)
            )
            appointment = result.scalar_one_or_none()

            if appointment:
                return AppointmentInDB.from_orm(appointment)
            return None

    async def update_appointment(
        self,
        appointment_id: str,
        appointment_data: AppointmentUpdate
    ) -> Optional[AppointmentInDB]:
        """
        Update an appointment.

        Args:
            appointment_id: Appointment ID
            appointment_data: Update data

        Returns:
            Updated appointment if found, None otherwise
        """
        async with self.get_session() as session:
            appointment = await session.get(Appointment, appointment_id)
            if not appointment:
                return None

            # Update fields
            update_data = appointment_data.dict(exclude_unset=True)

            # Handle duration update
            if 'duration_minutes' in update_data:
                appointment.duration_minutes = update_data['duration_minutes']
                if 'start_time' in update_data:
                    appointment.start_time = update_data['start_time']
                appointment.end_time = appointment.start_time + timedelta(minutes=appointment.duration_minutes)

            # Update other fields
            for field, value in update_data.items():
                if field not in ['duration_minutes']:
                    setattr(appointment, field, value)

            appointment.updated_at = datetime.utcnow()
            await session.flush()
            await session.refresh(appointment)

            # Load relationships
            await session.refresh(appointment, ["client", "consultant", "business"])

            logger.info(f"Updated appointment: {appointment_id}")
            return AppointmentInDB.from_orm(appointment)

    async def list_appointments(
        self,
        business_id: Optional[str] = None,
        consultant_id: Optional[str] = None,
        client_email: Optional[str] = None,
        status: Optional[AppointmentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AppointmentInDB]:
        """
        List appointments with optional filtering.

        Args:
            business_id: Filter by business ID
            consultant_id: Filter by consultant ID
            client_email: Filter by client email
            status: Filter by status
            start_date: Filter appointments from this date
            end_date: Filter appointments until this date
            limit: Maximum number of appointments to return
            offset: Number of appointments to skip

        Returns:
            List of appointments
        """
        async with self.get_session() as session:
            query = select(Appointment).options(
                selectinload(Appointment.client),
                selectinload(Appointment.consultant),
                selectinload(Appointment.business)
            )

            # Apply filters
            if business_id:
                query = query.where(Appointment.business_id == business_id)
            if consultant_id:
                query = query.where(Appointment.consultant_id == consultant_id)
            if client_email:
                query = query.where(Appointment.client_email == client_email)
            if status:
                query = query.where(Appointment.status == status)
            if start_date:
                query = query.where(Appointment.start_time >= start_date)
            if end_date:
                query = query.where(Appointment.start_time <= end_date)

            query = query.order_by(Appointment.start_time.desc()).limit(limit).offset(offset)

            result = await session.execute(query)
            appointments = result.scalars().all()

            return [AppointmentInDB.from_orm(appointment) for appointment in appointments]

    async def check_availability(
        self,
        consultant_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_appointment_id: Optional[str] = None
    ) -> bool:
        """
        Check if a consultant is available during a time slot.

        Args:
            consultant_id: Consultant ID
            start_time: Start time of the proposed appointment
            end_time: End time of the proposed appointment
            exclude_appointment_id: Exclude this appointment from conflict check

        Returns:
            True if available, False if conflicted
        """
        async with self.get_session() as session:
            query = select(Appointment).where(
                and_(
                    Appointment.consultant_id == consultant_id,
                    Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
                    or_(
                        and_(Appointment.start_time <= start_time, Appointment.end_time > start_time),
                        and_(Appointment.start_time < end_time, Appointment.end_time >= end_time),
                        and_(Appointment.start_time >= start_time, Appointment.end_time <= end_time)
                    )
                )
            )

            if exclude_appointment_id:
                query = query.where(Appointment.id != exclude_appointment_id)

            result = await session.execute(query)
            conflicting_appointments = result.scalars().all()

            return len(conflicting_appointments) == 0

    async def delete_appointment(self, appointment_id: str) -> bool:
        """
        Delete an appointment.

        Args:
            appointment_id: Appointment ID

        Returns:
            True if deleted, False if not found
        """
        async with self.get_session() as session:
            appointment = await session.get(Appointment, appointment_id)
            if not appointment:
                return False

            await session.delete(appointment)
            logger.info(f"Deleted appointment: {appointment_id}")
            return True

    # === Analytics and Reports ===

    async def get_appointment_stats(
        self,
        business_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get appointment statistics for a business.

        Args:
            business_id: Business ID
            start_date: Start date for stats
            end_date: End date for stats

        Returns:
            Dictionary with appointment statistics
        """
        async with self.get_session() as session:
            # Base query
            query = select(func.count(Appointment.id)).where(Appointment.business_id == business_id)

            if start_date:
                query = query.where(Appointment.start_time >= start_date)
            if end_date:
                query = query.where(Appointment.start_time <= end_date)

            # Total appointments
            result = await session.execute(query)
            total_appointments = result.scalar()

            # Appointments by status
            status_query = select(
                Appointment.status,
                func.count(Appointment.id)
            ).where(Appointment.business_id == business_id)

            if start_date:
                status_query = status_query.where(Appointment.start_time >= start_date)
            if end_date:
                status_query = status_query.where(Appointment.start_time <= end_date)

            status_query = status_query.group_by(Appointment.status)

            result = await session.execute(status_query)
            status_counts = dict(result.all())

            return {
                "total_appointments": total_appointments,
                "by_status": status_counts,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }


# Global database instance
_database_manager: Optional[DatabaseManager] = None


async def get_database() -> DatabaseManager:
    """
    Get the global database manager instance.

    Returns:
        DatabaseManager instance
    """
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
        await _database_manager.initialize()
    return _database_manager


async def close_database() -> None:
    """Close the global database manager."""
    global _database_manager
    if _database_manager is not None:
        await _database_manager.close()
        _database_manager = None