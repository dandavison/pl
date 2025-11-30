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
VERSION = "1.3.0"


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
3. Press F12 for Developer Tools → click the "Network" tab
4. In YouTube Music, click "Library" or "Home" to generate requests
5. Find a request named "browse" (Status 200)
6. Right-click on it → "Copy as fetch (Node.js)"
7. Save the copied text to: ~/.config/ytmusic-mcp/headers.txt
8. Run setup_youtube_music_from_file

The tool will automatically extract just the headers it needs!
"""

    return {
        "configured": is_configured,
        "config_path": str(config_path),
        "instructions": instructions,
    }


@mcp.tool()
def setup_youtube_music_from_file() -> Dict[str, Any]:
    """
    Connect your YouTube Music account using headers from a file.

    Put your headers in ~/.config/ytmusic-mcp/headers.txt first.

    Returns:
        Setup status
    """
    import sys

    headers_file = Path.home() / ".config" / "ytmusic-mcp" / "headers.txt"

    if not headers_file.exists():
        headers_file.parent.mkdir(parents=True, exist_ok=True)
        return {
            "success": False,
            "error": f"Please save your browser headers to {headers_file} first",
            "instructions": "Copy the Request Headers from Chrome DevTools and save them to the file above",
        }

    try:
        headers_raw = headers_file.read_text()
        print(
            f"[v{VERSION}] Read {len(headers_raw)} chars from headers.txt",
            file=sys.stderr,
        )

        # Process the headers using the same logic
        result = setup_youtube_music(headers_raw)

        # Delete the headers file after successful setup for security
        if result.get("success"):
            headers_file.unlink()
            print("Deleted headers.txt for security", file=sys.stderr)

        return result
    except Exception as e:
        import traceback

        traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


def _parse_fetch_headers(raw_text: str) -> Dict[str, str]:
    """
    Parse headers from various formats:
    - Chrome's 'Copy as fetch (Node.js)'
    - cURL command
    - Raw header lines
    """
    import json
    import re
    import sys

    headers_dict = {}

    # Method 1: Try to extract headers from fetch() format
    headers_match = re.search(
        r'"headers"\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', raw_text, re.DOTALL
    )

    if headers_match:
        headers_str = "{" + headers_match.group(1) + "}"
        print("Detected fetch format, extracting headers...", file=sys.stderr)

        try:
            headers_obj = json.loads(headers_str)
            print(
                f"Parsed {len(headers_obj)} headers from fetch format", file=sys.stderr
            )
            return headers_obj
        except json.JSONDecodeError as e:
            print(f"Failed to parse headers JSON: {e}", file=sys.stderr)

    # Method 2: Try to parse cURL format
    if raw_text.strip().startswith("curl "):
        print("Detected cURL format", file=sys.stderr)

        # Extract -H headers
        header_matches = re.findall(r"-H\s+'([^']+)'", raw_text)
        for header in header_matches:
            if ": " in header:
                key, value = header.split(": ", 1)
                headers_dict[key.strip()] = value.strip()

        # Extract -b cookies (cURL's cookie flag)
        cookie_match = re.search(r"-b\s+'([^']+)'", raw_text)
        if cookie_match:
            headers_dict["cookie"] = cookie_match.group(1)

        print(f"Parsed {len(headers_dict)} headers from cURL format", file=sys.stderr)
        return headers_dict

    # Method 3: Fallback to raw header lines
    print("Parsing as raw header lines", file=sys.stderr)
    for line in raw_text.split("\n"):
        line = line.strip().strip(",").strip('"')
        if ": " in line and not line.startswith("//"):
            if line.startswith('"') or "': '" in line:
                match = re.match(r'"?([^"]+)"?\s*:\s*"(.+)"$', line)
                if match:
                    headers_dict[match.group(1)] = match.group(2)
            else:
                key, value = line.split(": ", 1)
                headers_dict[key.strip()] = value.strip()

    return headers_dict


def _normalize_headers(headers_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Extract and normalize only the required headers for ytmusicapi.

    Takes headers with any casing and returns the properly-cased subset needed.
    """
    # Create a lowercase lookup
    lower_headers = {k.lower(): v for k, v in headers_dict.items()}

    result = {
        "Accept": lower_headers.get("accept", "*/*"),
        "Content-Type": lower_headers.get("content-type", "application/json"),
        "X-Goog-AuthUser": lower_headers.get("x-goog-authuser", "0"),
        "x-origin": lower_headers.get("x-origin", "https://music.youtube.com"),
    }

    # Cookie is required
    if "cookie" in lower_headers:
        result["Cookie"] = lower_headers["cookie"]

    # Authorization is optional but include if present
    if "authorization" in lower_headers:
        result["Authorization"] = lower_headers["authorization"]

    return result


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
    import time

    start_time = time.time()

    try:
        print(f"[v{VERSION}] Starting setup_youtube_music", file=sys.stderr)
        print(f"Input length: {len(headers_raw)} chars", file=sys.stderr)

        # Parse the headers (handles fetch format, JSON, or raw headers)
        headers_dict = _parse_fetch_headers(headers_raw)
        print(f"Parsed {len(headers_dict)} raw headers", file=sys.stderr)

        # Normalize to just the required headers with correct casing
        browser_json = _normalize_headers(headers_dict)
        print(f"Normalized to {len(browser_json)} headers", file=sys.stderr)

        # Check for required Cookie
        if "Cookie" not in browser_json:
            return {
                "success": False,
                "error": "No Cookie header found. Make sure you copied from an authenticated request.",
            }

        # Check for required cookie values
        cookie = browser_json.get("Cookie", "")
        if "__Secure-3PAPISID" not in cookie:
            print("Warning: Missing __Secure-3PAPISID cookie", file=sys.stderr)

        # Save to user config directory
        config_dir = Path.home() / ".config" / "ytmusic-mcp"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "browser.json"
        print(f"Saving to {config_path}", file=sys.stderr)

        with open(config_path, "w") as f:
            json.dump(browser_json, f, indent=2)

        elapsed = time.time() - start_time
        print(f"Successfully saved browser.json in {elapsed:.2f}s", file=sys.stderr)

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
def create_playlist(title: str, description: str, tracks: List[str]) -> Dict[str, Any]:
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
