#!/usr/bin/env python3
"""Test the cURL parsing from the MCP tool"""

import re
import sys

def parse_curl(curl_command):
    """Parse a cURL command and extract headers/cookies"""
    print(f"Input length: {len(curl_command)} chars", file=sys.stderr)
    print(f"First 200 chars: {repr(curl_command[:200])}", file=sys.stderr)
    
    # Join lines and clean up backslashes
    curl_text = " ".join(curl_command.split("\\\n"))
    curl_text = " ".join(curl_text.split("\\"))
    
    print(f"After cleanup: {len(curl_text)} chars", file=sys.stderr)
    
    headers = {}
    
    # Extract headers
    header_pattern = r"-H\s+['\"]([^'\"]+)['\"]"
    for match in re.finditer(header_pattern, curl_text):
        header_line = match.group(1)
        if ":" in header_line:
            key, value = header_line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
            print(f"Found header: {key.strip().lower()}", file=sys.stderr)
    
    # Extract cookies
    cookie_pattern = r"-b\s+['\"]([^'\"]+)['\"]"
    cookie_match = re.search(cookie_pattern, curl_text)
    if cookie_match:
        headers["cookie"] = cookie_match.group(1).strip()
        print(f"Found cookie from -b flag", file=sys.stderr)
    
    print(f"\nTotal headers found: {len(headers)}", file=sys.stderr)
    print(f"Has cookie: {'cookie' in headers}", file=sys.stderr)
    
    return headers

if __name__ == "__main__":
    # Read from stdin
    print("Paste your cURL command (Ctrl+D when done):", file=sys.stderr)
    curl_input = sys.stdin.read()
    
    headers = parse_curl(curl_input)
    
    if headers.get("cookie"):
        print("✅ Successfully parsed cookies!", file=sys.stderr)
    else:
        print("❌ No cookies found!", file=sys.stderr)
