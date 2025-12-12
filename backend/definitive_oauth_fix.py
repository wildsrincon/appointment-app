#!/usr/bin/env python3
"""
Definitive OAuth fix - creates a new, properly configured OAuth client.
"""

import os
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

def oauth_diagnostic():
    """Comprehensive OAuth diagnostic and fix."""

    print("🔍 OAUTH DIAGNOSTIC & FIX")
    print("=" * 50)

    # Check current environment
    from dotenv import load_dotenv
    load_dotenv()

    current_client_id = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
    current_client_secret = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")

    print(f"Current Client ID: {current_client_id[:30] if current_client_id else 'Missing'}...")
    print(f"Current Client Secret: {'Present' if current_client_secret else 'Missing'}")

    print("\n📋 STEP 1: CREATE NEW OAUTH CLIENT")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Select your project")
    print("3. Go to: APIs & Services → Credentials")
    print("4. Click '+ Create Credentials' → 'OAuth client ID'")
    print("5. Application type: 'Web application'")
    print("6. Name: 'Schedule AI Agent v2'")
    print("7. Authorized redirect URIs: Add EXACTLY these:")
    print("   - http://localhost:3000/callback")
    print("   - http://localhost:8080/callback")
    print("8. Click 'Create'")

    print("\n⏳ After creating, you'll see your credentials.")
    print("Copy the Client ID and Client Secret and update your .env file.")

    # Prompt for new credentials
    print("\n" + "=" * 50)
    print("🔧 UPDATE YOUR CREDENTIALS")
    print("=" * 50)

    new_client_id = input("Enter new Client ID: ").strip()
    new_client_secret = input("Enter new Client Secret: ").strip()

    if not new_client_id or not new_client_secret:
        print("❌ Both Client ID and Client Secret are required!")
        return False

    print("\n🧪 TESTING NEW OAUTH CONFIGURATION...")

    # Test both redirect URIs
    redirect_uris = [
        ("http://localhost:3000/callback", 3000),
        ("http://localhost:8080/callback", 8080)
    ]

    for redirect_uri, port in redirect_uris:
        print(f"\n🔄 Testing: {redirect_uri}")

        try:
            flow = InstalledAppFlow.from_client_config(
                {
                    "web": {
                        "client_id": new_client_id,
                        "client_secret": new_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                ['https://www.googleapis.com/auth/calendar']
            )

            print(f"✅ Configuration valid for {redirect_uri}")

            # Try to actually run OAuth flow
            try:
                print(f"🚀 Opening browser for {redirect_uri}...")
                print("📝 If you get 'redirect_uri_mismatch', the URI in Google Cloud Console doesn't match exactly!")
                print("💡 Make sure it's EXACTLY: " + redirect_uri)

                creds = flow.run_local_server(
                    port=port,
                    prompt='consent',
                    access_type='offline'
                )

                print("\n🎉 SUCCESS! OAuth completed!")
                print("=" * 60)
                print(f"✅ Client ID: {new_client_id}")
                print(f"✅ Client Secret: {'*' * len(new_client_secret)}")
                print(f"✅ Redirect URI: {redirect_uri}")
                print(f"✅ Access Token: {creds.token[:30]}..." if creds.token else "None")
                print(f"✅ Refresh Token: {creds.refresh_token[:30] if creds.refresh_token else 'None'}...")
                print("=" * 60)

                if creds.refresh_token:
                    print(f"\n🔑 UPDATE YOUR .env FILE:")
                    print(f"GOOGLE_CALENDAR_CLIENT_ID={new_client_id}")
                    print(f"GOOGLE_CALENDAR_CLIENT_SECRET={new_client_secret}")
                    print(f"GOOGLE_CALENDAR_REFRESH_TOKEN={creds.refresh_token}")

                    # Auto-update .env file
                    env_file = ".env"
                    if os.path.exists(env_file):
                        with open(env_file, 'r') as f:
                            content = f.read()

                        content = content.replace(
                            f"GOOGLE_CALENDAR_CLIENT_ID={current_client_id}",
                            f"GOOGLE_CALENDAR_CLIENT_ID={new_client_id}"
                        )
                        content = content.replace(
                            f"GOOGLE_CALENDAR_CLIENT_SECRET={current_client_secret}",
                            f"GOOGLE_CALENDAR_CLIENT_SECRET={new_client_secret}"
                        )

                        with open(env_file, 'w') as f:
                            f.write(content)

                        print(f"\n✅ .env file updated automatically!")

                    return True
                else:
                    print("⚠️ No refresh token received. This might be a problem.")
                    return False

            except Exception as oauth_error:
                print(f"❌ OAuth flow failed: {oauth_error}")
                if "redirect_uri_mismatch" in str(oauth_error).lower():
                    print(f"\n🔧 REDIRECT URI MISMATCH FIX:")
                    print(f"1. Go to Google Cloud Console")
                    print(f"2. Find your OAuth client: {new_client_id[:30]}...")
                    print(f"3. Edit the client")
                    print(f"4. Under 'Authorized redirect URIs', add EXACTLY: {redirect_uri}")
                    print(f"5. Remove any other redirect URIs that don't match")
                    print(f"6. Save and wait 5 minutes")

                continue

        except Exception as config_error:
            print(f"❌ Configuration error: {config_error}")
            continue

    print(f"\n❌ Both redirect URIs failed. Please check your Google Cloud Console setup.")
    return False

def verify_setup():
    """Verify the complete OAuth setup."""
    print("\n🔍 FINAL VERIFICATION")
    print("=" * 30)

    required_checklist = [
        "✅ Google Calendar API enabled",
        "✅ OAuth consent screen configured and published",
        "✅ Your email added as test user",
        "✅ OAuth client created with correct redirect URIs",
        "✅ .env file updated with new credentials"
    ]

    print("Checklist:")
    for item in required_checklist:
        print(f"  {item}")

    print(f"\nIf you have all ✅ items, run: ./test_env/bin/python test_oauth_config.py")

if __name__ == "__main__":
    success = oauth_diagnostic()
    verify_setup()

    if success:
        print(f"\n🎉 OAuth setup completed successfully!")
        print(f"📅 Your Google Calendar integration should now work!")
    else:
        print(f"\n❌ OAuth setup failed. Please review the error messages above.")
        print(f"📧 If you need help, share the exact error message.")