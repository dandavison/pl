#!/usr/bin/env python3
"""Test with explicit headers"""

from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials
import json

# Load credentials
with open('oauth_creds.json', 'r') as f:
    creds_data = json.load(f)

# Load oauth to check its structure
with open('oauth.json', 'r') as f:
    oauth_data = json.load(f)
    print("OAuth token structure:")
    for key in oauth_data:
        if key in ['access_token', 'refresh_token']:
            print(f"  {key}: ...{oauth_data[key][-10:]}")
        else:
            print(f"  {key}: {oauth_data[key]}")

creds = OAuthCredentials(
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)

print("\nInitializing YTMusic...")

# Try initializing with just the auth file first (simpler)
try:
    print("\nMethod 1: Direct auth file...")
    ytmusic = YTMusic(auth='oauth.json')
    print("  Initialized, testing search...")
    results = ytmusic.search("test", limit=1)
    print("  ✓ Success with direct auth file!")
except Exception as e:
    print(f"  ✗ Failed: {e}")

    # Try with oauth_credentials
    try:
        print("\nMethod 2: Auth file + oauth_credentials...")
        ytmusic = YTMusic(auth='oauth.json', oauth_credentials=creds)
        print("  Initialized, testing search...")
        results = ytmusic.search("test", limit=1)
        print("  ✓ Success with oauth_credentials!")
    except Exception as e2:
        print(f"  ✗ Failed: {e2}")
