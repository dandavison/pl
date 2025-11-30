#!/usr/bin/env python3
"""Test the setup tool directly"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ytmusic_mcp.server import mcp
import asyncio

async def test_setup():
    """Test the setup tool with headers"""
    
    # Sample headers (minimal for testing)
    headers_raw = """accept: */*
authorization: SAPISIDHASH test
cookie: __Secure-3PAPISID=test; other=cookies
x-goog-authuser: 0
content-type: application/json"""
    
    print("Testing setup with sample headers...")
    
    try:
        # Call the tool
        result = await mcp.call_tool(
            "setup_youtube_music",
            {"headers_raw": headers_raw}
        )
        # Result might be a TextContent object
        if hasattr(result, 'text'):
            print(f"Result text: {result.text}")
        else:
            print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_setup())
