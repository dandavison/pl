import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .auth import AuthManager
from .youtube_api import YouTubeAPI, PlaylistBuilder
from .browser_auth import BrowserAuthManager, BrowserPlaylistManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("YouTubeMusic")
auth_manager = AuthManager()
browser_auth_manager = BrowserAuthManager()

@mcp.tool()
def ytm_get_auth_url(client_id: str, client_secret: str) -> dict:
    """
    Step 1 of Authentication: Get the URL and code to authenticate with Google.
    You must provide your own Google Cloud Client ID and Secret.
    Returns a dict with 'verification_url', 'user_code', and 'device_code'.
    Provide the 'verification_url' and 'user_code' to the user.
    Keep the 'device_code' for the next step.
    """
    return auth_manager.start_oauth(client_id, client_secret)

@mcp.tool()
def ytm_authenticate(device_code: str) -> str:
    """
    Step 2 of Authentication: Complete the process using the device_code from Step 1.
    Call this AFTER the user has visited the URL and authorized the app.
    """
    return auth_manager.complete_oauth(device_code)

@mcp.tool()
def ytm_search_tracks(queries: List[str]) -> Dict[str, Any]:
    """
    Search for multiple tracks on YouTube and return detailed results for each query.
    This allows the LLM to select the best match based on criteria like:
    - Original recordings vs remixes
    - Original versions vs remasters
    - Official uploads vs user uploads
    - View count and popularity

    Args:
        queries: A list of search queries (e.g. ["Song Name Artist Name"])

    Returns:
        A dictionary mapping each query to a list of search results with metadata.
    """
    try:
        # Load OAuth token from file
        oauth_path = Path("oauth.json")
        if not oauth_path.exists():
            return {"error": "Not authenticated. Please run authentication flow first."}

        with open(oauth_path, 'r') as f:
            oauth_data = json.load(f)

        access_token = oauth_data.get("access_token")
        if not access_token:
            return {"error": "No access token found in oauth.json"}

        youtube_api = YouTubeAPI(access_token)
        builder = PlaylistBuilder(youtube_api)
        return builder.search_tracks_batch(queries)
    except Exception as e:
        logger.error(f"Error searching tracks: {e}")
        return {"error": str(e)}

@mcp.tool()
def ytm_create_playlist_from_ids(title: str, description: str, video_ids: List[str]) -> Dict[str, Any]:
    """
    Create a YouTube/YouTube Music playlist with specific video IDs.
    Use this after searching for tracks and selecting the best matches.

    Args:
        title: The title of the playlist
        description: The description of the playlist
        video_ids: List of YouTube video IDs to add to the playlist

    Returns:
        A dictionary with playlist_id, URLs, and success metrics
    """
    try:
        # Load OAuth token from file
        oauth_path = Path("oauth.json")
        if not oauth_path.exists():
            return {"error": "Not authenticated. Please run authentication flow first."}

        with open(oauth_path, 'r') as f:
            oauth_data = json.load(f)

        access_token = oauth_data.get("access_token")
        if not access_token:
            return {"error": "No access token found in oauth.json"}

        youtube_api = YouTubeAPI(access_token)
        builder = PlaylistBuilder(youtube_api)
        return builder.create_playlist_from_ids(title, description, video_ids)
    except Exception as e:
        logger.error(f"Error creating playlist: {e}")
        return {"error": str(e)}

@mcp.tool()
def ytm_create_playlist_ytmusic(title: str, description: str, tracks: List[str]) -> dict:
    """
    [LEGACY] Creates a new playlist using YTMusic API (takes first search result blindly).
    Prefer using ytm_search_tracks + ytm_create_playlist_from_ids for better control.

    Args:
        title: The title of the playlist.
        description: The description of the playlist.
        tracks: A list of search queries (e.g. "Song Name Artist Name") for the tracks to add.

    Returns:
        A dictionary containing the playlist URL and a summary of added tracks.
    """
    try:
        from .playlist import PlaylistManager
        ytmusic = auth_manager.get_ytmusic()
        manager = PlaylistManager(ytmusic)
        return manager.create_playlist_batch(title, description, tracks)
    except Exception as e:
        logger.error(f"Error creating playlist with ytmusicapi: {e}")
        return {"error": str(e)}

@mcp.tool()
def ytm_setup_browser_auth(headers_raw: str) -> str:
    """
    Set up browser authentication using headers from YouTube Music.
    This avoids API quotas by using the same auth as the web interface.

    To get headers:
    1. Open YouTube Music in browser (music.youtube.com)
    2. Open Developer Tools (F12)
    3. Go to Network tab
    4. Find a POST request to /browse
    5. Copy request headers

    Args:
        headers_raw: Raw headers copied from browser

    Returns:
        Success or error message
    """
    try:
        return browser_auth_manager.setup_from_headers(headers_raw)
    except Exception as e:
        return f"Error setting up browser auth: {e}"

@mcp.tool()
def ytm_validate_browser_auth() -> Dict[str, Any]:
    """
    Validate that browser authentication is working.

    Returns:
        Dictionary with validation status and details
    """
    if not browser_auth_manager.is_authenticated():
        return {
            "valid": False,
            "message": "No browser authentication found. Run ytm_setup_browser_auth first."
        }

    return browser_auth_manager.validate_auth()

@mcp.tool()
def ytm_search_browser(queries: List[str]) -> Dict[str, Any]:
    """
    Search for tracks using browser authentication (no API quotas).
    Returns detailed results for intelligent selection.

    Args:
        queries: List of search queries

    Returns:
        Dictionary mapping queries to search results
    """
    try:
        if not browser_auth_manager.is_authenticated():
            return {"error": "Browser auth not configured. Run ytm_setup_browser_auth first."}

        ytmusic = browser_auth_manager.get_ytmusic()
        manager = BrowserPlaylistManager(ytmusic)
        return manager.search_tracks_detailed(queries)
    except Exception as e:
        logger.error(f"Error searching with browser auth: {e}")
        return {"error": str(e)}

@mcp.tool()
def ytm_create_playlist_browser(title: str, description: str, tracks: List[str]) -> Dict[str, Any]:
    """
    Create playlist using browser authentication (no API quotas).
    This method searches for tracks and adds the best matches automatically.

    Args:
        title: Playlist title
        description: Playlist description
        tracks: List of search queries

    Returns:
        Dictionary with playlist details and results
    """
    try:
        if not browser_auth_manager.is_authenticated():
            return {"error": "Browser auth not configured. Run ytm_setup_browser_auth first."}

        ytmusic = browser_auth_manager.get_ytmusic()
        manager = BrowserPlaylistManager(ytmusic)
        return manager.search_and_create_playlist(title, description, tracks)
    except Exception as e:
        logger.error(f"Error creating playlist with browser auth: {e}")
        return {"error": str(e)}

def main():
    mcp.run()

if __name__ == "__main__":
    main()
