# YouTube Music MCP Server

An MCP server that allows AI agents to create playlists on YouTube Music.

## Features

- **Authentication**: OAuth flow integrated into the chat interface.
- **Batch Playlist Creation**: Create a playlist from a list of song queries (e.g., "Song Name Artist"). The server searches for each track and adds the best match.
- **Feedback**: Returns a detailed summary of found and missing tracks.

## Installation

Prerequisites: `uv` (or pip) and Python 3.10+.

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

You need a Google Cloud Project with the **YouTube Data API v3** enabled.
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and enable the "YouTube Data API v3".
3. Configure the OAuth consent screen (External, add yourself as a test user).
4. Create OAuth 2.0 Client IDs (Application type: **TVs and Limited Input devices**).
5. Copy the **Client ID** and **Client Secret**.

## Usage with Claude Desktop (or other MCP Clients)

Add the server to your MCP configuration file (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ytmusic": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ytmusic-mcp",
        "run",
        "ytmusic-mcp"
      ]
    }
  }
}
```

## Tools

### `ytm_get_auth_url`
Initiates the authentication process.
- **Inputs**: `client_id`, `client_secret`
- **Output**: Verification URL and user code.

### `ytm_authenticate`
Completes authentication after you have authorized the app.
- **Inputs**: `device_code` (returned from previous step)
- **Output**: Success message.

### `ytm_create_playlist`
Creates a playlist and adds tracks.
- **Inputs**: `title`, `description`, `tracks` (List of strings)
- **Output**: Playlist URL and track summary.

## Development

Run tests:
```bash
uv run pytest
```

Type check:
```bash
uv run ty check
```

