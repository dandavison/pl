_ARCHIVED: this is becoming available natively in YouTube Music: https://gemini.google.com/apps_

# YouTube Music MCP Server

MCP server for YouTube Music playlist creation using browser authentication.

## MCP Configuration

```json
{
  "mcpServers": {
    "ytmusic": {
      "command": "uvx",
      "args": [
        "git+https://github.com/dandavison/pl",
      ]
    }
  }
}
```

## Setup

Browser authentication required. The server will guide you through setup on first use.

## Tools

- `ytm_create_playlist_browser` - Create playlist from track names
- `ytm_search_browser` - Search for tracks
- `ytm_validate_browser_auth` - Validate authentication