#!/usr/bin/env python3
"""Fix oauth.json format for ytmusicapi"""

import json
from pathlib import Path

def fix_oauth():
    oauth_path = Path("oauth.json")

    print("Reading current oauth.json...")
    with open(oauth_path, 'r') as f:
        oauth_data = json.load(f)

    # The issue is that ytmusicapi expects the format differently
    # According to the error, it needs the oauth_credentials embedded correctly

    # Extract the credentials
    if 'oauth_credentials' not in oauth_data:
        print("ERROR: oauth_credentials not found in oauth.json")
        return False

    client_id = oauth_data['oauth_credentials']['client_id']
    client_secret = oauth_data['oauth_credentials']['client_secret']

    # Create the correctly formatted oauth file
    # Based on ytmusicapi's expected format
    fixed_oauth = {
        "access_token": oauth_data['access_token'],
        "refresh_token": oauth_data['refresh_token'],
        "expires_in": oauth_data['expires_in'],
        "expires_at": oauth_data.get('expires_at', 0),
        "token_type": oauth_data['token_type'],
        "scope": oauth_data['scope']
    }

    # Write to a new file first for safety
    backup_path = Path("oauth_backup.json")
    print(f"\nBacking up current oauth.json to {backup_path}...")
    with open(backup_path, 'w') as f:
        json.dump(oauth_data, f, indent=2)

    print("\nWriting fixed oauth.json...")
    with open(oauth_path, 'w') as f:
        json.dump(fixed_oauth, f, indent=2)

    # Also create a separate credentials file if needed
    creds_path = Path("oauth_creds.json")
    print(f"\nWriting credentials to {creds_path}...")
    with open(creds_path, 'w') as f:
        json.dump({
            "client_id": client_id,
            "client_secret": client_secret
        }, f, indent=2)

    print("\nDone! Files created:")
    print(f"  - {oauth_path} (fixed auth file)")
    print(f"  - {backup_path} (backup of original)")
    print(f"  - {creds_path} (credentials file)")

    return True

if __name__ == "__main__":
    fix_oauth()
