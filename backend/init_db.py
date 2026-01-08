#!/usr/bin/env python3
"""
Database initialization script for ScheduleAI.

This script creates the database schema, sets up initial data,
and handles database migrations using Alembic.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database import DatabaseManager
from models import BusinessCreate, ConsultantCreate, ClientCreate
from settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize the database with schema and sample data."""
    logger.info("🚀 Initializing ScheduleAI database...")

    try:
        # Get settings and create database manager
        settings = get_settings()
        db = DatabaseManager()

        # Initialize database schema
        logger.info("📋 Creating database tables...")
        await db.initialize()

        # Create sample business if none exists
        logger.info("🏢 Creating sample business...")
        business_data = BusinessCreate(
            id="default-business",
            name="Studio Medico意大利",
            description="Studio medico polispecialistico con servizi di consulenza",
            timezone="Europe/Rome",
            business_hours_start="09:00",
            business_hours_end="18:00",
            working_days="1,2,3,4,5",  # Monday to Friday
            address="Via Roma 123, 00100 Roma, Italia",
            phone="+39 06 1234567",
            email="info@studiomedico.it"
        )

        business = await db.create_business(business_data)
        logger.info(f"✅ Created business: {business.name}")

        # Create sample consultants
        logger.info("👥 Creating sample consultants...")
        consultants_data = [
            ConsultantCreate(
                id="dr-rossi",
                name="Dott. Rossi Mario",
                email="m.rossi@studiomedico.it",
                phone="+39 06 1234568",
                specializations='["Medicina Generale", "Cardiologia"]',
                business_id="default-business",
                calendar_id="primary"
            ),
            ConsultantCreate(
                id="dr-bianchi",
                name="Dott.ssa Bianchi Laura",
                email="l.bianchi@studiomedico.it",
                phone="+39 06 1234569",
                specializations='["Dermatologia", "Medicina Estetica"]',
                business_id="default-business",
                calendar_id="primary"
            ),
            ConsultantCreate(
                id="dr-verdi",
                name="Dott. Verdi Giuseppe",
                email="g.verdi@studiomedico.it",
                phone="+39 06 1234570",
                specializations='["Ortopedia", "Fisioterapia"]',
                business_id="default-business",
                calendar_id="primary"
            )
        ]

        for consultant_data in consultants_data:
            consultant = await db.create_consultant(consultant_data)
            logger.info(f"✅ Created consultant: {consultant.name}")

        # Create sample clients
        logger.info("👤 Creating sample clients...")
        clients_data = [
            ClientCreate(
                email="marco.rossi@email.com",
                name="Marco Rossi",
                phone="+39 333 1234567",
                notes="Paziente abituale, preferisce appuntamenti mattutini"
            ),
            ClientCreate(
                email="laura.bianchi@email.com",
                name="Laura Bianchi",
                phone="+39 333 2345678",
                notes="Nuova paziente, segnalata dal Dott. Rossi"
            ),
            ClientCreate(
                email="giuseppe.verdi@email.com",
                name="Giuseppe Verdi",
                phone="+39 333 3456789",
                notes="Paziente pediatrico, richiede visita con Dott.ssa Bianchi"
            )
        ]

        for client_data in clients_data:
            client = await db.create_client(client_data)
            logger.info(f"✅ Created client: {client.name}")

        # Close database connection
        await db.close()

        logger.info("🎉 Database initialization completed successfully!")
        logger.info("📊 Sample data created:")
        logger.info(f"   - 1 Business: {business.name}")
        logger.info(f"   - 3 Consultants: {[c.name for c in consultants_data]}")
        logger.info(f"   - 3 Clients: {[c.name for c in clients_data]}")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def reset_database():
    """Reset the database by dropping and recreating all tables."""
    logger.warning("⚠️ Resetting database - all data will be lost!")

    try:
        db = DatabaseManager()

        # Drop all tables
        logger.info("🗑️ Dropping all tables...")
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        # Recreate tables
        logger.info("📋 Recreating tables...")
        await db.initialize()

        # Create sample data
        await init_database()

        await db.close()

    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise


async def check_database():
    """Check database connection and schema."""
    logger.info("🔍 Checking database connection...")

    try:
        db = DatabaseManager()

        # Test connection
        async with db.get_session() as session:
            result = await session.execute("SELECT 1 as test")
            test_value = result.scalar()

            if test_value == 1:
                logger.info("✅ Database connection successful")
            else:
                raise Exception("Database connection test failed")

        # Check if tables exist
        logger.info("📋 Checking database schema...")
        async with db.engine.begin() as conn:
            tables = await conn.run_sync(
                lambda sync_conn: sync_conn.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                ).fetchall()
            )

        table_names = [table[0] for table in tables]
        expected_tables = ['businesses', 'consultants', 'clients', 'appointments']

        missing_tables = [table for table in expected_tables if table not in table_names]
        if missing_tables:
            logger.warning(f"⚠️ Missing tables: {missing_tables}")
        else:
            logger.info("✅ All required tables exist")

        await db.close()
        logger.info("✅ Database check completed")

    except Exception as e:
        logger.error(f"❌ Database check failed: {e}")
        raise


def print_usage():
    """Print usage instructions."""
    print("""
Usage: python init_db.py [command]

Commands:
    init     Initialize database with schema and sample data
    reset    Reset database (drop and recreate all tables)
    check    Check database connection and schema

Examples:
    python init_db.py init
    python init_db.py check
    python init_db.py reset
    """)


async def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "init":
        await init_database()
    elif command == "reset":
        await reset_database()
    elif command == "check":
        await check_database()
    else:
        logger.error(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    # Import Base after adding to path
    from models import Base

    asyncio.run(main())