# Browser Authentication Setup Guide

## Why Browser Auth?

Google blocks automated browser login for security ("This browser or app may not be secure"). However, we can extract authentication from your **existing** browser session where you're already logged in.

## Method 1: Quick Manual Setup (Recommended)

### Step 1: Get Your Headers

1. **Open YouTube Music** in your regular browser (Chrome/Firefox/Safari)
2. **Make sure you're logged in** to your Google account
3. **Open Developer Tools**:
   - Windows/Linux: Press `F12` or `Ctrl+Shift+I`
   - Mac: Press `Cmd+Option+I`
4. **Click on the Network tab**
5. **Trigger a request** by clicking "Library" or scrolling down
6. **Find a POST request** to `browse`:
   - Look for `browse?` in the Name column
   - Make sure Method is `POST` (not GET)
7. **Copy the headers**:
   - **Firefox**: Right-click → Copy → Copy Request Headers
   - **Chrome**: Click request → Headers tab → Select and copy all Request Headers
   - **Safari**: Click request → Headers → Copy all

### Step 2: Save the Headers

Run this command and paste your headers:
```bash
uv run python setup_browser_auth.py
```

Or use the new manual extractor:
```bash
uv run python extract_browser_auth_manual.py
```

## Method 2: Use Existing Chrome Session

If you use Chrome and want to avoid copying headers manually:

```python
# Use Chrome with a specific profile where you're logged in
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Use your existing Chrome installation
    browser = p.chromium.launch_persistent_context(
        user_data_dir="/path/to/chrome/profile",  # Your Chrome profile
        channel="chrome",  # Use system Chrome
        headless=False
    )
    # Browser will open with your existing login
```

## Method 3: Firefox Container Method

Firefox containers can help isolate the login:

1. Install Firefox Multi-Account Containers
2. Create a "YouTube" container
3. Log in to YouTube Music in that container
4. Extract headers from that container session

## Troubleshooting

### "This browser or app may not be secure"

This happens with automated browsers. Solutions:
- ✅ Use your regular browser where you're already logged in
- ✅ Extract headers from existing session (Method 1)
- ❌ Don't use Playwright's default Chromium

### Headers Don't Work

Make sure you:
- Copy from a **POST** request (not GET)
- Are logged in when copying
- Include the Cookie header
- Copy ALL headers from the request

### Alternative: Use Browser Cookies Directly

You can also extract just the cookies from your browser:

```python
import browser_cookie3
import json

# Get Chrome cookies for youtube.com
cookies = browser_cookie3.chrome(domain_name='youtube.com')

# Format for ytmusicapi
cookie_string = "; ".join([f"{c.name}={c.value}" for c in cookies])

browser_json = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "application/json",
    "X-Goog-AuthUser": "0",
    "x-origin": "https://music.youtube.com",
    "Cookie": cookie_string
}

with open("browser.json", "w") as f:
    json.dump(browser_json, f, indent=2)
```

## Benefits of Browser Auth

Once set up, browser auth gives you:
- ✅ **No API quotas** - unlimited operations
- ✅ **Valid for ~2 years** (until you log out)
- ✅ **Full access** to all YouTube Music features
- ✅ **No Google Cloud setup** needed

## Testing Your Setup

After creating `browser.json`, test it:

```python
from ytmusicapi import YTMusic

ytmusic = YTMusic("browser.json")
results = ytmusic.search("test", limit=1)
print("✅ Working!" if results else "❌ Not working")
```

## Security Notes

- `browser.json` contains your session cookies
- Keep it private (don't commit to git)
- It's tied to your Google account
- Revoke by logging out of YouTube Music
- Only works from the same IP/region (sometimes)
