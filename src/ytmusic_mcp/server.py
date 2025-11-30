import logging
from pathlib import Path
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

from .browser_auth import BrowserAuthManager, BrowserPlaylistManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("YouTubeMusic")
browser_auth_manager = BrowserAuthManager()

# Version for tracking updates
VERSION = "1.2.0"


@mcp.tool()
def version() -> Dict[str, Any]:
    """
    Get the version of the MCP server.

    Returns:
        Version information
    """
    return {"version": VERSION, "message": f"YouTube Music MCP Server v{VERSION}"}


@mcp.tool()
def get_setup_instructions() -> Dict[str, Any]:
    """
    Get instructions for connecting your YouTube Music account.

    Returns:
        Instructions and current status
    """

    # Check if already configured
    config_path = Path.home() / ".config" / "ytmusic-mcp" / "browser.json"
    is_configured = browser_auth_manager.is_authenticated()

    instructions = """
To set up browser authentication (no API quotas!):

1. Open Chrome and go to https://music.youtube.com
2. Make sure you're logged in to your Google account
3. Press F12 for Developer Tools and click the "Network" tab
4. Back in YouTube Music click on "Library" or "Home" to generate some requests
5. Find a request that says "browse" in the "Name" column

For Chrome:
- Click on the "browse" request
- In the Headers tab, scroll to "Request Headers"
- Copy everything from "accept: */*" to the end of that section
- OR right-click → Copy → Copy as fetch (Node.js) and extract just the headers object

For Firefox:
- Right-click on the "browse" request → Copy → Copy Request Headers

6. Use setup_youtube_music with the copied headers

This gives you unlimited playlist creation with no daily limits!
"""

    return {
        "configured": is_configured,
        "config_path": str(config_path),
        "instructions": instructions,
    }


@mcp.tool()
def setup_youtube_music(headers_raw: str) -> Dict[str, Any]:
    """
    Connect your YouTube Music account for unlimited playlist creation.

    Args:
        headers_raw: The request headers copied from your browser

    Returns:
        Setup status
    """
    import json
    import sys

    try:
        print(f"[v{VERSION}] Processing headers...", file=sys.stderr)

        # First try to parse as JSON (Chrome's "Copy as fetch" format)
        try:
            headers_dict = json.loads(headers_raw)
            print("Detected JSON format", file=sys.stderr)
        except json.JSONDecodeError:
            # Parse as raw headers text (Firefox format or Chrome's raw headers)
            print("Parsing as raw headers text", file=sys.stderr)
            headers_dict = {}

            for line in headers_raw.split("\n"):
                line = line.strip()
                if line and ":" in line:
                    key, value = line.split(":", 1)
                    # Normalize header names to match what ytmusicapi expects
                    key = key.strip()
                    if key.lower() == "cookie":
                        headers_dict["Cookie"] = value.strip()
                    elif key.lower() == "authorization":
                        headers_dict["Authorization"] = value.strip()
                    elif key.lower() == "x-goog-authuser":
                        headers_dict["X-Goog-AuthUser"] = value.strip()
                    elif key.lower() == "content-type":
                        headers_dict["Content-Type"] = value.strip()
                    elif key.lower() == "accept":
                        headers_dict["Accept"] = value.strip()
                    elif key.lower() == "x-origin":
                        headers_dict["x-origin"] = value.strip()

        print(f"Found {len(headers_dict)} headers", file=sys.stderr)

        # Check for required fields
        if "Cookie" not in headers_dict:
            return {
                "success": False,
                "error": "No Cookie header found. Make sure you copied from an authenticated POST request.",
            }

        # Check for required cookie
        if "__Secure-3PAPISID" not in headers_dict.get("Cookie", ""):
            print("Warning: Missing __Secure-3PAPISID cookie", file=sys.stderr)

        # Create browser.json structure matching ytmusicapi's expected format
        browser_json = {
            "Accept": headers_dict.get("Accept", "*/*"),
            "Authorization": headers_dict.get("Authorization", ""),
            "Content-Type": headers_dict.get("Content-Type", "application/json"),
            "X-Goog-AuthUser": headers_dict.get("X-Goog-AuthUser", "0"),
            "x-origin": headers_dict.get("x-origin", "https://music.youtube.com"),
            "Cookie": headers_dict["Cookie"],
        }

        # Remove empty Authorization if not present
        if not browser_json["Authorization"]:
            del browser_json["Authorization"]

        # Save to user config directory
        config_dir = Path.home() / ".config" / "ytmusic-mcp"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "browser.json"
        print(f"Saving to {config_path}", file=sys.stderr)

        with open(config_path, "w") as f:
            json.dump(browser_json, f, indent=2)
        print("Successfully saved browser.json", file=sys.stderr)

        return {
            "success": True,
            "config_path": str(config_path),
            "message": "YouTube Music connected successfully! You can now create playlists.",
        }

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


@mcp.tool()
def test_connection() -> Dict[str, Any]:
    """
    Test your YouTube Music connection.

    Returns:
        Connection status
    """
    if not browser_auth_manager.is_authenticated():
        return {
            "valid": False,
            "message": "YouTube Music not connected. Please run setup_youtube_music first.",
        }

    return browser_auth_manager.validate_auth()


@mcp.tool()
def search_songs(queries: List[str]) -> Dict[str, Any]:
    """
    Search for songs on YouTube Music.

    Args:
        queries: List of song names to search for

    Returns:
        Search results for each query
    """
    try:
        if not browser_auth_manager.is_authenticated():
            return {
                "error": "YouTube Music not connected. Please run setup_youtube_music first."
            }

        ytmusic = browser_auth_manager.get_ytmusic()
        manager = BrowserPlaylistManager(ytmusic)
        return manager.search_tracks_detailed(queries)
    except Exception as e:
        logger.error(f"Error searching with browser auth: {e}")
        return {"error": str(e)}


@mcp.tool()
def create_playlist(
    title: str, description: str, tracks: List[str]
) -> Dict[str, Any]:
    """
    Create a YouTube Music playlist.

    Args:
        title: Name of your playlist
        description: Description of your playlist
        tracks: List of song names to add

    Returns:
        Playlist creation results
    """
    try:
        if not browser_auth_manager.is_authenticated():
            return {
                "error": "YouTube Music not connected. Please run setup_youtube_music first."
            }

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
