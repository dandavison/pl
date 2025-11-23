#!/usr/bin/env python3
"""Try to refresh the OAuth token"""

from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken
import json
from datetime import datetime, timezone

# Load current oauth
with open('oauth.json', 'r') as f:
    oauth_data = json.load(f)

print("Current token info:")
print(f"  expires_at: {oauth_data.get('expires_at')}")
print(f"  expires_in: {oauth_data.get('expires_in')}")

# Check if expired
expires_at = oauth_data.get('expires_at', 0)
now = datetime.now(timezone.utc).timestamp()
if expires_at > 0 and expires_at < now:
    print(f"  Token expired {(now - expires_at) / 3600:.1f} hours ago")
elif expires_at > 0:
    print(f"  Token expires in {(expires_at - now) / 3600:.1f} hours")

# Load credentials
with open('oauth_creds.json', 'r') as f:
    creds_data = json.load(f)

print("\nAttempting to refresh token...")
try:
    creds = OAuthCredentials(
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret']
    )

    # Create RefreshingToken
    token = RefreshingToken(
        credentials=creds,
        **oauth_data
    )

    # Force refresh
    print("Refreshing token...")
    token.refresh()

    # Save updated token
    token.store_token('oauth.json')
    print("✓ Token refreshed and saved!")

    # Verify it worked
    from ytmusicapi import YTMusic
    print("\nVerifying refreshed token...")
    ytmusic = YTMusic(auth='oauth.json', oauth_credentials=creds)

    # Try a simple call
    print("Testing with search...")
    results = ytmusic.search("test", limit=1)
    print("✓ API call successful!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
