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

### Method 1: Browser Authentication (Recommended - No Quotas)

Extract authentication from your browser session:

```bash
# Automated extraction (opens browser)
uv run python extract_browser_auth.py

# Or manual setup
uv run python setup_browser_auth.py
```

This method:
- ✅ No API quotas - unlimited playlist creation
- ✅ Uses your existing YouTube Music login
- ✅ Credentials valid for ~2 years
- ⚠️ Less suitable for production apps

### Method 2: OAuth API (Limited by Quotas)

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

### Browser Authentication Tools (No Quotas)

#### `ytm_setup_browser_auth`
Set up browser authentication using headers from YouTube Music.
- **Input**: `headers_raw` (copied from browser)
- **Output**: Success message

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

### OAuth API Tools (Subject to Quotas)

#### `ytm_get_auth_url`
Initiates the OAuth authentication process.
- **Inputs**: `client_id`, `client_secret`
- **Output**: Verification URL, user code, and device code

#### `ytm_authenticate`
Completes authentication after user authorization.
- **Inputs**: `device_code` (from previous step)
- **Output**: Success message

### Playlist Creation Tools

#### `ytm_search_tracks` (NEW)
Search for multiple tracks with detailed metadata for intelligent selection.
- **Inputs**: `queries` (List of search strings like "Artist Song Title")
- **Output**: Dictionary mapping each query to list of results with:
  - Video ID, title, channel, description
  - View count, like count, duration
  - Flags for remix/remaster detection
  - Published date and thumbnails

#### `ytm_create_playlist_from_ids` (NEW)
Create a playlist with specific video IDs after intelligent selection.
- **Inputs**:
  - `title`: Playlist title
  - `description`: Playlist description
  - `video_ids`: List of YouTube video IDs
- **Output**: Playlist ID, YouTube/YouTube Music URLs, success metrics

#### `ytm_create_playlist_ytmusic` (LEGACY)
Creates a playlist using YTMusic API (takes first search result).
- **Inputs**: `title`, `description`, `tracks` (List of strings)
- **Output**: Playlist URL and track summary
- **Note**: Prefer using search + create_from_ids for better control

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

