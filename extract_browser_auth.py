#!/usr/bin/env python3
"""
Extract YouTube Music browser authentication headers using Playwright.
This allows using ytmusicapi with browser authentication for better API limits.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Optional

from playwright.async_api import async_playwright, Request, Response


class YouTubeMusicAuthExtractor:
    """Extract authentication headers from YouTube Music using browser automation."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.headers: Optional[Dict[str, str]] = None
        self.target_request_found = False

    async def extract_headers(self) -> Optional[Dict[str, str]]:
        """
        Launch browser and extract authentication headers from YouTube Music.

        Returns:
            Dictionary of headers if successful, None otherwise.
        """
        async with async_playwright() as p:
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()

            # Set up request interception
            page.on("request", self._handle_request)

            print("📱 Opening YouTube Music...")
            print("👤 Please log in to your Google/YouTube account if not already logged in")
            await page.goto("https://music.youtube.com")

            # Wait for user to log in and for the page to load
            print("⏳ Waiting for authentication...")
            print("   After logging in, browse around a bit (click Library, scroll, etc.)")
            print("   This will trigger the requests we need to capture...")

            # Wait for a /browse request or timeout after 2 minutes
            max_wait = 120  # seconds
            check_interval = 0.5  # seconds
            elapsed = 0

            while not self.target_request_found and elapsed < max_wait:
                await asyncio.sleep(check_interval)
                elapsed += check_interval

                # Check if we're on the right page
                current_url = page.url
                if "music.youtube.com" not in current_url:
                    print("⚠️  Please navigate back to music.youtube.com")

            if self.target_request_found and self.headers:
                print("✅ Authentication headers captured successfully!")
                await browser.close()
                return self.headers
            else:
                print("❌ Timeout: Could not capture authentication headers")
                print("   Try clicking on 'Library' or scrolling to trigger requests")
                await browser.close()
                return None

    def _handle_request(self, request: Request) -> None:
        """Handle intercepted requests to find authentication headers."""
        # Look for authenticated POST requests to /browse endpoint
        if (request.method == "POST" and
            "music.youtube.com" in request.url and
            "/browse" in request.url):

            headers = request.headers

            # Check if this is an authenticated request
            if "cookie" in headers or "Cookie" in headers:
                print(f"🎯 Found authenticated request: {request.url[:80]}...")

                # Extract the headers we need for ytmusicapi
                self.headers = {
                    "User-Agent": headers.get("user-agent", ""),
                    "Accept": "*/*",
                    "Accept-Language": headers.get("accept-language", "en-US,en;q=0.5"),
                    "Content-Type": "application/json",
                    "X-Goog-AuthUser": headers.get("x-goog-authuser", "0"),
                    "x-origin": "https://music.youtube.com",
                    "Cookie": headers.get("cookie", "")
                }

                # Also capture additional headers that might be needed
                if "authorization" in headers:
                    self.headers["Authorization"] = headers["authorization"]
                if "x-goog-visitor-id" in headers:
                    self.headers["X-Goog-Visitor-Id"] = headers["x-goog-visitor-id"]
                if "x-youtube-client-name" in headers:
                    self.headers["X-Youtube-Client-Name"] = headers["x-youtube-client-name"]
                if "x-youtube-client-version" in headers:
                    self.headers["X-Youtube-Client-Version"] = headers["x-youtube-client-version"]

                self.target_request_found = True


def save_browser_json(headers: Dict[str, str], filepath: str = "browser.json") -> None:
    """
    Save headers to browser.json file for use with ytmusicapi.

    Args:
        headers: Dictionary of headers
        filepath: Path to save the browser.json file
    """
    # Format according to ytmusicapi's expected structure
    browser_data = {
        "User-Agent": headers.get("User-Agent", ""),
        "Accept": headers.get("Accept", "*/*"),
        "Accept-Language": headers.get("Accept-Language", "en-US,en;q=0.5"),
        "Content-Type": headers.get("Content-Type", "application/json"),
        "X-Goog-AuthUser": headers.get("X-Goog-AuthUser", "0"),
        "x-origin": headers.get("x-origin", "https://music.youtube.com"),
        "Cookie": headers.get("Cookie", "")
    }

    # Add optional headers if present
    optional_headers = [
        "Authorization", "X-Goog-Visitor-Id",
        "X-Youtube-Client-Name", "X-Youtube-Client-Version"
    ]
    for header in optional_headers:
        if header in headers and headers[header]:
            browser_data[header] = headers[header]

    with open(filepath, 'w') as f:
        json.dump(browser_data, f, indent=2)

    print(f"💾 Saved browser authentication to {filepath}")


async def main():
    """Main function to run the authentication extraction."""
    print("=" * 60)
    print("🎵 YouTube Music Browser Authentication Extractor")
    print("=" * 60)
    print()
    print("This tool will:")
    print("1. Open a browser window with YouTube Music")
    print("2. Let you log in to your Google account")
    print("3. Capture the authentication headers")
    print("4. Save them for use with ytmusicapi")
    print()
    print("⚠️  Note: This uses YOUR personal Google account")
    print("    The extracted credentials will remain valid for ~2 years")
    print("    unless you explicitly log out from YouTube Music")
    print()

    # Ask for user confirmation
    confirm = input("Do you want to proceed? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Cancelled.")
        return 1

    # Ask if user wants headless mode
    headless_input = input("Run in headless mode? (y/n, default=n): ").lower().strip()
    headless = headless_input == 'y'

    if headless:
        print("⚠️  Headless mode: You'll need to be already logged in to Google")

    # Create extractor and run
    extractor = YouTubeMusicAuthExtractor(headless=headless)
    headers = await extractor.extract_headers()

    if headers:
        # Save to browser.json
        save_browser_json(headers)

        # Also offer to save with a custom name
        custom = input("\nSave with a custom filename too? (press Enter to skip): ").strip()
        if custom:
            if not custom.endswith('.json'):
                custom += '.json'
            save_browser_json(headers, custom)

        print("\n✅ Success! You can now use browser authentication with ytmusicapi:")
        print("   from ytmusicapi import YTMusic")
        print("   ytmusic = YTMusic('browser.json')")
        return 0
    else:
        print("\n❌ Failed to extract authentication headers")
        print("   Please try again and make sure to:")
        print("   1. Log in to your Google account")
        print("   2. Click on 'Library' or browse around to trigger requests")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
