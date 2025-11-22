#!/usr/bin/env python3
"""
Extract YouTube Music authentication from browser cookies.
This works with your existing browser where you're already logged in.
"""

import json
import sys
from pathlib import Path


def get_cookies_from_chrome():
    """Extract cookies from Chrome."""
    try:
        import browser_cookie3
        cookies = browser_cookie3.chrome(domain_name='.youtube.com')
        return cookies
    except Exception as e:
        print(f"❌ Could not extract Chrome cookies: {e}")
        return None


def get_cookies_from_firefox():
    """Extract cookies from Firefox."""
    try:
        import browser_cookie3
        cookies = browser_cookie3.firefox(domain_name='.youtube.com')
        return cookies
    except Exception as e:
        print(f"❌ Could not extract Firefox cookies: {e}")
        return None


def get_cookies_from_safari():
    """Extract cookies from Safari."""
    try:
        import browser_cookie3
        cookies = browser_cookie3.safari(domain_name='.youtube.com')
        return cookies
    except Exception as e:
        print(f"❌ Could not extract Safari cookies: {e}")
        return None


def create_browser_json(cookies, browser_name="Unknown"):
    """Create browser.json from cookies."""
    if not cookies:
        return None
    
    # Convert cookies to string
    cookie_list = []
    important_cookies = ['VISITOR_INFO1_LIVE', 'PREF', 'LOGIN_INFO', 'SIDCC', 'HSID', 'SSID', 'APISID', 'SAPISID', 'SID', '__Secure-1PSID', '__Secure-3PSID']
    
    found_important = False
    for cookie in cookies:
        cookie_list.append(f"{cookie.name}={cookie.value}")
        if cookie.name in important_cookies:
            found_important = True
    
    if not found_important:
        print(f"⚠️  Warning: No YouTube authentication cookies found in {browser_name}")
        print("    Make sure you're logged in to YouTube/YouTube Music")
    
    cookie_string = "; ".join(cookie_list)
    
    # Create browser.json structure
    browser_json = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
        "X-Goog-AuthUser": "0",
        "x-origin": "https://music.youtube.com",
        "Cookie": cookie_string
    }
    
    return browser_json


def test_browser_json(filepath="browser.json"):
    """Test if browser.json works."""
    try:
        from ytmusicapi import YTMusic
        
        print("\n🔍 Testing authentication...")
        ytmusic = YTMusic(filepath)
        results = ytmusic.search("test", limit=1)
        
        if results:
            print("✅ Authentication is working!")
            return True
        else:
            print("⚠️  Authentication might not be working properly")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("🍪 Extract YouTube Music Auth from Browser Cookies")
    print("=" * 60)
    
    # Check if browser_cookie3 is installed
    try:
        import browser_cookie3
    except ImportError:
        print("\n❌ browser_cookie3 not installed")
        print("\nInstall it with:")
        print("  uv add browser-cookie3")
        return 1
    
    print("\nThis tool extracts cookies from your browser where you're")
    print("already logged in to YouTube/YouTube Music.")
    print("\nTrying different browsers...")
    
    # Try different browsers
    browsers = [
        ("Chrome", get_cookies_from_chrome),
        ("Firefox", get_cookies_from_firefox),
        ("Safari", get_cookies_from_safari)
    ]
    
    success = False
    for browser_name, get_cookies_func in browsers:
        print(f"\n🔍 Trying {browser_name}...")
        cookies = get_cookies_func()
        
        if cookies:
            cookie_count = len(list(cookies))
            print(f"   Found {cookie_count} cookies")
            
            # Create browser.json
            browser_data = create_browser_json(cookies, browser_name)
            
            if browser_data and browser_data["Cookie"]:
                # Save to file
                with open("browser.json", "w") as f:
                    json.dump(browser_data, f, indent=2)
                
                print(f"   💾 Saved to browser.json")
                
                # Test it
                if test_browser_json():
                    print(f"\n🎉 Success! Extracted auth from {browser_name}")
                    success = True
                    break
                else:
                    print(f"   ⚠️  Cookies from {browser_name} didn't work")
    
    if success:
        print("\n✅ You can now use browser authentication!")
        print("\nUsage:")
        print("  from ytmusicapi import YTMusic")
        print("  ytmusic = YTMusic('browser.json')")
        return 0
    else:
        print("\n❌ Could not extract working authentication")
        print("\nTroubleshooting:")
        print("1. Make sure you're logged in to YouTube Music in your browser")
        print("2. Try the manual method: uv run python setup_browser_auth.py")
        print("3. Your browser might be blocking cookie access")
        return 1


if __name__ == "__main__":
    # First check if we need to install browser-cookie3
    try:
        import browser_cookie3
    except ImportError:
        print("📦 Installing browser-cookie3...")
        import subprocess
        subprocess.run(["uv", "add", "browser-cookie3"], check=True)
        print("✅ Installed! Running script...\n")
    
    sys.exit(main())
