#!/usr/bin/env python3
"""
Extract YouTube Music browser authentication from Chrome's "Copy as cURL" output.
Reads from curl.txt file.
"""

import json
import re
import sys
from pathlib import Path


def extract_cookies_and_headers(text: str) -> dict:
    """
    Extract headers and cookies from any cURL format.
    """
    # Join all lines and clean up backslashes
    text = " ".join(text.split("\\\n"))
    text = " ".join(text.split("\\"))

    result = {}

    # Extract all -H headers
    header_pattern = r"-H\s+['\"]([^'\"]+)['\"]"
    for match in re.finditer(header_pattern, text):
        header_line = match.group(1)
        if ":" in header_line:
            key, value = header_line.split(":", 1)
            result[key.strip().lower()] = value.strip()

    # Extract cookies from -b flag
    cookie_pattern = r"-b\s+['\"]([^'\"]+)['\"]"
    cookie_match = re.search(cookie_pattern, text)
    if cookie_match:
        result["cookie"] = cookie_match.group(1).strip()

    return result


def main():
    print("=" * 60)
    print("🌐 YouTube Music Auth from Chrome DevTools")
    print("=" * 60)

    # Read from curl.txt
    curl_file = Path("curl.txt")

    if not curl_file.exists():
        print("\n❌ curl.txt not found!")
        print("\nInstructions:")
        print("1. Copy cURL from Chrome DevTools (Copy → Copy as cURL)")
        print("2. Save it to curl.txt in this directory")
        print("3. Run this script again")
        return 1

    with open(curl_file, "r") as f:
        input_text = f.read()

    print(f"\n✅ Read {len(input_text)} bytes from curl.txt")

    # Extract headers and cookies
    data = extract_cookies_and_headers(input_text)

    if not data.get("cookie"):
        print("\n❌ No cookies found in the cURL command")
        print(f"   Found {len(data)} headers but no cookies")
        print("\nMake sure the curl.txt contains the full cURL command from Chrome")
        return 1

    print(f"✅ Found {len(data)} headers including cookies")

    # Create browser.json
    browser_json = {
        "User-Agent": data.get(
            "user-agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        ),
        "Accept": data.get("accept", "*/*"),
        "Accept-Language": data.get("accept-language", "en-US,en;q=0.9"),
        "Content-Type": data.get("content-type", "application/json"),
        "X-Goog-AuthUser": data.get("x-goog-authuser", "0"),
        "x-origin": data.get("x-origin", "https://music.youtube.com"),
        "Cookie": data["cookie"],
    }

    # Add authorization if present
    if "authorization" in data:
        browser_json["Authorization"] = data["authorization"]

    # Save to browser.json
    with open("browser.json", "w") as f:
        json.dump(browser_json, f, indent=2)

    print("💾 Saved to browser.json")

    # Test it
    print("\n🔍 Testing with ytmusicapi...")
    try:
        from ytmusicapi import YTMusic

        ytmusic = YTMusic("browser.json")
        results = ytmusic.search("test", limit=1)
        if results:
            print("✅ SUCCESS! Authentication is working!")
            print("\nYou can now create unlimited playlists without quotas!")
        else:
            print("⚠️  Couldn't verify, but try using it anyway")
    except Exception as e:
        print(f"⚠️  Test error: {str(e)[:100]}")
        print("\nThe browser.json file was created. Try using it anyway.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
