# Dependency Configuration - Italian Appointment Scheduling AI Agent

## Configuration Philosophy
Simple, minimal configuration for MVP deployment with essential environment variables only. Focus on single model provider and basic dependencies.

## Environment Variables (.env)

### Core LLM Configuration
```bash
# OpenAI Configuration (REQUIRED)
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1

# Google Calendar Integration (REQUIRED)
GOOGLE_CALENDAR_API_KEY=your-google-calendar-api-key
GOOGLE_CALENDAR_CLIENT_ID=your-google-client-id
GOOGLE_CALENDAR_CLIENT_SECRET=your-google-client-secret
GOOGLE_CALENDAR_REFRESH_TOKEN=your-refresh-token

# Business Configuration (REQUIRED)
DEFAULT_TIMEZONE=Europe/Rome
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=18:00
WORKING_DAYS=1,2,3,4,5

# Application Settings
APP_ENV=development
DEBUG=false
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

## Dataclass Dependencies

```python
@dataclass
class ScheduleAgentDependencies:
    """Minimal dependencies for appointment scheduling agent."""

    # API Credentials
    openai_api_key: str
    google_calendar_config: dict

    # Business Configuration
    timezone: str = "Europe/Rome"
    business_hours: tuple = (9, 18)
    working_days: tuple = (1, 2, 3, 4, 5)

    # Runtime Context
    session_id: Optional[str] = None
    business_id: Optional[str] = None

    # External Clients (initialized lazily)
    _google_client: Optional[Any] = field(default=None, init=False, repr=False)
    _db_client: Optional[Any] = field(default=None, init=False, repr=False)
```

## Model Provider Configuration

### Single Provider Setup (OpenAI)
```python
def get_llm_model():
    """Get configured OpenAI model."""
    settings = load_settings()
    provider = OpenAIProvider(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key
    )
    return OpenAIModel(settings.llm_model, provider=provider)
```

## Google Calendar API Setup

### OAuth 2.0 Configuration
```python
@dataclass
class GoogleCalendarConfig:
    """Google Calendar API configuration."""
    api_key: str
    client_id: str
    client_secret: str
    refresh_token: str

    def get_credentials(self):
        """Create OAuth2 credentials for Google Calendar."""
        from google.oauth2.credentials import Credentials
        return Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
```

### Calendar Service Client
```python
async def get_calendar_client(config: GoogleCalendarConfig):
    """Initialize Google Calendar service client."""
    from googleapiclient.discovery import build

    credentials = config.get_credentials()
    service = build('calendar', 'v3', credentials=credentials)
    return service
```

## Multi-Business Configuration

### Business Profile Structure
```python
@dataclass
class BusinessProfile:
    """Multi-business configuration profile."""
    business_id: str
    name: str
    timezone: str
    business_hours: tuple
    working_days: tuple
    calendar_ids: dict  # consultant_id -> calendar_id
    service_types: dict  # service_name -> duration_minutes
```

### Business Configuration Storage
```python
class BusinessConfigManager:
    """Simple JSON-based business configuration storage."""

    def __init__(self, config_file="business_config.json"):
        self.config_file = config_file
        self._configs = {}

    def load_business(self, business_id: str) -> Optional[BusinessProfile]:
        """Load business configuration by ID."""
        if business_id not in self._configs:
            self._load_from_file()
        return self._configs.get(business_id)

    def _load_from_file(self):
        """Load configurations from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                for business_id, config in data.items():
                    self._configs[business_id] = BusinessProfile(**config)
        except FileNotFoundError:
            logger.warning(f"Business config file not found: {self.config_file}")
```

## Essential Python Packages

### Core Dependencies (requirements.txt)
```
# Pydantic AI Framework
pydantic-ai>=0.1.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# OpenAI Integration
openai>=1.0.0

# Google Calendar API
google-api-python-client>=2.100.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0

# Async Support
httpx>=0.25.0
aiofiles>=23.0.0

# Italian Timezone Support
pytz>=2023.3

# Simple Database
sqlite3  # Built-in with Python
aiosqlite>=0.19.0

# Development & Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Logging
loguru>=0.7.0
```

## Settings Management

### Environment Configuration Class
```python
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv

class ScheduleSettings(BaseSettings):
    """Configuration for schedule AI agent."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Configuration
    llm_provider: str = Field(default="openai")
    llm_api_key: str = Field(..., description="OpenAI API key")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_base_url: str = Field(default="https://api.openai.com/v1")

    # Google Calendar Configuration
    google_calendar_api_key: str = Field(..., description="Google Calendar API key")
    google_calendar_client_id: str = Field(..., description="Google OAuth client ID")
    google_calendar_client_secret: str = Field(..., description="Google OAuth client secret")
    google_calendar_refresh_token: str = Field(..., description="Google OAuth refresh token")

    # Business Configuration
    default_timezone: str = Field(default="Europe/Rome")
    business_hours_start: str = Field(default="09:00")
    business_hours_end: str = Field(default="18:00")
    working_days: str = Field(default="1,2,3,4,5")

    # Application Settings
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    max_retries: int = Field(default=3)
    timeout_seconds: int = Field(default=30)

    @field_validator("llm_api_key")
    @classmethod
    def validate_llm_key(cls, v):
        """Ensure LLM API key is not empty."""
        if not v or v.strip() == "":
            raise ValueError("LLM API key cannot be empty")
        return v

    @property
    def working_days_list(self) -> list[int]:
        """Parse working days string to list."""
        return [int(day.strip()) for day in self.working_days.split(",")]
```

## Database Configuration

### Simple SQLite Setup
```python
import aiosqlite
from typing import Optional

class DatabaseManager:
    """Simple SQLite database for appointments and clients."""

    def __init__(self, db_path: str = "appointments.db"):
        self.db_path = db_path

    async def initialize(self):
        """Create database tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id TEXT PRIMARY KEY,
                    business_id TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    client_email TEXT,
                    client_phone TEXT,
                    consultant_id TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    datetime TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    calendar_event_id TEXT,
                    status TEXT DEFAULT 'scheduled',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    email TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            await db.commit()
```

## Security Configuration

### API Key Management
```python
import os
from typing import Optional

class SecurityManager:
    """Basic security management for API keys and data."""

    @staticmethod
    def encrypt_api_key(api_key: str) -> str:
        """Basic encryption for API keys (use proper encryption in production)."""
        # In production, use proper encryption like cryptography.fernet
        return api_key  # Placeholder - implement proper encryption

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Basic input sanitization."""
        return text.strip()[:500]  # Simple length limit
```

## Error Handling Configuration

### Retry and Timeout Settings
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryConfig:
    """Retry configuration for external API calls."""

    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def calendar_api_call(func, *args, **kwargs):
        """Retry wrapper for Google Calendar API calls."""
        return await func(*args, **kwargs)

    @staticmethod
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5)
    )
    async def llm_api_call(func, *args, **kwargs):
        """Retry wrapper for OpenAI API calls."""
        return await func(*args, **kwargs)
```

## Testing Configuration

### Test Environment Setup
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
from pydantic_ai.models.test import TestModel

@pytest.fixture
def test_settings():
    """Mock settings for testing."""
    return Mock(
        llm_provider="openai",
        llm_api_key="test-key",
        llm_model="gpt-4o-mini",
        google_calendar_api_key="test-google-key",
        debug=True
    )

@pytest.fixture
def test_dependencies():
    """Test dependencies."""
    from dependencies import ScheduleAgentDependencies
    return ScheduleAgentDependencies(
        openai_api_key="test-key",
        google_calendar_config={
            "api_key": "test-google-key",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "refresh_token": "test-refresh-token"
        },
        debug=True
    )

@pytest.fixture
def test_agent():
    """Test agent with TestModel."""
    from pydantic_ai import Agent
    return Agent(TestModel(), deps_type=ScheduleAgentDependencies)
```

## Deployment Configuration

### Environment File Template (.env.example)
```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1

# Google Calendar Integration
GOOGLE_CALENDAR_API_KEY=your-google-calendar-api-key
GOOGLE_CALENDAR_CLIENT_ID=your-google-client-id
GOOGLE_CALENDAR_CLIENT_SECRET=your-google-client-secret
GOOGLE_CALENDAR_REFRESH_TOKEN=your-google-refresh-token

# Business Configuration
DEFAULT_TIMEZONE=Europe/Rome
BUSINESS_HOURS_START=09:00
BUSINESS_HOURS_END=18:00
WORKING_DAYS=1,2,3,4,5

# Application Settings
APP_ENV=production
DEBUG=false
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

## Quality Checklist

Before finalizing dependency configuration:
- ✅ All required environment variables identified
- ✅ Single model provider (OpenAI) configured
- ✅ Google Calendar API integration planned
- ✅ Multi-business support through configuration
- ✅ Simple dataclass dependencies defined
- ✅ Minimal Python package list
- ✅ Security considerations addressed
- ✅ Testing configuration provided
- ✅ Error handling and retry logic
- ✅ Italian timezone support included

## Integration Notes

This configuration will be used by:
- **Main Claude Code**: Implements agent.py with these dependencies
- **pydantic-ai-validator**: Tests with this configuration
- **Google Calendar API**: Primary calendar integration
- **Multi-business support**: Through BusinessProfile configurations

Archon Project ID: 33213ec9-6ccd-4ea4-b9d1-c1a9c425d42f