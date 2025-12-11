#!/usr/bin/env python3
"""
Test the final Google Calendar integration with smart authentication.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from agent import get_agent
from google_calendar import create_google_calendar_event, check_google_calendar_availability

async def test_final_integration():
    """Test the complete integration with smart authentication."""

    print("🧪 TESTING FINAL GOOGLE CALENDAR INTEGRATION")
    print("=" * 60)

    # Test 1: Check availability
    print("\n1️⃣ Testing availability check...")
    start_time = (datetime.now() + timedelta(hours=2)).isoformat()
    end_time = (datetime.now() + timedelta(hours=3)).isoformat()

    availability = await check_google_calendar_availability(
        start_time=start_time,
        end_time=end_time,
        client_id=os.getenv("GOOGLE_CALENDAR_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", ""),
        refresh_token=os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN", "")
    )

    print(f"✅ Availability result: {availability}")

    # Test 2: Create event
    print("\n2️⃣ Testing event creation...")
    event_start = (datetime.now() + timedelta(hours=1)).isoformat()

    event_result = await create_google_calendar_event(
        title="Test Event - Final Integration",
        start_time=event_start,
        duration_minutes=30,
        client_name="Test Client",
        service_type="Test Service",
        description="This is a test event for the final integration test",
        client_email=None,
        client_id=os.getenv("GOOGLE_CALENDAR_CLIENT_ID", ""),
        client_secret=os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET", ""),
        refresh_token=os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN", "")
    )

    print(f"✅ Event creation result: {event_result}")

    # Test 3: Full agent workflow
    print("\n3️⃣ Testing full agent workflow...")
    agent = get_agent()

    response = await agent.process_message(
        message="Vorrei prenotare una consulenza per domani alle 15:00. Cliente: Mario Rossi, Email: mario.rossi@example.com",
        session_id="test_final_integration"
    )

    print(f"✅ Agent response: {response}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)

    availability_success = availability.get("success", False)
    event_success = event_result.get("success", False)
    agent_has_calendar = "google calendar" in response.lower() or "calendario" in response.lower()

    print(f"Availability Check: {'✅ PASS' if availability_success else '❌ FAIL'}")
    print(f"Event Creation: {'✅ PASS' if event_success else '❌ FAIL'}")
    print(f"Agent Integration: {'✅ PASS' if agent_has_calendar else '❌ FAIL'}")

    if availability_success and event_success:
        print(f"\n🎉 COMPLETE SUCCESS! Your Google Calendar integration is working!")
        print(f"📅 The agent can now create real events in Google Calendar!")
    elif event_success:
        print(f"\n✅ PARTIAL SUCCESS! Event creation works!")
        print(f"📅 The agent can create events, check the response above for details.")
    else:
        print(f"\n❌ INTEGRATION FAILED!")
        print(f"🔧 See the error messages above for troubleshooting steps.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_final_integration())