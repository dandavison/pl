#!/usr/bin/env python3
"""
Extract YouTube Music browser authentication using your default browser.
This version uses your existing browser session instead of automated login.
"""

import json
import sys
import webbrowser
from pathlib import Path
from typing import Dict, Optional


def extract_from_existing_session() -> Optional[Dict[str, str]]:
    """
    Guide user to extract headers from their existing browser session.
    """
    print("=" * 60)
    print("🎵 YouTube Music Browser Authentication Extractor")
    print("=" * 60)
    print("\n✅ Using your existing browser session (no login needed)")
    print("\nSteps:")
    print("1. I'll open YouTube Music in your default browser")
    print("2. Make sure you're already logged in")
    print("3. Open Developer Tools (F12 or Cmd+Option+I on Mac)")
    print("4. Go to the Network tab")
    print("5. Click on 'Library' or scroll down the page")
    print("6. Find a POST request to 'browse' endpoint")
    print("7. Right-click it and copy request headers")
    print("\n" + "=" * 60)

    # Ask user to confirm
    input("Press Enter to open YouTube Music in your browser...")

    # Open YouTube Music
    webbrowser.open("https://music.youtube.com")

    print("\n📋 After copying the headers, paste them below.")
    print("   (Press Enter twice when done)")
    print("-" * 60)

    # Collect headers
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
            lines.append(line)
        except (EOFError, KeyboardInterrupt):
            break

    if not lines or all(not line for line in lines):
        return None

    # Parse headers
    headers_text = "\n".join(lines)
    headers = {}

    for line in lines:
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers[key.lower()] = value

    # Extract required headers for ytmusicapi
    required_headers = {
        "User-Agent": headers.get("user-agent", ""),
        "Accept": "*/*",
        "Accept-Language": headers.get("accept-language", "en-US,en;q=0.5"),
        "Content-Type": "application/json",
        "X-Goog-AuthUser": headers.get("x-goog-authuser", "0"),
        "x-origin": "https://music.youtube.com",
        "Cookie": headers.get("cookie", "")
    }

    # Check if we have the essential cookie
    if not required_headers["Cookie"]:
        print("❌ No cookie found in headers. Make sure you:")
        print("   - Are logged in to YouTube Music")
        print("   - Copied headers from a POST request")
        return None

    return required_headers


def save_browser_json(headers: Dict[str, str], filepath: str = "browser.json") -> None:
    """Save headers to browser.json file."""
    with open(filepath, 'w') as f:
        json.dump(headers, f, indent=2)
    print(f"\n💾 Saved browser authentication to {filepath}")


def validate_browser_auth(filepath: str = "browser.json") -> bool:
    """Test if the browser auth works."""
    try:
        from ytmusicapi import YTMusic

        print("\n🔍 Testing authentication...")
        ytmusic = YTMusic(filepath)

        # Try a simple search
        results = ytmusic.search("test", limit=1)

        if results:
            print("✅ Authentication is working!")

            # Try to get user info
            try:
                playlists = ytmusic.get_library_playlists(limit=1)
                print("✅ Can access your library")
            except:
                print("⚠️  Can search but not access library (might be normal)")

            return True
        else:
            print("⚠️  Auth saved but search returned no results")
            return False

    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False


def main():
    """Main function."""
    print("\n🔒 Note: Google blocks automated browser login for security")
    print("   This tool uses your EXISTING browser session instead\n")

    # Extract headers
    headers = extract_from_existing_session()

    if not headers:
        print("\n❌ Failed to extract headers")
        print("\nTroubleshooting:")
        print("1. Make sure you're logged in to YouTube Music")
        print("2. Copy from a POST request (not GET)")
        print("3. In Firefox: Right-click → Copy → Copy Request Headers")
        print("4. In Chrome: Click request → Headers tab → Copy all Request Headers")
        return 1

    # Save to browser.json
    save_browser_json(headers)

    # Validate
    if validate_browser_auth():
        print("\n🎉 Success! You can now use browser authentication")
        print("\nUsage with MCP:")
        print("  - Use ytm_create_playlist_browser (no quotas)")
        print("  - Use ytm_search_browser (no quotas)")
        print("\nDirect usage:")
        print("  from ytmusicapi import YTMusic")
        print("  ytmusic = YTMusic('browser.json')")
        return 0
    else:
        print("\n⚠️  Headers saved but validation failed")
        print("The headers might still work - try using them anyway")
        return 1


if __name__ == "__main__":
    sys.exit(main())
