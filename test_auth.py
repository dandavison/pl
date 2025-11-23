#!/usr/bin/env python3
"""Test script to verify YTMusic authentication is working"""

import json
from pathlib import Path
from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken

def test_oauth():
    oauth_path = Path("oauth.json")

    print(f"1. Checking if oauth.json exists: {oauth_path.exists()}")

    if not oauth_path.exists():
        print("   ERROR: oauth.json not found!")
        return False

    print("\n2. Loading oauth.json...")
    with open(oauth_path, 'r') as f:
        oauth_data = json.load(f)

    print(f"   Keys in oauth.json: {list(oauth_data.keys())}")
    print(f"   Has oauth_credentials: {'oauth_credentials' in oauth_data}")

    if 'oauth_credentials' in oauth_data:
        print(f"   Client ID: {oauth_data['oauth_credentials']['client_id'][:20]}...")

    print("\n3. Attempting to create YTMusic instance...")
    try:
        ytmusic = YTMusic(str(oauth_path))
        print("   SUCCESS: YTMusic instance created!")

        print("\n4. Testing API call (getting user playlists)...")
        playlists = ytmusic.get_library_playlists(limit=1)
        print(f"   SUCCESS: Retrieved {len(playlists)} playlist(s)")
        if playlists:
            print(f"   First playlist: {playlists[0]['title']}")

        return True

    except Exception as e:
        print(f"   ERROR: {e}")
        print(f"   Error type: {type(e).__name__}")

        # Try to provide more details
        if "oauth_credentials" in str(e):
            print("\n   The error mentions oauth_credentials. Let's try fixing it...")

            # Check if we need to reformat the oauth file
            if 'oauth_credentials' in oauth_data:
                print("   oauth_credentials found in file, trying alternative approach...")

                # Try creating YTMusic with explicit auth
                try:
                    print("\n   Attempting with auth parameter...")
                    ytmusic = YTMusic(auth=oauth_path)
                    print("   SUCCESS with auth parameter!")
                    return True
                except Exception as e2:
                    print(f"   Still failed: {e2}")

        return False

if __name__ == "__main__":
    print("Testing YTMusic Authentication\n" + "="*40)
    success = test_oauth()
    print("\n" + "="*40)
    if success:
        print("✅ Authentication is working!")
    else:
        print("❌ Authentication failed. Check the errors above.")
