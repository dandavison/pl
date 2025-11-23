#!/usr/bin/env python3
"""Check if token is valid by testing with raw requests"""

import json
import requests

# Load token
with open('oauth.json', 'r') as f:
    oauth = json.load(f)

access_token = oauth['access_token']

print("Testing token with raw YouTube Data API v3 request...")
print(f"Token starts with: {access_token[:20]}...")

# Test with a simple API call
url = "https://www.googleapis.com/youtube/v3/channels"
params = {
    "part": "snippet",
    "mine": "true"
}
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(url, params=params, headers=headers)
print(f"\nResponse status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if 'items' in data and data['items']:
        channel = data['items'][0]['snippet']
        print(f"✓ Token works! Channel: {channel['title']}")
    else:
        print("✓ Token works but no channel data")
else:
    print(f"✗ Error: {response.text}")

    if "API has not been used" in response.text:
        print("\n⚠️  YouTube Data API v3 may not be enabled in your Google Cloud project")
        print("   Go to: https://console.cloud.google.com/apis/library/youtube.googleapis.com")
        print("   And enable the YouTube Data API v3")
    elif "invalid" in response.text.lower():
        print("\n⚠️  Token may be invalid or expired")
    elif "quota" in response.text.lower():
        print("\n⚠️  API quota may be exceeded")
