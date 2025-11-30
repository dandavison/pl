"""
Test MCP tools directly, simulating user interactions.
These are "live" tests that actually call the tools.
"""

import json
import pytest
from pathlib import Path
from ytmusic_mcp.server import mcp


@pytest.mark.asyncio
async def test_version_tool():
    """Test that version tool returns expected format."""
    result = await mcp.call_tool("version", {})
    
    # Result is a tuple (content_list, metadata)
    content_list, metadata = result
    
    # Extract the actual result from metadata
    actual_result = metadata.get("result", {})
    
    assert "version" in actual_result
    assert "message" in actual_result
    assert actual_result["version"].startswith("1.")
    print(f"Version: {actual_result['version']}")


@pytest.mark.asyncio
async def test_get_setup_instructions():
    """Test getting setup instructions."""
    result = await mcp.call_tool("get_setup_instructions", {})
    
    content_list, metadata = result
    actual_result = metadata.get("result", {})
    
    assert "instructions" in actual_result
    assert "config_path" in actual_result
    assert "configured" in actual_result
    
    print(f"Configured: {actual_result['configured']}")
    print(f"Config path: {actual_result['config_path']}")


@pytest.mark.asyncio
async def test_setup_with_minimal_headers():
    """Test setup with minimal valid headers."""
    # Minimal headers that should work
    headers_raw = """accept: */*
authorization: SAPISIDHASH test_token
cookie: __Secure-3PAPISID=test_value; other=cookies
x-goog-authuser: 0
content-type: application/json"""
    
    result = await mcp.call_tool("setup_youtube_music", {"headers_raw": headers_raw})
    
    content_list, metadata = result
    actual_result = metadata.get("result", {})
    
    assert "success" in actual_result
    assert actual_result["success"] is True
    assert "config_path" in actual_result
    
    print(f"Setup result: {actual_result.get('message')}")
    
    # Clean up test file
    config_path = Path(actual_result["config_path"])
    if config_path.exists():
        config_path.unlink()
        print(f"Cleaned up test config: {config_path}")


@pytest.mark.asyncio
async def test_setup_with_invalid_headers():
    """Test setup with invalid headers (missing cookie)."""
    headers_raw = """accept: */*
content-type: application/json"""
    
    result = await mcp.call_tool("setup_youtube_music", {"headers_raw": headers_raw})
    
    content_list, metadata = result
    actual_result = metadata.get("result", {})
    
    assert "success" in actual_result
    assert actual_result["success"] is False
    assert "error" in actual_result
    assert "Cookie" in actual_result["error"]
    
    print(f"Expected error: {actual_result['error']}")


@pytest.mark.asyncio
async def test_setup_from_file_no_file():
    """Test file-based setup when file doesn't exist."""
    # Make sure file doesn't exist
    headers_file = Path.home() / ".config" / "ytmusic-mcp" / "headers.txt"
    if headers_file.exists():
        headers_file.unlink()
    
    result = await mcp.call_tool("setup_youtube_music_from_file", {})
    
    content_list, metadata = result
    actual_result = metadata.get("result", {})
    
    assert "success" in actual_result
    assert actual_result["success"] is False
    assert "error" in actual_result
    assert "headers.txt" in actual_result["error"]
    
    print(f"Expected error: {actual_result['error']}")


@pytest.mark.asyncio
async def test_setup_from_file_with_headers():
    """Test file-based setup with valid headers file."""
    # Create headers file
    headers_file = Path.home() / ".config" / "ytmusic-mcp" / "headers.txt"
    headers_file.parent.mkdir(parents=True, exist_ok=True)
    
    headers_content = """accept: */*
authorization: SAPISIDHASH test_file_token
cookie: __Secure-3PAPISID=file_test; session=active
x-goog-authuser: 0
content-type: application/json"""
    
    headers_file.write_text(headers_content)
    
    try:
        result = await mcp.call_tool("setup_youtube_music_from_file", {})
        
        content_list, metadata = result
        actual_result = metadata.get("result", {})
        
        assert "success" in actual_result
        assert actual_result["success"] is True
        
        # File should be deleted after successful setup
        assert not headers_file.exists(), "Headers file should be deleted after successful setup"
        
        print(f"File-based setup: {actual_result.get('message')}")
        
        # Clean up config
        config_path = Path(actual_result["config_path"])
        if config_path.exists():
            config_path.unlink()
            
    finally:
        # Clean up in case of failure
        if headers_file.exists():
            headers_file.unlink()


@pytest.mark.asyncio
async def test_test_connection_without_auth():
    """Test connection check without authentication."""
    # Ensure no auth file exists
    config_path = Path.home() / ".config" / "ytmusic-mcp" / "browser.json"
    if config_path.exists():
        config_path.rename(config_path.with_suffix(".json.backup"))
    
    try:
        result = await mcp.call_tool("test_connection", {})
        
        content_list, metadata = result
        actual_result = metadata.get("result", {})
        
        assert "valid" in actual_result
        assert actual_result["valid"] is False
        assert "message" in actual_result
        
        print(f"Connection test: {actual_result['message']}")
        
    finally:
        # Restore backup if it exists
        backup = config_path.with_suffix(".json.backup")
        if backup.exists():
            backup.rename(config_path)


@pytest.mark.asyncio
@pytest.mark.parametrize("query", [
    "Bohemian Rhapsody",
    "test song that doesn't exist 123456789"
])
async def test_search_songs_without_auth(query):
    """Test search without authentication - should fail gracefully."""
    # Ensure no auth
    config_path = Path.home() / ".config" / "ytmusic-mcp" / "browser.json"
    has_auth = config_path.exists()
    
    if has_auth:
        config_path.rename(config_path.with_suffix(".json.backup"))
    
    try:
        result = await mcp.call_tool("search_songs", {"queries": [query]})
        
        content_list, metadata = result
        actual_result = metadata.get("result", {})
        
        assert "error" in actual_result
        assert "not connected" in actual_result["error"].lower()
        
        print(f"Search without auth: {actual_result['error']}")
        
    finally:
        # Restore auth
        backup = config_path.with_suffix(".json.backup")
        if backup.exists():
            backup.rename(config_path)


@pytest.mark.asyncio
async def test_create_playlist_without_auth():
    """Test playlist creation without authentication."""
    # Ensure no auth
    config_path = Path.home() / ".config" / "ytmusic-mcp" / "browser.json"
    has_auth = config_path.exists()
    
    if has_auth:
        config_path.rename(config_path.with_suffix(".json.backup"))
    
    try:
        result = await mcp.call_tool("create_playlist", {
            "title": "Test Playlist",
            "description": "Test Description",
            "tracks": ["Song 1", "Song 2"]
        })
        
        content_list, metadata = result
        actual_result = metadata.get("result", {})
        
        assert "error" in actual_result
        assert "not connected" in actual_result["error"].lower()
        
        print(f"Playlist creation without auth: {actual_result['error']}")
        
    finally:
        # Restore auth
        backup = config_path.with_suffix(".json.backup")
        if backup.exists():
            backup.rename(config_path)


# Live tests that require real authentication
# These should be marked with a special marker so they can be skipped in CI

@pytest.mark.live
@pytest.mark.asyncio
async def test_full_flow_with_real_headers():
    """
    Full integration test with real headers.
    This test is skipped unless run with: pytest -m live
    
    To run this test:
    1. Get real headers from Chrome DevTools
    2. Set YOUTUBE_MUSIC_HEADERS environment variable
    3. Run: pytest tests/test_mcp_tools.py::test_full_flow_with_real_headers -m live
    """
    import os
    
    headers_raw = os.environ.get("YOUTUBE_MUSIC_HEADERS")
    if not headers_raw:
        pytest.skip("YOUTUBE_MUSIC_HEADERS environment variable not set")
    
    # Setup
    result = await mcp.call_tool("setup_youtube_music", {"headers_raw": headers_raw})
    content_list, metadata = result
    setup_result = metadata.get("result", {})
    
    assert setup_result["success"] is True
    print(f"Setup: {setup_result['message']}")
    
    # Test connection
    result = await mcp.call_tool("test_connection", {})
    content_list, metadata = result
    conn_result = metadata.get("result", {})
    
    assert conn_result["valid"] is True
    print(f"Connection: {conn_result['message']}")
    
    # Search for songs
    result = await mcp.call_tool("search_songs", {
        "queries": ["Bohemian Rhapsody", "Hotel California"]
    })
    content_list, metadata = result
    search_result = metadata.get("result", {})
    
    assert "results" in search_result
    assert len(search_result["results"]) == 2
    print(f"Found {len(search_result['results'])} songs")
    
    # Create playlist (optional - only if you want to actually create one)
    if os.environ.get("CREATE_TEST_PLAYLIST") == "yes":
        result = await mcp.call_tool("create_playlist", {
            "title": "MCP Test Playlist",
            "description": "Created by automated test",
            "tracks": ["Bohemian Rhapsody", "Hotel California"]
        })
        content_list, metadata = result
        playlist_result = metadata.get("result", {})
        
        if "playlist_id" in playlist_result:
            print(f"Created playlist: {playlist_result['playlist_id']}")
        else:
            print(f"Playlist creation result: {playlist_result}")
