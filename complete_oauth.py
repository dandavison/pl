#!/usr/bin/env python3
"""Complete the OAuth flow after browser authorization"""

from ytmusicapi.auth.oauth import OAuthCredentials
import json
import time

# Load credentials
with open('oauth_creds.json', 'r') as f:
    creds_data = json.load(f)

print("Completing OAuth flow...")

# Create credentials
oauth_credentials = OAuthCredentials(
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)

# Get a new code to display the device code we need
code_info = oauth_credentials.get_code()

print(f"New verification URL: {code_info['verification_url']}")
print(f"New user code: {code_info['user_code']}")
print(f"Device code: {code_info['device_code']}")

# Since you already authorized with RFV-JQX-JRJS, we need to poll for that token
# But we don't have the device_code for that session...
# Let's try to get the token using the current device code

print("\nIf you just authorized RFV-JQX-JRJS, please go back and authorize this new code:")
print(f"  {code_info['user_code']}")
print("\nOr press Ctrl+C and we'll try a different approach...")

# Wait and poll for token
interval = code_info.get('interval', 5)
print(f"\nPolling for token (interval: {interval}s)...")

for i in range(60 // interval):  # Try for 1 minute
    try:
        time.sleep(interval)
        print(f"  Attempt {i+1}...")
        token = oauth_credentials.token_from_code(code_info['device_code'])

        # Success! Save the token
        print("✓ Token obtained successfully!")

        # Create RefreshingToken and save
        from ytmusicapi.auth.oauth import RefreshingToken
        refreshing_token = RefreshingToken(
            credentials=oauth_credentials,
            **token
        )

        # Save token
        refreshing_token.store_token('oauth.json')
        print("✓ Saved to oauth.json")

        # Also save credentials separately
        with open('oauth_creds.json', 'w') as f:
            json.dump({
                'client_id': creds_data['client_id'],
                'client_secret': creds_data['client_secret']
            }, f, indent=2)

        print("\n✓ Authentication complete!")
        break

    except Exception as e:
        if "authorization_pending" in str(e).lower():
            continue  # Keep polling
        else:
            print(f"Error: {e}")
            break
