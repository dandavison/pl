#!/usr/bin/env python3
"""Debug playlist creation"""

from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials
import json
import traceback

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
    print("\nAttempting to create playlist...")
    playlist_id = ytmusic.create_playlist(
        title="Test Playlist",
        description="Test"
    )
    print(f"✓ Playlist created! ID: {playlist_id}")
    print(f"  URL: https://music.youtube.com/playlist?list={playlist_id}")

except Exception as e:
    print(f"✗ Error creating playlist: {e}")
    print(f"  Error type: {type(e).__name__}")
    traceback.print_exc()
