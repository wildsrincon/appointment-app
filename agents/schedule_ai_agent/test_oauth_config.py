#!/usr/bin/env python3
"""
Test script to validate Google OAuth configuration.
"""

import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow

# Load credentials from .env
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000/callback"
SCOPES = ['https://www.googleapis.com/auth/calendar']

def test_oauth_config():
    """Test OAuth configuration."""

    print("🔍 Testing Google OAuth Configuration...")
    print(f"Client ID: {CLIENT_ID[:20]}..." if CLIENT_ID else "❌ Client ID missing")
    print(f"Client Secret: {'✅ Present' if CLIENT_SECRET else '❌ Missing'}")

    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n❌ Missing OAuth credentials in .env file!")
        print("Please set GOOGLE_CALENDAR_CLIENT_ID and GOOGLE_CALENDAR_CLIENT_SECRET")
        return False

    print(f"\n🌐 Using redirect URI: {REDIRECT_URI}")
    print(f"📅 Requesting scope: {SCOPES[0]}")

    try:
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [REDIRECT_URI]
                }
            },
            SCOPES
        )

        print("\n🚀 Starting OAuth flow...")
        print("📝 Make sure:")
        print("   1. Your email is added as a test user in OAuth consent screen")
        print("   2. The redirect URI matches exactly in Google Cloud Console")
        print("   3. Google Calendar API scope is added to OAuth consent screen")

        # Run the OAuth flow
        flow.run_local_server(
            port=3000,
            prompt='consent',
            access_type='offline'
        )

        # If we get here, OAuth worked!
        creds = flow.credentials

        print("\n" + "="*60)
        print("🎉 SUCCESS! OAuth authentication completed!")
        print("="*60)
        print(f"\n✅ Access Token: {creds.token[:30]}...")
        print(f"✅ Refresh Token: {creds.refresh_token[:30] if creds.refresh_token else 'None'}...")
        print(f"✅ Expires at: {creds.expiry}")
        print(f"✅ Client ID: {creds.client_id}")

        if creds.refresh_token:
            print(f"\n🔑 NEW REFRESH TOKEN (copy to .env):")
            print(f"GOOGLE_CALENDAR_REFRESH_TOKEN={creds.refresh_token}")
        else:
            print(f"\n⚠️  No refresh token received. Make sure 'access_type=offline' and 'prompt=consent'")

        print("="*60)

        return True

    except Exception as e:
        print(f"\n❌ OAuth Error: {e}")
        print("\n🔧 Common fixes:")
        print("   1. Add your email as test user in OAuth consent screen")
        print("   2. Make sure redirect URI matches exactly")
        print("   3. Add Google Calendar API scope to OAuth consent screen")
        print("   4. Enable Google Calendar API in API Library")
        print("   5. Publish your OAuth consent screen")
        return False

if __name__ == "__main__":
    test_oauth_config()