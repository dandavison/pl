import logging
from typing import List
from mcp.server.fastmcp import FastMCP
from .auth import AuthManager
from .playlist import PlaylistManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("YouTubeMusic")
auth_manager = AuthManager()

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
def ytm_create_playlist(title: str, description: str, tracks: List[str]) -> dict:
    """
    Creates a new playlist and adds tracks to it.

    Args:
        title: The title of the playlist.
        description: The description of the playlist.
        tracks: A list of search queries (e.g. "Song Name Artist Name") for the tracks to add.

    Returns:
        A dictionary containing the playlist URL and a summary of added tracks.
    """
    try:
        ytmusic = auth_manager.get_ytmusic()
        manager = PlaylistManager(ytmusic)
        return manager.create_playlist_batch(title, description, tracks)
    except Exception as e:
        logger.error(f"Error creating playlist: {e}")
        return {"error": str(e)}

def main():
    mcp.run()

if __name__ == "__main__":
    main()
