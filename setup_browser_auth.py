#!/usr/bin/env python3
"""
Manual setup for browser authentication.
Paste headers when prompted or pass as argument.
"""

import sys
import json
from pathlib import Path
import ytmusicapi


def setup_browser_auth(headers_raw: str = None, output_file: str = "browser.json"):
    """
    Set up browser authentication from headers.
    
    Args:
        headers_raw: Raw headers string (if None, will prompt)
        output_file: Output filename for browser auth
    """
    if headers_raw is None:
        print("=" * 60)
        print("🎵 YouTube Music Browser Authentication Setup")
        print("=" * 60)
        print("\nTo get your headers:")
        print("1. Open music.youtube.com in your browser")
        print("2. Open Developer Tools (F12)")
        print("3. Go to Network tab")
        print("4. Click on Library or scroll down")
        print("5. Find a POST request to /browse")
        print("6. Copy request headers (right-click > Copy > Copy Request Headers)")
        print("\nPaste headers below (press Enter twice when done):")
        print("-" * 60)
        
        lines = []
        while True:
            try:
                line = input()
                if not line and lines and not lines[-1]:
                    break
                lines.append(line)
            except EOFError:
                break
        
        headers_raw = "\n".join(lines[:-1] if lines and not lines[-1] else lines)
    
    if not headers_raw:
        print("❌ No headers provided")
        return False
    
    try:
        # Use ytmusicapi's setup to parse headers
        auth_json = ytmusicapi.setup(headers_raw=headers_raw)
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(auth_json)
        
        print(f"\n✅ Browser authentication saved to {output_file}")
        
        # Test it
        print("\n🔍 Testing authentication...")
        ytmusic = ytmusicapi.YTMusic(output_file)
        results = ytmusic.search("test", limit=1)
        
        if results:
            print("✅ Authentication is working!")
            print("\nYou can now use browser auth with:")
            print("  - MCP tools: ytm_create_playlist_browser, ytm_search_browser")
            print("  - Direct API: YTMusic('browser.json')")
        else:
            print("⚠️  Authentication saved but search returned no results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up browser auth: {e}")
        print("\nCommon issues:")
        print("- Make sure you're logged in to YouTube Music")
        print("- Copy headers from a POST request (not GET)")
        print("- Include all headers from 'accept' to the end")
        return False


if __name__ == "__main__":
    # Check if headers were passed as argument
    if len(sys.argv) > 1:
        # Join all arguments in case headers were split
        headers = " ".join(sys.argv[1:])
        success = setup_browser_auth(headers)
    else:
        success = setup_browser_auth()
    
    sys.exit(0 if success else 1)
