#!/usr/bin/env python3
"""Fresh authentication flow"""

from ytmusicapi.auth.oauth import OAuthCredentials
import json

# Load credentials
with open('oauth_creds.json', 'r') as f:
    creds_data = json.load(f)

print("Starting fresh OAuth flow...")
print("=" * 50)

# Create credentials
creds = OAuthCredentials(
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)

# Get auth code
code = creds.get_code()

print(f"\n🔗 Please visit this URL:\n   {code['verification_url']}\n")
print(f"📝 Enter this code: {code['user_code']}\n")
print("=" * 50)
print("\nWaiting for authorization...")
print("Press Ctrl+C once you've completed authorization in the browser\n")

device_code = code['device_code']

print(f"Device code for next step: {device_code}")
print("\nOnce authorized, run:")
print(f"  python complete_auth.py {device_code}")

# Save device code for next step
with open('device_code.txt', 'w') as f:
    f.write(device_code)
