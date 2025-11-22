#!/usr/bin/env python3
"""
Extract YouTube Music browser authentication from Chrome's "Copy as cURL" output.
This works with modern Chrome DevTools.
"""

import json
import re
import sys
from pathlib import Path


def parse_curl_command(curl_text: str) -> dict:
    """
    Parse a cURL command copied from Chrome DevTools.
    
    Chrome's "Copy as cURL" format includes all headers in -H flags.
    """
    headers = {}
    
    # Find all -H or --header flags
    header_pattern = r"-H\s+'([^:]+):\s*([^']+)'|--header\s+'([^:]+):\s*([^']+)'"
    matches = re.findall(header_pattern, curl_text)
    
    for match in matches:
        if match[0]:  # -H format
            key, value = match[0], match[1]
        else:  # --header format
            key, value = match[2], match[3]
        
        # Normalize header names to lowercase for consistency
        headers[key.lower()] = value
    
    # Also try to find headers without quotes (some versions)
    header_pattern2 = r'-H\s+([^:]+):\s*([^\s]+)'
    matches2 = re.findall(header_pattern2, curl_text)
    for key, value in matches2:
        if key.lower() not in headers:
            headers[key.lower()] = value
    
    return headers


def parse_fetch_command(fetch_text: str) -> dict:
    """
    Parse a fetch command copied from Chrome DevTools.
    
    Chrome's "Copy as fetch" format has headers in a JavaScript object.
    """
    headers = {}
    
    # Try to find the headers object in the fetch call
    # Look for headers: { ... }
    headers_match = re.search(r'headers:\s*{([^}]+)}', fetch_text, re.DOTALL)
    
    if headers_match:
        headers_content = headers_match.group(1)
        
        # Parse each header line
        # Format is usually: "Header-Name": "value"
        header_pattern = r'"([^"]+)":\s*"([^"]+)"'
        matches = re.findall(header_pattern, headers_content)
        
        for key, value in matches:
            headers[key.lower()] = value
    
    return headers


def create_browser_json(headers: dict) -> dict:
    """
    Create browser.json structure from parsed headers.
    """
    # Essential headers for ytmusicapi
    browser_json = {
        "User-Agent": headers.get("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"),
        "Accept": headers.get("accept", "*/*"),
        "Accept-Language": headers.get("accept-language", "en-US,en;q=0.9"),
        "Content-Type": headers.get("content-type", "application/json"),
        "X-Goog-AuthUser": headers.get("x-goog-authuser", "0"),
        "x-origin": headers.get("x-origin", "https://music.youtube.com"),
        "Cookie": headers.get("cookie", "")
    }
    
    # Add Authorization if present
    if "authorization" in headers:
        browser_json["Authorization"] = headers["authorization"]
    
    return browser_json


def validate_browser_json(filepath: str = "browser.json") -> bool:
    """Test if the browser.json works with ytmusicapi."""
    try:
        from ytmusicapi import YTMusic
        
        print("\n🔍 Testing authentication...")
        ytmusic = YTMusic(filepath)
        
        # Try a simple search
        results = ytmusic.search("test", limit=1)
        
        if results:
            print("✅ Authentication is working!")
            
            # Try to access library
            try:
                playlists = ytmusic.get_library_playlists(limit=1)
                print("✅ Can access your library")
            except:
                print("⚠️  Can search but not access library")
            
            return True
        else:
            print("⚠️  Authentication might not be working")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("🌐 YouTube Music Auth from Chrome DevTools")
    print("=" * 60)
    
    print("\nThis tool extracts auth from Chrome's 'Copy as cURL' or 'Copy as fetch'")
    print("\nSteps:")
    print("1. Open music.youtube.com in Chrome")
    print("2. Open DevTools (F12)")
    print("3. Go to Network tab")
    print("4. Find a POST request to 'browse'")
    print("5. Right-click → Copy → Copy as cURL (or Copy as fetch)")
    print("6. Paste below")
    print("\n" + "-" * 60)
    print("Paste the cURL or fetch command (press Enter twice when done):")
    print("-" * 60)
    
    # Collect input
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
    
    if not lines:
        print("\n❌ No input provided")
        return 1
    
    full_text = "\n".join(lines)
    
    # Try to parse as cURL first
    headers = {}
    if "curl" in full_text.lower() or "-H" in full_text:
        print("\n📝 Detected cURL format")
        headers = parse_curl_command(full_text)
    elif "fetch" in full_text.lower():
        print("\n📝 Detected fetch format")
        headers = parse_fetch_command(full_text)
    else:
        # Try both
        headers = parse_curl_command(full_text)
        if not headers.get("cookie"):
            headers = parse_fetch_command(full_text)
    
    if not headers or not headers.get("cookie"):
        print("\n❌ Could not extract headers/cookies")
        print("\nMake sure you:")
        print("1. Are logged in to YouTube Music")
        print("2. Copied from a POST request to 'browse'")
        print("3. Used 'Copy as cURL' or 'Copy as fetch'")
        return 1
    
    print(f"\n✅ Extracted {len(headers)} headers")
    
    # Create browser.json
    browser_data = create_browser_json(headers)
    
    # Save to file
    with open("browser.json", "w") as f:
        json.dump(browser_data, f, indent=2)
    
    print("💾 Saved to browser.json")
    
    # Validate
    if validate_browser_json():
        print("\n🎉 Success! You can now use browser authentication")
        print("\nUsage:")
        print("  - MCP: ytm_create_playlist_browser (no quotas)")
        print("  - Direct: YTMusic('browser.json')")
        return 0
    else:
        print("\n⚠️  Saved but validation failed")
        print("Try using it anyway - it might still work")
        return 1


if __name__ == "__main__":
    sys.exit(main())
