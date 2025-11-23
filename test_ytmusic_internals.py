#!/usr/bin/env python3
"""Test ytmusicapi internals to understand the 400 error"""

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

print("Initializing YTMusic with detailed debugging...")
ytmusic = YTMusic('oauth.json', oauth_credentials=creds)

# Check the headers being sent
print("\nHeaders YTMusic is using:")
for key, value in ytmusic.headers.items():
    if key == "Authorization" and value:
        print(f"  {key}: {value[:30]}...")
    else:
        print(f"  {key}: {value}")

# Check the base URL
print(f"\nBase URL: {ytmusic._base_url if hasattr(ytmusic, '_base_url') else 'Not found'}")

# Try to inspect what endpoint it's hitting
print("\nAttempting a search to see the request details...")
try:
    # Enable logging to see the actual request
    import logging
    logging.basicConfig(level=logging.DEBUG)

    results = ytmusic.search("test", limit=1)
    print("Search succeeded!")
except Exception as e:
    print(f"Search failed: {e}")

    # Try to get more details about the request
    if hasattr(e, 'response'):
        print(f"Response status: {e.response.status_code}")
        print(f"Response headers: {e.response.headers}")
        print(f"Response body: {e.response.text[:500]}")
