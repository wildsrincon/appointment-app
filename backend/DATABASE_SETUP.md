# Database Setup Guide for ScheduleAI

This guide explains how to set up and configure the PostgreSQL database for the ScheduleAI appointment management system.

## 📋 Overview

The ScheduleAI backend now includes a complete database implementation using:
- **PostgreSQL** as the primary database
- **SQLAlchemy** ORM with async support
- **Alembic** for database migrations
- **Pydantic** models for API validation

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install database dependencies
pip install -r requirements.txt
```

### 2. Set up PostgreSQL Database

#### Option A: Local PostgreSQL
```bash
# Create database
createdb scheduleai

# Create user (optional)
createuser -P scheduleai_user
```

#### Option B: Docker PostgreSQL
```bash
docker run --name scheduleai-db \
  -e POSTGRES_DB=scheduleai \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:15
```

#### Option C: Cloud PostgreSQL (Recommended for Production)
- **Railway**: Add PostgreSQL service
- **Supabase**: Create new project
- **Neon**: Create new database
- **AWS RDS**: Set up PostgreSQL instance

### 3. Configure Environment Variables

Update your `.env` file:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=scheduleai
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_SSL_MODE=prefer

# Or use full connection URL
# DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

### 4. Initialize Database

```bash
# Run database initialization
python init_db.py init

# Check database connection
python init_db.py check

# Reset database (if needed)
python init_db.py reset
```

## 🗄️ Database Schema

### Tables Overview

1. **Businesses** - Business/clinic information
2. **Consultants** - Service providers/doctors
3. **Clients** - Customer information
4. **Appointments** - Scheduled appointments with relationships

### Schema Details

#### `businesses`
- `id` (string, primary key) - Business identifier
- `name` (string) - Business name
- `timezone` (string) - Business timezone
- `business_hours_start/end` (time) - Operating hours
- `working_days` (string) - Comma-separated working days
- `address`, `phone`, `email` - Contact information

#### `consultants`
- `id` (string, primary key) - Consultant identifier
- `name` (string) - Consultant name
- `email`, `phone` - Contact information
- `specializations` (text) - JSON array of specializations
- `business_id` (foreign key) - Associated business
- `calendar_id` (string) - Google Calendar ID
- `is_active` (boolean) - Active status

#### `clients`
- `email` (string, primary key) - Client email
- `name` (string) - Client name
- `phone` (string) - Phone number
- `notes` (text) - Additional notes

#### `appointments`
- `id` (string, primary key) - Appointment identifier
- `business_id`, `consultant_id`, `client_email` (foreign keys)
- `service_type` (enum) - Type of service
- `title`, `description` (text) - Appointment details
- `start_time`, `end_time` (datetime) - Appointment time
- `duration_minutes` (integer) - Duration in minutes
- `status` (enum) - Appointment status
- `calendar_event_id` (string) - Google Calendar event ID
- `meeting_link` (string) - Video meeting link
- `notes` (text) - Additional notes

## 🔧 API Endpoints

### Database-Enhanced Endpoints

All new endpoints have `/db` suffix to distinguish from mock endpoints:

#### Appointments
- `POST /appointments/db` - Create appointment with full validation
- `GET /appointments/db` - List appointments with filtering
- `GET /appointments/db/{id}` - Get specific appointment
- `PUT /appointments/db/{id}` - Update appointment
- `POST /appointments/db/{id}/cancel` - Cancel appointment
- `GET /appointments/db/stats/{business_id}` - Get statistics

#### Clients
- `POST /clients/db` - Create client
- `GET /clients/db` - List clients with pagination
- `GET /clients/db/{email}` - Get specific client

#### Availability
- `GET /availability/db` - Check consultant availability

### Example API Usage

#### Create Appointment
```bash
curl -X POST "http://localhost:8000/appointments/db" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "Marco Rossi",
    "client_email": "marco@email.com",
    "client_phone": "+39 333 1234567",
    "consultant_id": "dr-rossi",
    "service_type": "consultation",
    "title": "Visita di controllo",
    "start_time": "2024-12-15T10:00:00",
    "duration_minutes": 30
  }'
```

#### Check Availability
```bash
curl -X GET "http://localhost:8000/availability/db?consultant_id=dr-rossi&start_time=2024-12-15T10:00:00&duration_minutes=30"
```

#### List Appointments
```bash
curl -X GET "http://localhost:8000/appointments/db?consultant_id=dr-rossi&start_date=2024-12-01&end_date=2024-12-31"
```

## 🔌 Database Integration with Agent

The AI agent now has database-integrated tools available in `db_tools.py`:

### Available Agent Tools
- `db_create_appointment` - Create appointments with validation
- `db_check_availability` - Check real-time availability
- `db_create_client` - Create or update clients
- `db_list_appointments` - Query appointments with filters
- `db_update_appointment` - Modify existing appointments
- `db_get_consultants` - Get available consultants

### Agent Integration Example
```python
# In agent.py, import database tools
from db_tools import (
    db_create_appointment,
    db_check_availability,
    db_get_consultants
)

# Register tools with the Pydantic AI agent
@agent.tool
async def create_appointment_db(ctx: RunContext[Dependencies], data: dict):
    """Create appointment using database."""
    input_data = CreateAppointmentInput(**data)
    return await db_create_appointment(ctx, input_data)
```

## 🚀 Deployment

### Railway Setup
1. Add PostgreSQL service in Railway
2. Set environment variables:
   - `DB_HOST` (provided by Railway)
   - `DB_PORT` (provided by Railway)
   - `DB_NAME` (provided by Railway)
   - `DB_USER` (provided by Railway)
   - `DB_PASSWORD` (provided by Railway)
3. Update `railway.toml` if needed
4. Deploy - the database will be initialized automatically

### Environment Variables for Production
```env
# Production Database (Railway example)
DATABASE_URL=postgresql+asyncpg://postgres:password@containers-us-west-xxx.railway.app:7923/railway

# Or individual components
DB_HOST=containers-us-west-xxx.railway.app
DB_PORT=7923
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=your_railway_password
```

## 🔄 Database Migrations

### Creating New Migrations
```bash
# Generate migration file
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Migration Scripts
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply all migrations
alembic upgrade head
```

## 📊 Monitoring and Analytics

### Database Health Checks
- `GET /health` - Overall service health
- Database connection status included in health check
- Automatic retry logic for failed connections

### Statistics and Reports
- Appointment volume by status
- Consultant utilization metrics
- Client appointment history
- Business performance analytics

## 🛠️ Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check database connection
python init_db.py check

# Verify environment variables
echo $DATABASE_URL
```

#### Migration Issues
```bash
# Reset database
python init_db.py reset

# Manual migration
alembic upgrade head
```

#### Performance Issues
- Check database indexes in models.py
- Monitor query performance with logging
- Consider connection pooling for high traffic

### Logs and Debugging
```python
# Enable debug logging in settings
DEBUG=true

# Database query logging
# Set in settings.py or environment variable
ECHO=true
```

## 🔒 Security Considerations

- Use environment variables for credentials
- Enable SSL for production databases
- Implement connection pooling
- Regular database backups
- Role-based access control

## 📈 Scaling

### Database Scaling
- Read replicas for reporting
- Connection pooling (PgBouncer)
- Database partitioning for large datasets
- Caching layer (Redis) for frequent queries

### API Scaling
- Pagination for large result sets
- Async database operations
- Background task processing for notifications
- Database connection management

## 📝 Next Steps

1. **Set up production database** (Railway/Supabase/Neon)
2. **Run initialization script** to create sample data
3. **Test API endpoints** with your frontend
4. **Configure monitoring** and alerts
5. **Set up regular backups** and maintenance

## 🆘 Support

If you encounter issues:
1. Check logs for error messages
2. Verify database connection with `python init_db.py check`
3. Ensure all environment variables are set correctly
4. Review the troubleshooting section above