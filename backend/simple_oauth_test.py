#!/usr/bin/env python3
"""
Simple OAuth test - enter your new credentials directly here.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
import os

# ENTER YOUR NEW CREDENTIALS HERE (or update .env and remove these lines)
load_dotenv()
CLIENT_ID = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")  # or paste your new Client ID as string
CLIENT_SECRET = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")  # or paste your new Client Secret as string

def simple_oauth_test():
    """Test OAuth with minimal configuration."""

    print("🧪 Simple OAuth Test")
    print(f"Client ID: {CLIENT_ID[:30] if CLIENT_ID else 'MISSING'}...")
    print(f"Client Secret: {'Present' if CLIENT_SECRET else 'MISSING'}")

    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n❌ Missing credentials!")
        print("Add your Client ID and Client Secret above or update .env file")
        return False

    try:
        flow = InstalledAppFlow.from_client_config(
            {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:3000/callback"]
                }
            },
            ["https://www.googleapis.com/auth/calendar"]
        )

        print("\n🚀 Starting OAuth flow...")
        print("If you get 'redirect_uri_mismatch', make sure you have:")
        print("http://localhost:3000/callback")
        print("in your Google Cloud Console OAuth client configuration!")

        creds = flow.run_local_server(
            port=3000,
            prompt='consent',
            access_type='offline'
        )

        print("\n🎉 SUCCESS!")
        print(f"Refresh Token: {creds.refresh_token[:50] if creds.refresh_token else 'NONE'}...")

        if creds.refresh_token:
            print(f"\n🔑 Add this to your .env:")
            print(f"GOOGLE_CALENDAR_REFRESH_TOKEN={creds.refresh_token}")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if "redirect_uri_mismatch" in str(e).lower():
            print(f"\n🔧 Fix:")
            print(f"1. Go to Google Cloud Console")
            print(f"2. Find OAuth client: {CLIENT_ID[:30]}...")
            print(f"3. Edit and add: http://localhost:3000/callback")
            print(f"4. Save and wait 5 minutes")
        return False

if __name__ == "__main__":
    simple_oauth_test()