"""Browser authentication support for YouTube Music."""

from pathlib import Path
from typing import Any, Dict, Optional

from ytmusicapi import YTMusic


class BrowserAuthManager:
    """Manage browser-based authentication for YouTube Music."""

    def __init__(self, browser_json_path: str = None):
        if browser_json_path is None:
            # Look in multiple locations
            possible_paths = [
                Path.home()
                / ".config"
                / "ytmusic-mcp"
                / "browser.json",  # User config dir
                Path.home() / ".ytmusic" / "browser.json",  # Home directory
                Path("browser.json"),  # Current directory
            ]
            for path in possible_paths:
                if path.exists():
                    self.browser_json_path = path
                    break
            else:
                # Default to user config directory
                self.browser_json_path = (
                    Path.home() / ".config" / "ytmusic-mcp" / "browser.json"
                )
        else:
            self.browser_json_path = Path(browser_json_path)
        self._ytmusic: Optional[YTMusic] = None

    def is_authenticated(self) -> bool:
        """Check if browser authentication is available."""
        return self.browser_json_path.exists()

    def get_ytmusic(self) -> YTMusic:
        """Get YTMusic instance with browser authentication."""
        if not self.is_authenticated():
            raise RuntimeError(f"Browser auth not found at {self.browser_json_path}")

        if self._ytmusic is None:
            self._ytmusic = YTMusic(str(self.browser_json_path))

        return self._ytmusic

    def setup_from_headers(self, headers_raw: str) -> str:
        """
        Setup browser authentication from raw headers.

        Args:
            headers_raw: Raw headers copied from browser

        Returns:
            Success message
        """
        import ytmusicapi

        # Use ytmusicapi's setup function to parse headers
        auth_json = ytmusicapi.setup(headers_raw=headers_raw)

        # Save to file
        with open(self.browser_json_path, "w") as f:
            f.write(auth_json)

        # Clear cached instance
        self._ytmusic = None

        return f"Browser authentication saved to {self.browser_json_path}"

    def validate_auth(self) -> Dict[str, Any]:
        """
        Validate browser authentication by making a test request.

        Returns:
            Dictionary with validation results
        """
        try:
            ytmusic = self.get_ytmusic()

            # Try to get library playlists as a test
            playlists = ytmusic.get_library_playlists(limit=1)

            # Try to search as well
            search_results = ytmusic.search("test", filter="songs", limit=1)

            return {
                "valid": True,
                "can_access_library": True,
                "can_search": len(search_results) > 0,
                "message": "Browser authentication is working",
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Browser authentication failed",
            }


class BrowserPlaylistManager:
    """Create playlists using browser authentication (no API quotas)."""

    def __init__(self, ytmusic: YTMusic):
        self.ytmusic = ytmusic

    def search_and_create_playlist(
        self, title: str, description: str, queries: list[str], privacy: str = "PRIVATE"
    ) -> Dict[str, Any]:
        """
        Search for tracks and create a playlist using browser auth.

        This method uses ytmusicapi's browser authentication which doesn't
        count against API quotas.

        Args:
            title: Playlist title
            description: Playlist description
            queries: List of search queries
            privacy: PRIVATE, UNLISTED, or PUBLIC

        Returns:
            Dictionary with results
        """
        # Create playlist
        playlist_id = self.ytmusic.create_playlist(
            title=title, description=description, privacy_status=privacy
        )

        if isinstance(playlist_id, dict) and "error" in playlist_id:
            return playlist_id

        # Search and add tracks
        results = []
        video_ids = []

        for query in queries:
            try:
                # Search with more results for better selection
                search_results = self.ytmusic.search(query, filter="songs", limit=5)

                if search_results:
                    # Select best match (prefer non-remix, non-live)
                    best_match = self._select_best_match(search_results, query)

                    if best_match:
                        video_ids.append(best_match["videoId"])
                        results.append(
                            {
                                "query": query,
                                "found": True,
                                "title": best_match.get("title"),
                                "artists": ", ".join(
                                    a["name"] for a in best_match.get("artists", [])
                                ),
                                "album": best_match.get("album", {}).get("name"),
                                "duration": best_match.get("duration"),
                                "videoId": best_match["videoId"],
                            }
                        )
                    else:
                        results.append(
                            {
                                "query": query,
                                "found": False,
                                "reason": "No suitable match found",
                            }
                        )
                else:
                    results.append(
                        {"query": query, "found": False, "reason": "No search results"}
                    )
            except Exception as e:
                results.append({"query": query, "found": False, "error": str(e)})

        # Add tracks to playlist
        if video_ids:
            try:
                self.ytmusic.add_playlist_items(playlist_id, video_ids)
            except Exception as e:
                # Log error but continue
                print(f"Warning: Error adding some tracks: {e}")

        return {
            "playlist_id": playlist_id,
            "playlist_url": f"https://music.youtube.com/playlist?list={playlist_id}",
            "youtube_url": f"https://www.youtube.com/playlist?list={playlist_id}",
            "tracks_added": len(video_ids),
            "tracks_total": len(queries),
            "details": results,
        }

    def _select_best_match(self, search_results: list, query: str) -> Optional[Dict]:
        """
        Select the best match from search results.

        Prefers:
        - Exact title matches
        - Non-remix versions
        - Non-live versions
        - Official/topic channels
        """
        if not search_results:
            return None

        query_lower = query.lower()

        # Score each result
        scored_results = []
        for result in search_results:
            score = 0
            title_lower = result.get("title", "").lower()

            # Exact title match
            if query_lower in title_lower:
                score += 10

            # Penalize remixes
            if any(word in title_lower for word in ["remix", "rmx", "rework", "edit"]):
                score -= 5

            # Penalize live versions
            if "live" in title_lower:
                score -= 3

            # Penalize covers
            if "cover" in title_lower:
                score -= 4

            # Prefer official/topic channels
            artists = result.get("artists", [])
            if artists and any("topic" in a.get("name", "").lower() for a in artists):
                score += 2

            # Prefer explicit matches if in query
            if "explicit" in query_lower and result.get("isExplicit"):
                score += 1

            scored_results.append((score, result))

        # Sort by score and return best match
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return scored_results[0][1] if scored_results else None

    def search_tracks_detailed(self, queries: list[str]) -> Dict[str, list]:
        """
        Search for tracks and return detailed results for each query.

        Args:
            queries: List of search queries

        Returns:
            Dictionary mapping query to list of detailed results
        """
        results = {}

        for query in queries:
            try:
                search_results = self.ytmusic.search(query, filter="songs", limit=5)

                detailed_results = []
                for item in search_results:
                    detailed_results.append(
                        {
                            "videoId": item.get("videoId"),
                            "title": item.get("title"),
                            "artists": [a["name"] for a in item.get("artists", [])],
                            "album": item.get("album", {}).get("name"),
                            "duration": item.get("duration"),
                            "isExplicit": item.get("isExplicit", False),
                            "thumbnails": item.get("thumbnails", []),
                            # Detect remix/live/cover
                            "isRemix": any(
                                word in item.get("title", "").lower()
                                for word in ["remix", "rmx", "rework", "edit"]
                            ),
                            "isLive": "live" in item.get("title", "").lower(),
                            "isCover": "cover" in item.get("title", "").lower(),
                        }
                    )

                results[query] = detailed_results
            except Exception as e:
                results[query] = {"error": str(e)}

        return results
