#!/usr/bin/env python3
"""Test if search works to verify auth"""

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
ytmusic = YTMusic(auth='oauth.json', oauth_credentials=creds)
print("✓ YTMusic initialized")

try:
    print("\nTesting search...")
    results = ytmusic.search("Artifact303 Feelings", filter="songs", limit=2)
    if results:
        for r in results:
            print(f"✓ Found: {r['title']} by {r['artists'][0]['name']}")
            print(f"  Video ID: {r['videoId']}")
    else:
        print("✗ No results found")

    print("\nTesting get_library_playlists...")
    playlists = ytmusic.get_library_playlists(limit=3)
    print(f"✓ Found {len(playlists)} playlists in library")
    for p in playlists:
        print(f"  - {p['title']} (ID: {p['playlistId']})")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
