"""YouTube Data API v3 integration for MCP server"""

import json
from typing import List, Dict, Any, Optional
import requests
from pathlib import Path


class YouTubeAPI:
    """Wrapper for YouTube Data API v3 operations"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def search_tracks(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for music tracks on YouTube with detailed metadata.
        Returns multiple results for LLM to choose from.

        Returns:
            List of dicts with keys:
            - videoId: YouTube video ID
            - title: Video title
            - channel: Channel name
            - channelId: Channel ID
            - description: Video description (truncated)
            - duration: Duration in ISO 8601 format
            - publishedAt: Upload date
            - viewCount: View count if available
            - isLive: Whether it's a live recording
            - isRemix: Heuristic check for remix
            - isRemaster: Heuristic check for remaster
        """
        url = f"{self.base_url}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "videoCategoryId": "10",  # Music category
            "order": "relevance"
        }

        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Search failed: {response.text}")

        items = response.json().get("items", [])
        video_ids = [item["id"]["videoId"] for item in items]

        # Get additional details for each video
        if video_ids:
            details = self._get_video_details(video_ids)
        else:
            details = {}

        results = []
        for item in items:
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            title = snippet["title"]

            # Heuristic checks
            title_lower = title.lower()
            is_remix = any(word in title_lower for word in
                         ["remix", "rmx", "rework", "bootleg", "edit"])
            is_remaster = any(word in title_lower for word in
                            ["remaster", "remastered", "2020", "2021", "2022", "2023", "2024"])
            is_live = "liveBroadcastContent" in snippet and snippet["liveBroadcastContent"] != "none"

            result = {
                "videoId": video_id,
                "title": title,
                "channel": snippet["channelTitle"],
                "channelId": snippet["channelId"],
                "description": snippet["description"][:200],
                "publishedAt": snippet["publishedAt"],
                "thumbnails": snippet["thumbnails"],
                "isLive": is_live,
                "isRemix": is_remix,
                "isRemaster": is_remaster,
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }

            # Add details if available
            if video_id in details:
                result.update(details[video_id])

            results.append(result)

        return results

    def _get_video_details(self, video_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get detailed information for videos"""
        url = f"{self.base_url}/videos"
        params = {
            "part": "contentDetails,statistics",
            "id": ",".join(video_ids)
        }

        response = requests.get(url, params=params, headers=self.headers)
        if response.status_code != 200:
            return {}

        details = {}
        for item in response.json().get("items", []):
            video_id = item["id"]
            details[video_id] = {
                "duration": item["contentDetails"]["duration"],
                "viewCount": int(item["statistics"].get("viewCount", 0)),
                "likeCount": int(item["statistics"].get("likeCount", 0))
            }

        return details

    def create_playlist(self, title: str, description: str,
                       privacy: str = "private") -> str:
        """Create a new YouTube playlist"""
        url = f"{self.base_url}/playlists"
        params = {"part": "snippet,status"}
        headers = {**self.headers, "Content-Type": "application/json"}

        data = {
            "snippet": {
                "title": title,
                "description": description,
                "defaultLanguage": "en"
            },
            "status": {
                "privacyStatus": privacy
            }
        }

        response = requests.post(url, params=params, headers=headers, json=data)
        if response.status_code != 200:
            raise Exception(f"Failed to create playlist: {response.text}")

        return response.json()["id"]

    def add_to_playlist(self, playlist_id: str, video_ids: List[str]) -> List[bool]:
        """Add multiple videos to a playlist"""
        url = f"{self.base_url}/playlistItems"
        params = {"part": "snippet"}
        headers = {**self.headers, "Content-Type": "application/json"}

        results = []
        for video_id in video_ids:
            data = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }

            response = requests.post(url, params=params, headers=headers, json=data)
            results.append(response.status_code == 200)

        return results


class PlaylistBuilder:
    """Intelligent playlist builder using YouTube API"""

    def __init__(self, youtube_api: YouTubeAPI):
        self.api = youtube_api

    def search_tracks_batch(self, queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for multiple tracks and return options for each.

        Returns:
            Dict mapping query -> list of search results
        """
        results = {}
        for query in queries:
            try:
                results[query] = self.api.search_tracks(query)
            except Exception as e:
                results[query] = {"error": str(e)}

        return results

    def create_playlist_from_ids(self, title: str, description: str,
                                video_ids: List[str]) -> Dict[str, Any]:
        """
        Create a playlist with specific video IDs (after LLM selection).

        Args:
            title: Playlist title
            description: Playlist description
            video_ids: List of YouTube video IDs to add

        Returns:
            Dict with playlist_id, urls, and success metrics
        """
        # Create playlist
        playlist_id = self.api.create_playlist(title, description)

        # Add videos
        add_results = self.api.add_to_playlist(playlist_id, video_ids)

        return {
            "playlist_id": playlist_id,
            "youtube_url": f"https://www.youtube.com/playlist?list={playlist_id}",
            "music_url": f"https://music.youtube.com/playlist?list={playlist_id}",
            "videos_added": sum(add_results),
            "videos_total": len(video_ids),
            "add_results": add_results
        }
