import pytest
from unittest.mock import MagicMock
from ytmusic_mcp.playlist import PlaylistManager

@pytest.fixture
def mock_ytmusic():
    return MagicMock()

def test_create_playlist_batch(mock_ytmusic):
    manager = PlaylistManager(mock_ytmusic)

    # Mock create_playlist
    mock_ytmusic.create_playlist.return_value = "playlist-id-123"

    # Mock search
    # Query 1: Found
    # Query 2: Not found
    def search_side_effect(query, filter, limit):
        if query == "Found Song":
            return [{"videoId": "vid-1", "title": "Found Song", "artists": [{"name": "Artist 1"}]}]
        return []

    mock_ytmusic.search.side_effect = search_side_effect

    result = manager.create_playlist_batch("My Playlist", "Desc", ["Found Song", "Missing Song"])

    assert result["playlist_id"] == "playlist-id-123"
    assert result["track_count"] == 1
    assert len(result["details"]) == 2

    # Verify add_playlist_items called with correct IDs
    mock_ytmusic.add_playlist_items.assert_called_once_with("playlist-id-123", ["vid-1"])

    # Check details
    assert result["details"][0]["found"] is True
    assert result["details"][0]["title"] == "Found Song"
    assert result["details"][1]["found"] is False

