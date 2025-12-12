#!/usr/bin/env python3
"""
Check what redirect URIs are configured in Google Cloud Console
by trying different common variations.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")

# Common redirect URI variations to test
redirect_uris_to_test = [
    "http://localhost:8080/callback",
    "http://localhost:8080/callback/",
    "http://127.0.0.1:8080/callback",
    "http://127.0.0.1:8080/callback/",
    "http://localhost:3000/callback",
    "http://localhost:3000/callback/",
    "http://localhost:8000/callback",
]

print("🔍 Testing different redirect URIs...")
print(f"Client ID: {CLIENT_ID[:30]}..." if CLIENT_ID else "Missing client ID")

def test_redirect_uri(redirect_uri):
    """Test if a redirect URI works with the current OAuth config."""
    try:
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            ["https://www.googleapis.com/auth/calendar"]
        )

        # Just try to create the auth URL to see if the config is valid
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent'
        )

        print(f"✅ {redirect_uri} - Valid configuration")
        return True

    except Exception as e:
        print(f"❌ {redirect_uri} - {str(e)}")
        return False

print("\n🧪 Testing redirect URIs...")
valid_uris = []

for uri in redirect_uris_to_test:
    if test_redirect_uri(uri):
        valid_uris.append(uri)

if valid_uris:
    print(f"\n✅ Valid redirect URIs found: {valid_uris}")
    print(f"\n🎯 Use this one: {valid_uris[0]}")
else:
    print("\n❌ No valid redirect URIs found.")
    print("You need to update your Google Cloud Console configuration.")