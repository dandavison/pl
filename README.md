# YouTube Music MCP Server

Create unlimited YouTube Music playlists without API quotas using browser authentication.

## Features

- **No API quotas** - Create unlimited playlists
- **No Google Cloud setup** - Uses your existing YouTube Music login
- **Smart track selection** - Finds the best match for each song
- **Simple setup** - One-time browser authentication

## Installation

```bash
# Clone the repository
git clone <this-repo>
cd ytmusic-mcp

# Install dependencies
uv sync
```

## Setup Browser Authentication

1. Save your YouTube Music credentials:
```bash
uv run python setup_youtube_music.py
```

2. Follow the instructions:
   - Open Chrome and go to music.youtube.com
   - Press F12 and click the Network tab
   - Click "Library" in YouTube Music
   - Find "browse" in the Network tab
   - Right-click it → Copy → Copy as cURL
   - Paste into the script

That's it! Your credentials are saved and will work for ~2 years.

## MCP Server Configuration

Add to your MCP client config (e.g., Claude Desktop):

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

## Available Tools

- **ytm_create_playlist_browser** - Create a playlist with a list of track names
- **ytm_search_browser** - Search for tracks
- **ytm_validate_browser_auth** - Check if authentication is working

## Usage Example

Once connected to your MCP client, you can say:

> "Create a playlist called 'Summer Vibes' with these songs: [list of songs]"

The server will automatically search for each track and add the best match to your playlist.

## Troubleshooting

If you get authentication errors:
1. Make sure you're logged into YouTube Music in Chrome
2. Re-run `setup_youtube_music.py` to update your credentials
3. Check that the browser.json file was created in `~/.config/ytmusic-mcp/`

## Development

Run tests:
```bash
uv run pytest tests/
```