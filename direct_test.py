#!/usr/bin/env python3
"""Direct test of playlist creation"""

import json
from pathlib import Path
from ytmusicapi import YTMusic

def main():
    # First, let's try to understand what's happening
    oauth_path = Path("oauth.json")

    print("Trying different initialization methods...\n")

    # Method 1: Direct path as string
    print("1. YTMusic(auth='oauth.json')...")
    try:
        ytmusic = YTMusic(auth="oauth.json")
        print("   SUCCESS!")

        # Try a simple API call
        print("   Testing API access...")
        search = ytmusic.search("Artifact303 Feelings", filter="songs", limit=1)
        if search:
            print(f"   Found: {search[0]['title']} by {search[0]['artists'][0]['name']}")

        # Try creating a test playlist
        print("\n   Creating test playlist...")
        playlist_id = ytmusic.create_playlist(
            title="Test Playlist - Delete Me",
            description="Test playlist created via API"
        )
        print(f"   Playlist created! ID: {playlist_id}")

        # Search for a track and add it
        print("\n   Searching for a track to add...")
        search_results = ytmusic.search("Artifact303 Feelings", filter="songs", limit=1)
        if search_results:
            video_id = search_results[0]['videoId']
            print(f"   Found video ID: {video_id}")

            print("   Adding to playlist...")
            ytmusic.add_playlist_items(playlist_id, [video_id])
            print("   SUCCESS! Track added to playlist!")

        print(f"\n✅ Full success! Playlist URL: https://music.youtube.com/playlist?list={playlist_id}")

    except Exception as e:
        print(f"   FAILED: {e}")
        print(f"   Error type: {type(e).__name__}")

    print("\n" + "="*50)

if __name__ == "__main__":
    main()
