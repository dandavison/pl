#!/usr/bin/env python3
"""Test to understand ytmusicapi's expected oauth format"""

import json
from pathlib import Path
from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken, OAuthToken

def test_format():
    # Load our current oauth.json
    with open('oauth.json', 'r') as f:
        oauth_data = json.load(f)

    print("Current oauth.json structure:")
    for key in oauth_data:
        if key == 'access_token':
            print(f"  {key}: {oauth_data[key][:20]}...")
        elif key == 'oauth_credentials':
            print(f"  {key}: {oauth_data[key]}")
        else:
            print(f"  {key}: {oauth_data[key]}")

    print("\n" + "="*50)

    # Try to understand what RefreshingToken expects
    if 'oauth_credentials' in oauth_data:
        client_id = oauth_data['oauth_credentials']['client_id']
        client_secret = oauth_data['oauth_credentials']['client_secret']

        print(f"\nCreating OAuthCredentials with client_id and secret...")
        creds = OAuthCredentials(client_id, client_secret)

        print(f"Creating RefreshingToken...")
        try:
            # Extract token data without oauth_credentials
            token_data = {k: v for k, v in oauth_data.items() if k != 'oauth_credentials'}

            token = RefreshingToken(
                credentials=creds,
                **token_data
            )

            print("SUCCESS: RefreshingToken created!")

            # Now save it in the proper format
            print("\nSaving token in proper format...")
            token.store_token("oauth_fixed.json")

            # Check what got saved
            print("\nChecking saved format...")
            with open("oauth_fixed.json", 'r') as f:
                fixed_data = json.load(f)

            print("Fixed oauth structure:")
            for key in fixed_data:
                if isinstance(fixed_data[key], str) and len(fixed_data[key]) > 50:
                    print(f"  {key}: {fixed_data[key][:20]}...")
                else:
                    print(f"  {key}: {fixed_data[key]}")

        except Exception as e:
            print(f"ERROR: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_format()
