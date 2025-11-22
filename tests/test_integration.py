"""Integration tests for the MCP server with real API calls."""

import pytest
import asyncio
import json
from pathlib import Path
from ytmusic_mcp.server import mcp


def has_valid_oauth():
    """Check if valid OAuth credentials are available."""
    oauth_path = Path("oauth.json")
    if not oauth_path.exists():
        return False

    try:
        with open(oauth_path, 'r') as f:
            oauth_data = json.load(f)
        return "access_token" in oauth_data
    except:
        return False


@pytest.mark.skipif(not has_valid_oauth(), reason="No valid OAuth credentials found")
class TestMCPIntegration:
    """Integration tests that require valid OAuth credentials."""

    @pytest.mark.asyncio
    async def test_search_tracks_integration(self):
        """Test searching for tracks with real API."""
        result = await mcp.call_tool(
            "ytm_search_tracks",
            {"queries": ["The Beatles Yesterday"]}
        )

        # Extract result from tuple format
        if isinstance(result, tuple) and len(result) >= 2:
            search_data = result[1].get('result', {})
        else:
            pytest.fail("Unexpected result format from search")

        assert "The Beatles Yesterday" in search_data
        results = search_data["The Beatles Yesterday"]

        # Should have multiple results
        assert isinstance(results, list)
        assert len(results) > 0

        # Check first result has expected fields
        first = results[0]
        assert "videoId" in first
        assert "title" in first
        assert "channel" in first
        assert "url" in first
        assert "isRemix" in first
        assert "isRemaster" in first

    @pytest.mark.asyncio
    async def test_tools_available(self):
        """Test that all expected tools are available."""
        tools = await mcp.list_tools()
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            "ytm_get_auth_url",
            "ytm_authenticate",
            "ytm_search_tracks",
            "ytm_create_playlist_from_ids",
            "ytm_create_playlist_ytmusic"
        ]

        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found"

    @pytest.mark.asyncio
    async def test_search_with_multiple_queries(self):
        """Test searching for multiple tracks at once."""
        queries = [
            "Pink Floyd Comfortably Numb",
            "Led Zeppelin Stairway to Heaven"
        ]

        result = await mcp.call_tool(
            "ytm_search_tracks",
            {"queries": queries}
        )

        # Extract result
        if isinstance(result, tuple) and len(result) >= 2:
            search_data = result[1].get('result', {})
        else:
            pytest.fail("Unexpected result format")

        # Check we got results for both queries
        for query in queries:
            assert query in search_data
            assert len(search_data[query]) > 0

    @pytest.mark.asyncio
    async def test_remix_detection(self):
        """Test that remixes are properly detected."""
        # Search for something likely to have remixes
        result = await mcp.call_tool(
            "ytm_search_tracks",
            {"queries": ["Daft Punk Around the World Remix"]}
        )

        if isinstance(result, tuple) and len(result) >= 2:
            search_data = result[1].get('result', {})
        else:
            pytest.fail("Unexpected result format")

        results = search_data.get("Daft Punk Around the World Remix", [])

        # At least one result should be detected as a remix
        has_remix = any(r.get("isRemix", False) for r in results)
        assert has_remix or len(results) == 0, "Should detect remix in results or have no results"


@pytest.mark.skipif(has_valid_oauth(), reason="OAuth credentials available, no need to test without")
class TestWithoutAuth:
    """Tests for behavior when OAuth is not available."""

    @pytest.mark.asyncio
    async def test_search_without_auth(self):
        """Test that search fails gracefully without auth."""
        result = await mcp.call_tool(
            "ytm_search_tracks",
            {"queries": ["test"]}
        )

        # Should get an error
        if isinstance(result, tuple) and len(result) >= 2:
            data = result[1].get('result', {})
        else:
            data = {}

        assert "error" in data
