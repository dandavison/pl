#!/usr/bin/env python3
"""Create YouTube playlist using YouTube Data API v3"""

import json
from typing import Any, Dict, List

import requests


def create_playlist(access_token: str, title: str, description: str) -> str:
    """Create a new YouTube playlist"""
    url = "https://www.googleapis.com/youtube/v3/playlists"
    params = {"part": "snippet,status"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "snippet": {
            "title": title,
            "description": description,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "private"  # Start as private, you can change it later
        },
    }

    response = requests.post(url, params=params, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to create playlist: {response.text}")

    return response.json()["id"]


def search_video(access_token: str, query: str) -> Dict[str, Any]:
    """Search for a video on YouTube"""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 1,
        "videoCategoryId": "10",  # Music category
    }
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Search failed: {response.text}")

    items = response.json().get("items", [])
    if items:
        return {
            "videoId": items[0]["id"]["videoId"],
            "title": items[0]["snippet"]["title"],
            "channelTitle": items[0]["snippet"]["channelTitle"],
        }
    return None


def add_to_playlist(access_token: str, playlist_id: str, video_id: str) -> bool:
    """Add a video to a playlist"""
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {"part": "snippet"}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": video_id},
        }
    }

    response = requests.post(url, params=params, headers=headers, json=data)
    return response.status_code == 200


def create_playlist_with_tracks(
    access_token: str, title: str, description: str, tracks: List[str]
) -> Dict[str, Any]:
    """Create a playlist and add tracks to it"""
    print(f"\n🎵 Creating playlist: {title}")
    print("=" * 60)

    # Create playlist
    try:
        playlist_id = create_playlist(access_token, title, description)
        print(f"✓ Playlist created! ID: {playlist_id}")
        print(f"  URL: https://www.youtube.com/playlist?list={playlist_id}")
    except Exception as e:
        print(f"✗ Failed to create playlist: {e}")
        return None

    # Search and add tracks
    print(f"\n📝 Adding {len(tracks)} tracks...")
    results = []
    added_count = 0

    for i, query in enumerate(tracks, 1):
        print(f"\n[{i}/{len(tracks)}] Searching: {query}")

        try:
            video = search_video(access_token, query)
            if video:
                print(f"  Found: {video['title']} by {video['channelTitle']}")

                if add_to_playlist(access_token, playlist_id, video["videoId"]):
                    print("  ✓ Added to playlist")
                    added_count += 1
                    results.append(
                        {
                            "query": query,
                            "found": True,
                            "title": video["title"],
                            "channel": video["channelTitle"],
                            "videoId": video["videoId"],
                        }
                    )
                else:
                    print("  ✗ Failed to add to playlist")
                    results.append(
                        {"query": query, "found": True, "error": "Failed to add"}
                    )
            else:
                print("  ✗ No results found")
                results.append({"query": query, "found": False})
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({"query": query, "found": False, "error": str(e)})

    print("\n" + "=" * 60)
    print("✅ Playlist created successfully!")
    print(f"📊 Added {added_count} of {len(tracks)} tracks")
    print(f"🔗 URL: https://www.youtube.com/playlist?list={playlist_id}")
    print(f"🎵 Music URL: https://music.youtube.com/playlist?list={playlist_id}")

    return {
        "playlist_id": playlist_id,
        "playlist_url": f"https://www.youtube.com/playlist?list={playlist_id}",
        "music_url": f"https://music.youtube.com/playlist?list={playlist_id}",
        "tracks_added": added_count,
        "tracks_total": len(tracks),
        "details": results,
    }


if __name__ == "__main__":
    # Load OAuth token
    with open("oauth.json", "r") as f:
        oauth_data = json.load(f)

    access_token = oauth_data["access_token"]

    # Define playlist
    playlist_title = "Contemporary Melodic Psy/Goa: The Essential Journey"
    playlist_description = (
        "A curated collection of the finest contemporary serious melodic psy/goa trance. "
        "Features the best modern artists carrying the torch of classic X-Dream's emotional "
        "and melodic style. No cheese, no gimmicks - just pure psychedelic journeys."
    )

    # Track list
    tracks = [
        "Artifact303 Feelings",
        "Mindsphere Inner Cyclone",
        "Celestial Intelligence Perpetual Energy",
        "Morphic Resonance Chromatic World",
        "Artifact303 Levitation Device",
        "Mindsphere Patience for Heaven",
        "Celestial Intelligence Anapa",
        "Morphic Resonance City of Moons",
        "E-Clip Shiva Chandra",
        "Ovnimoon Galactic Mantra",
        "Solar Fields Discovering",
        "E-Clip Sacred Science",
        "Psilocybian Subliminal Melancholies",
        "Triquetra Ecstatic Planet",
        "Median Project In the Depth of Space",
        "Crossing Mind Innermost Perception",
        "Hypnoxock Solar Warden",
        "Proxeeus Psychoactive Waste",
        "Crossing Mind Beyond the Senses",
        "Hypnoxock Distant Signals",
        "Cosmic Dimension Cosmic Ascension",
        "Goasia Amphibians on Spacedock",
        "Filteria Navigate",
        "Skarma Arrested Development",
        "JIS Illusions",
        "Median Project To Another Galaxy",
        "Celestial Intelligence Divine Miracles",
        "Morphic Resonance Psychoactive Landscape",
        "Artifact303 Through the Wormhole",
        "Mindsphere Reborn",
    ]

    # Create the playlist
    result = create_playlist_with_tracks(
        access_token, playlist_title, playlist_description, tracks
    )

    if result:
        # Save results
        with open("playlist_result.json", "w") as f:
            json.dump(result, f, indent=2)
        print("\n📁 Results saved to playlist_result.json")
