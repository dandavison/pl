# YouTube Music MCP Server

An MCP server that allows AI agents to intelligently search for tracks and create playlists on YouTube/YouTube Music using the YouTube Data API v3.

## Features

- **Dual Authentication Methods**:
  - OAuth (YouTube Data API v3) - Official but has quotas
  - Browser Auth (ytmusicapi) - No quotas, uses web interface
- **Intelligent Track Search**: Search for multiple tracks and return detailed metadata for LLM selection
- **Smart Playlist Creation**: Create playlists with specific video IDs after intelligent selection
- **No API Quota Limits** (with browser auth): Create unlimited playlists
- **Metadata-Rich Results**: Returns information about remixes, remasters, view counts, and more

## Installation

Prerequisites: `uv` (or pip) and Python 3.10+.

1. Clone the repository.
2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

### Browser Authentication (No API Quotas!)

Extract authentication from your browser session:

```bash
# For Chrome users (recommended):
uv run python extract_from_curl.py  # Paste "Copy as cURL" output

# Alternative methods:
uv run python extract_from_browser_cookies.py  # Extract cookies directly
uv run python extract_browser_auth_manual.py   # Guided extraction
uv run python setup_browser_auth.py            # Paste raw headers
```

**Note**: Google blocks automated login ("This browser may not be secure").
Use the manual extraction from your existing browser session instead.

This method:
- ✅ No API quotas - unlimited playlist creation
- ✅ Uses your existing YouTube Music login
- ✅ Credentials valid for ~2 years
- ⚠️ Less suitable for production apps


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

### Browser Authentication Tools (No Quotas)

#### `ytm_get_browser_auth_instructions`
Get step-by-step instructions for setting up browser auth.
- **Output**: Instructions and current status

#### `ytm_setup_browser_auth_from_curl`
Set up browser authentication using cURL from Chrome.
- **Input**: `curl_command` (copied from Chrome DevTools)
- **Output**: Success status and config location

#### `ytm_validate_browser_auth`
Check if browser authentication is working.
- **Output**: Validation status

#### `ytm_search_browser`
Search using browser auth (no quotas).
- **Input**: `queries` (list of search strings)
- **Output**: Detailed search results

#### `ytm_create_playlist_browser`
Create playlist using browser auth (no quotas).
- **Input**: `title`, `description`, `tracks`
- **Output**: Playlist URL and details


## Intelligent Playlist Creation Workflow

The new tools enable a smarter playlist creation workflow:

1. **Search Phase**: Use `ytm_search_tracks` to get multiple results per query
2. **Selection Phase**: LLM analyzes results based on criteria:
   - Prefer original recordings over remixes
   - Prefer original versions over remasters
   - Consider channel authority (official/label channels)
   - Avoid full album uploads when searching for single tracks
   - Consider view count and engagement metrics
3. **Creation Phase**: Use `ytm_create_playlist_from_ids` with selected video IDs

This approach ensures better quality playlists compared to blindly taking the first search result.

## Development

Run tests:
```bash
uv run pytest
```

Type check:
```bash
uv run ty check
```

