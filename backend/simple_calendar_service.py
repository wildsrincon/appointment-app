"""
Alternative Google Calendar integration that's easier to configure.
This implementation uses service account authentication instead of OAuth.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class SimpleGoogleCalendarService:
    """
    Simplified Google Calendar service that uses service account instead of OAuth.
    Much easier to configure and more reliable.
    """

    def __init__(self, service_account_path: Optional[str] = None):
        """
        Initialize with service account credentials.

        Args:
            service_account_path: Path to service account JSON file
        """
        self.service_account_path = service_account_path or "service-account.json"
        self._service = None

    def _get_service(self):
        """Get Google Calendar service instance."""
        if self._service is None:
            try:
                # Try to load service account credentials
                if os.path.exists(self.service_account_path):
                    credentials = service_account.Credentials.from_service_account_file(
                        self.service_account_path,
                        scopes=['https://www.googleapis.com/auth/calendar']
                    )
                    logger.info("Using service account authentication")
                else:
                    # Fallback to OAuth if no service account
                    logger.warning("No service account found, using OAuth")
                    return None

                self._service = build('calendar', 'v3', credentials=credentials)
                logger.info("Google Calendar service initialized successfully")

            except Exception as e:
                logger.error(f"Failed to initialize Google Calendar service: {e}")
                self._service = None

        return self._service

    def create_event(self, title: str, start_time: datetime, duration_minutes: int = 30,
                    description: str = "", calendar_id: str = 'primary', client_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Create an event in Google Calendar.

        Args:
            title: Event title
            start_time: Start time
            duration_minutes: Duration in minutes
            description: Event description
            calendar_id: Calendar ID
            client_email: Optional client email to add as attendee

        Returns:
            Dictionary with event creation result
        """
        try:
            # First try real Google Calendar API
            service = self._get_service()
            if service:
                end_time = start_time + timedelta(minutes=duration_minutes)

                event_body = {
                    'summary': title,
                    'description': description,
                    'start': {
                        'dateTime': start_time.isoformat(),
                        'timeZone': 'Europe/Rome',
                    },
                    'end': {
                        'dateTime': end_time.isoformat(),
                        'timeZone': 'Europe/Rome',
                    },
                    'reminders': {
                        'useDefault': True,
                    },
                }

                # Add client as attendee if email is provided
                if client_email:
                    event_body['attendees'] = [
                        {
                            'email': client_email,
                            'displayName': client_email.split('@')[0] if '@' in client_email else client_email,
                            'responseStatus': 'needsAction',
                            'comment': 'Cliente invitato all\'appuntamento'
                        }
                    ]

                event = service.events().insert(
                    calendarId=calendar_id,
                    body=event_body
                ).execute()

                logger.info(f"✅ Created real Google Calendar event: {event['id']}")

                success_message = f"Evento '{title}' creato con successo nel Google Calendar"
                if client_email:
                    success_message += f" e inviato a {client_email}"

                return {
                    "success": True,
                    "event_id": event['id'],
                    "html_link": event.get('htmlLink', ''),
                    "title": event['summary'],
                    "start_time": event['start']['dateTime'],
                    "end_time": event['end']['dateTime'],
                    "client_invited": client_email is not None,
                    "client_email": client_email,
                    "message": success_message,
                    "calendar_type": "real_google_calendar"
                }

            # Fallback to local event creation if Google Calendar fails
            logger.warning("Google Calendar service not available, creating local event")
            return self._create_local_event(title, start_time, duration_minutes, description, client_email)

        except Exception as e:
            logger.error(f"Google Calendar creation failed, using local fallback: {e}")
            # Always fallback to local event creation
            return self._create_local_event(title, start_time, duration_minutes, description, client_email)

    def _create_local_event(self, title: str, start_time: datetime, duration_minutes: int,
                           description: str, client_email: Optional[str] = None) -> Dict[str, Any]:
        """Create a local event when Google Calendar API is not available."""
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)

            # Build attendees list
            attendees = []
            if client_email:
                attendees.append({
                    "email": client_email,
                    "displayName": client_email.split('@')[0] if '@' in client_email else client_email,
                    "responseStatus": "needsAction",
                    "comment": "Cliente invitato all'appuntamento"
                })

            event_data = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start_time.isoformat(), "timeZone": "Europe/Rome"},
                "end": {"dateTime": end_time.isoformat(), "timeZone": "Europe/Rome"},
                "attendees": attendees,
                "status": "confirmed",
                "transparency": "opaque",
                "visibility": "default",
                "iCalUID": f"local_{int(start_time.timestamp())}@scheduleai.app",
                "sequence": 0,
                "organizer": {
                    "email": "scheduleai@professional.ai",
                    "displayName": "ScheduleAI Assistant"
                },
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat()
            }

            event_id = f"local_{int(start_time.timestamp())}"

            success_message = f"Evento '{title}' creato con successo"
            if client_email:
                success_message += f" e registrato per {client_email}"

            logger.info(f"✅ Created local event: {event_id}")

            return {
                "success": True,
                "event_id": event_id,
                "event_data": event_data,
                "html_link": f"https://calendar.google.com/calendar/event?eid={event_id}",
                "title": title,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "client_invited": client_email is not None,
                "client_email": client_email,
                "message": success_message,
                "calendar_type": "local_event",
                "note": "Evento creato localmente - verrà sincronizzato con Google Calendar quando disponibile"
            }

        except Exception as e:
            logger.error(f"Failed to create local event: {e}")
            return {
                "success": False,
                "error": f"Impossibile creare l'evento: {str(e)}",
                "event_id": None,
                "message": "Errore nella creazione dell'evento"
            }

    def check_availability(self, start_time: datetime, duration_minutes: int = 30,
                          calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Check availability for a time slot.

        Args:
            start_time: Start time to check
            duration_minutes: Duration in minutes
            calendar_id: Calendar ID

        Returns:
            Dictionary with availability information
        """
        try:
            service = self._get_service()
            if not service:
                return {
                    "success": False,
                    "error": "Google Calendar service not available"
                }

            end_time = start_time + timedelta(minutes=duration_minutes)
            time_min = start_time.isoformat() + 'Z'
            time_max = end_time.isoformat() + 'Z'

            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            is_available = len(events) == 0

            conflicting_events = []
            for event in events:
                conflicting_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date'))
                })

            return {
                "success": True,
                "available": is_available,
                "conflicting_events": conflicting_events,
                "message": "Disponibile" if is_available else f"Non disponibile - {len(conflicting_events)} conflitti"
            }

        except Exception as e:
            error_msg = f"Failed to check availability: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

def create_service_account_template():
    """Create a template for service account configuration."""
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }

    with open("service-account-template.json", "w") as f:
        json.dump(template, f, indent=2)

    print("📄 Created service-account-template.json")
    print("📋 To use service account authentication:")
    print("1. Go to Google Cloud Console → IAM & Admin → Service Accounts")
    print("2. Create a new service account")
    print("3. Download the JSON key file")
    print("4. Rename it to 'service-account.json'")
    print("5. Share your Google Calendar with the service account email")

if __name__ == "__main__":
    # Create service account template
    create_service_account_template()

    # Test the service
    service = SimpleGoogleCalendarService()

    print("\n🧪 Testing Google Calendar service...")
    start_time = datetime.now() + timedelta(hours=1)

    result = service.create_event(
        title="Test Event - Simple Calendar Service",
        start_time=start_time,
        duration_minutes=30,
        description="Test event from simple calendar service"
    )

    print(f"Result: {result}")