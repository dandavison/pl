import json
import logging
from typing import List, Dict, Any
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from .browser_auth import BrowserAuthManager, BrowserPlaylistManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("YouTubeMusic")
browser_auth_manager = BrowserAuthManager()




@mcp.tool()
def ytm_get_browser_auth_instructions() -> Dict[str, Any]:
    """
    Get instructions for setting up browser authentication.
    This avoids API quotas completely.

    Returns:
        Instructions and current status
    """
    from pathlib import Path

    # Check if already configured
    config_path = Path.home() / ".config" / "ytmusic-mcp" / "browser.json"
    is_configured = browser_auth_manager.is_authenticated()

    instructions = """
To set up browser authentication (no API quotas!):

1. Open Chrome and go to https://music.youtube.com
2. Make sure you're logged in to your Google account
3. Press F12 for Developer Tools and then inside the dev tools click the "Network" tab
4. Back in YouTube Music click on "Library" or "Home" to generate some requests
5. In the dev tools, find a request that says "browse" in the "Name" column
6. Right-click on it → Copy → Copy as cURL
7. Send the cURL command using ytm_setup_browser_auth_from_curl

This gives you unlimited playlist creation with no daily limits!
"""

    return {
        "configured": is_configured,
        "config_path": str(config_path),
        "instructions": instructions
    }

@mcp.tool()
def ytm_setup_browser_auth_from_curl(curl_command: str) -> Dict[str, Any]:
    """
    Set up browser authentication using a cURL command from Chrome DevTools.
    This is the recommended method to avoid API quotas.

    Args:
        curl_command: The full cURL command copied from Chrome DevTools

    Returns:
        Setup status and result
    """
    import re
    from pathlib import Path

    try:
        # Parse the cURL command
        # Join lines and clean up backslashes
        curl_text = " ".join(curl_command.split("\\\n"))
        curl_text = " ".join(curl_text.split("\\"))

        headers = {}

        # Extract headers
        header_pattern = r"-H\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(header_pattern, curl_text):
            header_line = match.group(1)
            if ":" in header_line:
                key, value = header_line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        # Extract cookies
        cookie_pattern = r"-b\s+['\"]([^'\"]+)['\"]"
        cookie_match = re.search(cookie_pattern, curl_text)
        if cookie_match:
            headers["cookie"] = cookie_match.group(1).strip()

        if not headers.get("cookie"):
            return {
                "success": False,
                "error": "No cookies found in cURL command. Make sure you're logged in and copied from a POST request."
            }

        # Create browser.json structure
        browser_json = {
            "User-Agent": headers.get("user-agent", "Mozilla/5.0"),
            "Accept": headers.get("accept", "*/*"),
            "Accept-Language": headers.get("accept-language", "en-US,en;q=0.9"),
            "Content-Type": headers.get("content-type", "application/json"),
            "X-Goog-AuthUser": headers.get("x-goog-authuser", "0"),
            "x-origin": headers.get("x-origin", "https://music.youtube.com"),
            "Cookie": headers["cookie"]
        }

        if "authorization" in headers:
            browser_json["Authorization"] = headers["authorization"]

        # Save to user config directory
        config_dir = Path.home() / ".config" / "ytmusic-mcp"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "browser.json"

        import json
        with open(config_path, "w") as f:
            json.dump(browser_json, f, indent=2)

        # Test it
        validation = browser_auth_manager.validate_auth()

        return {
            "success": True,
            "config_path": str(config_path),
            "valid": validation.get("valid", False),
            "message": "Browser authentication configured successfully! You can now create unlimited playlists."
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


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
