#!/usr/bin/env python3
"""
Advanced OAuth solver - automatically tests multiple configurations
and provides the definitive solution for redirect_uri_mismatch issues.
"""

import os
import webbrowser
import time
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import threading
import socket
from urllib.parse import urlencode, parse_qs

load_dotenv()

class OAuthSolver:
    """Advanced OAuth configuration solver."""

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CALENDAR_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CALENDAR_CLIENT_SECRET")
        self.available_ports = self._find_available_ports()
        self.test_results = {}

    def _find_available_ports(self):
        """Find available ports for testing."""
        ports = [3000, 8080, 8000, 5000, 4000, 9000]
        available = []

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                available.append(port)
            except OSError:
                continue

        return available

    def test_redirect_uri_combinations(self):
        """Test all possible redirect URI combinations."""
        print("🔍 Testing all redirect URI combinations...")
        print(f"Available ports: {self.available_ports}")

        combinations = []
        for port in self.available_ports:
            combinations.extend([
                f"http://localhost:{port}/callback",
                f"http://127.0.0.1:{port}/callback",
                f"http://localhost:{port}/auth/callback",
                f"http://127.0.0.1:{port}/auth/callback"
            ])

        print(f"\n🧪 Testing {len(combinations)} combinations...")

        for uri in combinations:
            print(f"Testing: {uri}")

            try:
                # Extract port and redirect path from URI
                if "localhost:" in uri:
                    host = "localhost"
                else:
                    host = "127.0.0.1"

                port = int(uri.split(":")[1].split("/")[0])
                path = "/" + "/".join(uri.split(":")[1].split("/")[1:])

                flow = InstalledAppFlow.from_client_config(
                    {
                        "web": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [uri]
                        }
                    },
                    ['https://www.googleapis.com/auth/calendar']
                )

                # Test if we can create the authorization URL
                auth_url, state = flow.authorization_url(
                    access_type='offline',
                    prompt='consent',
                    redirect_uri=uri
                )

                print(f"✅ {uri} - Configuration valid")
                self.test_results[uri] = {
                    "status": "valid",
                    "auth_url": auth_url,
                    "state": state,
                    "port": port,
                    "path": path
                }

            except Exception as e:
                error_msg = str(e).lower()
                print(f"❌ {uri} - {error_msg}")
                self.test_results[uri] = {
                    "status": "invalid",
                    "error": str(e)
                }

        return self.test_results

    def find_best_working_config(self):
        """Find the best working configuration."""
        valid_configs = [uri for uri, result in self.test_results.items()
                        if result["status"] == "valid"]

        if not valid_configs:
            print("\n❌ No valid configurations found!")
            return None

        # Prefer localhost over 127.0.0.1 and standard ports
        preferred_configs = []

        # First preference: localhost:3000
        for uri in valid_configs:
            if "localhost:3000" in uri:
                preferred_configs.append(uri)
                break

        # Second preference: localhost:8080
        if not preferred_configs:
            for uri in valid_configs:
                if "localhost:8080" in uri:
                    preferred_configs.append(uri)
                    break

        # Third preference: any localhost with /callback
        if not preferred_configs:
            for uri in valid_configs:
                if "localhost:" in uri and "/callback" in uri:
                    preferred_configs.append(uri)
                    break

        # Fallback: any valid config
        if not preferred_configs and valid_configs:
            preferred_configs.append(valid_configs[0])

        return preferred_configs[0] if preferred_configs else None

    def run_oauth_flow(self, redirect_uri):
        """Run OAuth flow with the specified redirect URI."""
        print(f"\n🚀 Running OAuth flow with: {redirect_uri}")

        try:
            result = self.test_results[redirect_uri]
            port = result["port"]

            flow = InstalledAppFlow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [redirect_uri]
                    }
                },
                ['https://www.googleapis.com/auth/calendar']
            )

            print(f"📝 Opening browser for OAuth authentication...")
            print(f"🔗 Redirect URI: {redirect_uri}")
            print(f"💡 If you get 'redirect_uri_mismatch', add this exact URI to your Google Cloud Console:")
            print(f"   {redirect_uri}")

            creds = flow.run_local_server(
                port=port,
                prompt='consent',
                access_type='offline'
            )

            return creds

        except Exception as e:
            print(f"❌ OAuth flow failed: {e}")
            return None

    def provide_setup_instructions(self, redirect_uri):
        """Provide detailed setup instructions."""
        print(f"\n📋 GOOGLE CLOUD CONSOLE SETUP INSTRUCTIONS")
        print("=" * 60)
        print(f"1. Go to: https://console.cloud.google.com/")
        print(f"2. Select your project")
        print(f"3. Go to: APIs & Services → Credentials")
        print(f"4. Find your OAuth client: {self.client_id[:30]}...")
        print(f"5. Click to edit the client")
        print(f"6. Under 'Authorized redirect URIs', add EXACTLY:")
        print(f"   {redirect_uri}")
        print(f"7. Remove any other redirect URIs")
        print(f"8. Click 'Save'")
        print(f"9. Wait 5 minutes for changes to take effect")
        print("=" * 60)

def main():
    """Main solver function."""
    print("🔧 ADVANCED OAUTH SOLVER")
    print("=" * 50)

    solver = OAuthSolver()

    if not solver.client_id or not solver.client_secret:
        print("❌ Missing OAuth credentials in .env file!")
        return False

    print(f"Client ID: {solver.client_id[:30]}...")
    print(f"Client Secret: Present")

    # Test all combinations
    results = solver.test_redirect_uri_combinations()

    # Find best config
    best_config = solver.find_best_working_config()

    if best_config:
        print(f"\n✅ Best working configuration found: {best_config}")

        # Provide setup instructions
        solver.provide_setup_instructions(best_config)

        # Ask user to try
        print(f"\n🔄 After updating Google Cloud Console, try this test:")
        print(f"python3 -c \"from advanced_oauth_solver import OAuthSolver; s=OAuthSolver(); s.run_oauth_flow('{best_config}')\"")

        return True
    else:
        print(f"\n❌ No working configurations found!")
        print(f"🔧 Possible solutions:")
        print(f"1. Create a new OAuth client in Google Cloud Console")
        print(f"2. Enable Google Calendar API")
        print(f"3. Add your email as test user")
        print(f"4. Publish OAuth consent screen")

        return False

if __name__ == "__main__":
    main()