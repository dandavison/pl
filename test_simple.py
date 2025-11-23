#!/usr/bin/env python3
"""Test simplest API calls"""

from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials
import json

# Load credentials
with open('oauth_creds.json', 'r') as f:
    creds_data = json.load(f)

creds = OAuthCredentials(
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)

print("Initializing YTMusic...")
ytmusic = YTMusic('oauth.json', oauth_credentials=creds)

# Test different API endpoints
tests = [
    ("Get user playlists", lambda: ytmusic.get_library_playlists(limit=1)),
    ("Get user", lambda: ytmusic.get_user("UC44hbeRoCZVVMVg5z0FfIww")),  # Some random user
    ("Search", lambda: ytmusic.search("test", limit=1)),
    ("Get artist", lambda: ytmusic.get_artist("UC52ZqHVQz5OoGhvbWiRal6g"))  # Some artist
]

for name, test_func in tests:
    print(f"\nTesting: {name}")
    try:
        result = test_func()
        print(f"  ✓ Success!")
        if result:
            print(f"  Result type: {type(result)}")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

# Try to get account info
print("\n" + "="*50)
print("Checking account access...")
try:
    # Try to get library which requires auth
    playlists = ytmusic.get_library_playlists(limit=1)
    print(f"✓ Can access library (found {len(playlists)} playlists)")
except Exception as e:
    print(f"✗ Cannot access library: {e}")
