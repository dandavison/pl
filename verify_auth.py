#!/usr/bin/env python3
"""
Verify OAuth authentication and YouTube API access.
This script tests that the OAuth credentials are valid and can perform
all the operations needed by the MCP server.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
import requests


def load_oauth_token() -> tuple[str, Dict[str, Any]]:
    """Load OAuth token from oauth.json file."""
    oauth_path = Path("oauth.json")
    if not oauth_path.exists():
        print("❌ oauth.json not found. Please run authentication first.")
        return None, None
    
    with open(oauth_path, 'r') as f:
        oauth_data = json.load(f)
    
    access_token = oauth_data.get("access_token")
    if not access_token:
        print("❌ No access token found in oauth.json")
        return None, oauth_data
    
    return access_token, oauth_data


def test_token_validity(access_token: str) -> bool:
    """Test if the OAuth token is valid by making a simple API call."""
    print("\n1️⃣  Testing token validity...")
    
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {"part": "snippet", "mine": "true"}
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                channel = data["items"][0]["snippet"]["title"]
                print(f"   ✅ Token is valid! Authenticated as: {channel}")
                return True
            else:
                print("   ⚠️  Token is valid but no channel found")
                return True
        elif response.status_code == 401:
            print("   ❌ Token is expired or invalid (401 Unauthorized)")
            print(f"   Response: {response.text}")
            return False
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing token: {e}")
        return False


def test_search_capability(access_token: str) -> bool:
    """Test if we can search for videos."""
    print("\n2️⃣  Testing search capability...")
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": "test",
        "type": "video",
        "maxResults": 1,
        "videoCategoryId": "10"  # Music category
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                print(f"   ✅ Search works! Found {len(data['items'])} result(s)")
                return True
            else:
                print("   ⚠️  Search works but no results found")
                return True
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error searching: {e}")
        return False


def test_playlist_permissions(access_token: str) -> bool:
    """Test if we have permissions to create playlists."""
    print("\n3️⃣  Testing playlist creation permissions...")
    
    # First, try to list existing playlists
    url = "https://www.googleapis.com/youtube/v3/playlists"
    params = {"part": "snippet", "mine": "true", "maxResults": 1}
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            print("   ✅ Can read playlists")
            
            # Check if we have the youtube scope for playlist creation
            # This is a bit indirect, but we can check by attempting a dry run
            # or checking the token info
            print("   ℹ️  Note: Actual playlist creation requires the 'youtube' scope")
            print("   ℹ️  If playlist creation fails, ensure your OAuth app has the right scopes")
            return True
        elif response.status_code == 403:
            print("   ❌ Insufficient permissions to access playlists")
            print("   Response:", response.text)
            return False
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error checking playlist permissions: {e}")
        return False


def test_video_details_access(access_token: str) -> bool:
    """Test if we can get video details (for duration, stats, etc)."""
    print("\n4️⃣  Testing video details access...")
    
    # Use a known video ID (this is "Never Gonna Give You Up" as a safe test)
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "contentDetails,statistics",
        "id": "dQw4w9WgXcQ"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                item = data["items"][0]
                duration = item["contentDetails"]["duration"]
                views = item["statistics"]["viewCount"]
                print(f"   ✅ Can get video details (duration: {duration}, views: {views})")
                return True
            else:
                print("   ⚠️  API works but video not found")
                return True
        else:
            print(f"   ❌ Cannot get video details: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error getting video details: {e}")
        return False


def check_token_expiry(oauth_data: Dict[str, Any]) -> None:
    """Check and display token expiry information."""
    print("\n5️⃣  Token expiry information...")
    
    expires_at = oauth_data.get("expires_at")
    if expires_at:
        from datetime import datetime
        expiry_time = datetime.fromtimestamp(expires_at)
        now = datetime.now()
        
        if expiry_time > now:
            time_left = expiry_time - now
            hours_left = time_left.total_seconds() / 3600
            print(f"   ⏰ Token expires at: {expiry_time}")
            print(f"   ⏱️  Time remaining: {hours_left:.1f} hours")
        else:
            print(f"   ⚠️  Token expired at: {expiry_time}")
            print("   ℹ️  The token should auto-refresh on next use")
    else:
        print("   ℹ️  No expiry information available")


def test_mcp_server_integration() -> bool:
    """Test if the MCP server can be imported and tools are available."""
    print("\n6️⃣  Testing MCP server integration...")
    
    try:
        from src.ytmusic_mcp.server import mcp
        import asyncio
        
        async def get_tools():
            return await mcp.list_tools()
        
        tools = asyncio.run(get_tools())
        tool_names = [tool.name for tool in tools]
        
        print(f"   ✅ MCP server loaded with {len(tools)} tools:")
        for name in tool_names:
            print(f"      • {name}")
        
        # Check for our new tools
        expected_tools = ["ytm_search_tracks", "ytm_create_playlist_from_ids"]
        missing_tools = [t for t in expected_tools if t not in tool_names]
        
        if missing_tools:
            print(f"   ⚠️  Missing expected tools: {missing_tools}")
            return False
        else:
            print("   ✅ All expected tools are available")
            return True
            
    except Exception as e:
        print(f"   ❌ Error loading MCP server: {e}")
        return False


def main():
    """Run all authentication verification tests."""
    print("=" * 60)
    print("🔐 YouTube Music MCP - Authentication Verification")
    print("=" * 60)
    
    # Load token
    access_token, oauth_data = load_oauth_token()
    if not access_token:
        print("\n❌ Cannot proceed without valid OAuth token")
        print("\nTo authenticate, run:")
        print("  1. Start the MCP server")
        print("  2. Use ytm_get_auth_url with your client_id and client_secret")
        print("  3. Visit the URL and enter the code")
        print("  4. Use ytm_authenticate with the device_code")
        return 1
    
    # Run tests
    results = {
        "Token Validity": test_token_validity(access_token),
        "Search API": test_search_capability(access_token),
        "Playlist Permissions": test_playlist_permissions(access_token),
        "Video Details API": test_video_details_access(access_token),
        "MCP Server": test_mcp_server_integration()
    }
    
    # Check token expiry
    check_token_expiry(oauth_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! The MCP server is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
