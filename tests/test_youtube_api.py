"""Tests for YouTube API integration."""

import pytest
from unittest.mock import MagicMock, patch, Mock
from ytmusic_mcp.youtube_api import YouTubeAPI, PlaylistBuilder


class TestYouTubeAPI:
    """Test YouTube API class."""

    @pytest.fixture
    def youtube_api(self):
        """Create a YouTube API instance with a fake token."""
        return YouTubeAPI("fake_access_token")

    @patch('requests.get')
    def test_search_tracks_success(self, mock_get, youtube_api):
        """Test successful track search."""
        # Mock search response
        mock_search_response = Mock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "test_id_1"},
                    "snippet": {
                        "title": "Test Song",
                        "channelTitle": "Test Artist",
                        "channelId": "channel_1",
                        "description": "Test description",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "thumbnails": {"default": {"url": "http://example.com/thumb.jpg"}},
                        "liveBroadcastContent": "none"
                    }
                }
            ]
        }

        # Mock video details response
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {
            "items": [
                {
                    "id": "test_id_1",
                    "contentDetails": {"duration": "PT3M30S"},
                    "statistics": {"viewCount": "1000", "likeCount": "100"}
                }
            ]
        }

        # Set up the mock to return different responses for different URLs
        def side_effect(url, **kwargs):
            if "search" in url:
                return mock_search_response
            else:
                return mock_details_response

        mock_get.side_effect = side_effect

        # Test
        results = youtube_api.search_tracks("test query")

        assert len(results) == 1
        assert results[0]["videoId"] == "test_id_1"
        assert results[0]["title"] == "Test Song"
        assert results[0]["channel"] == "Test Artist"
        assert results[0]["isRemix"] == False
        assert results[0]["isRemaster"] == False
        assert results[0]["duration"] == "PT3M30S"
        assert results[0]["viewCount"] == 1000

    @patch('requests.get')
    def test_search_tracks_detects_remix(self, mock_get, youtube_api):
        """Test that remixes are properly detected."""
        # Mock search response
        mock_search_response = Mock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "remix_id"},
                    "snippet": {
                        "title": "Test Song (Artist Remix)",
                        "channelTitle": "Test Channel",
                        "channelId": "channel_1",
                        "description": "Remix version",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "thumbnails": {"default": {"url": "http://example.com/thumb.jpg"}},
                        "liveBroadcastContent": "none"
                    }
                }
            ]
        }

        # Mock video details response (empty since we don't need it for remix detection)
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {"items": []}

        # Set up the mock to return different responses
        def side_effect(url, **kwargs):
            if "search" in url:
                return mock_search_response
            else:
                return mock_details_response

        mock_get.side_effect = side_effect

        results = youtube_api.search_tracks("test query")
        assert results[0]["isRemix"] == True

    @patch('requests.get')
    def test_search_tracks_detects_remaster(self, mock_get, youtube_api):
        """Test that remasters are properly detected."""
        # Mock search response
        mock_search_response = Mock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "items": [
                {
                    "id": {"videoId": "remaster_id"},
                    "snippet": {
                        "title": "Test Song (2023 Remaster)",
                        "channelTitle": "Test Channel",
                        "channelId": "channel_1",
                        "description": "Remastered version",
                        "publishedAt": "2023-01-01T00:00:00Z",
                        "thumbnails": {"default": {"url": "http://example.com/thumb.jpg"}},
                        "liveBroadcastContent": "none"
                    }
                }
            ]
        }

        # Mock video details response (empty since we don't need it for remaster detection)
        mock_details_response = Mock()
        mock_details_response.status_code = 200
        mock_details_response.json.return_value = {"items": []}

        # Set up the mock to return different responses
        def side_effect(url, **kwargs):
            if "search" in url:
                return mock_search_response
            else:
                return mock_details_response

        mock_get.side_effect = side_effect

        results = youtube_api.search_tracks("test query")
        assert results[0]["isRemaster"] == True

    @patch('requests.post')
    def test_create_playlist(self, mock_post, youtube_api):
        """Test playlist creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "new_playlist_id"}
        mock_post.return_value = mock_response

        playlist_id = youtube_api.create_playlist("Test Playlist", "Test Description")

        assert playlist_id == "new_playlist_id"
        mock_post.assert_called_once()

        # Check the call arguments
        call_args = mock_post.call_args
        assert call_args[1]["json"]["snippet"]["title"] == "Test Playlist"
        assert call_args[1]["json"]["snippet"]["description"] == "Test Description"

    @patch('requests.post')
    def test_add_to_playlist(self, mock_post, youtube_api):
        """Test adding videos to playlist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        results = youtube_api.add_to_playlist("playlist_id", ["video1", "video2"])

        assert results == [True, True]
        assert mock_post.call_count == 2


class TestPlaylistBuilder:
    """Test PlaylistBuilder class."""

    @pytest.fixture
    def playlist_builder(self):
        """Create a PlaylistBuilder with mocked YouTube API."""
        mock_api = MagicMock(spec=YouTubeAPI)
        return PlaylistBuilder(mock_api)

    def test_search_tracks_batch(self, playlist_builder):
        """Test batch track search."""
        # Mock the search_tracks method
        playlist_builder.api.search_tracks.side_effect = [
            [{"videoId": "id1", "title": "Song 1"}],
            [{"videoId": "id2", "title": "Song 2"}]
        ]

        results = playlist_builder.search_tracks_batch(["query1", "query2"])

        assert "query1" in results
        assert "query2" in results
        assert results["query1"][0]["title"] == "Song 1"
        assert results["query2"][0]["title"] == "Song 2"

    def test_search_tracks_batch_handles_errors(self, playlist_builder):
        """Test batch search handles errors gracefully."""
        # Mock one success and one failure
        playlist_builder.api.search_tracks.side_effect = [
            [{"videoId": "id1", "title": "Song 1"}],
            Exception("API Error")
        ]

        results = playlist_builder.search_tracks_batch(["query1", "query2"])

        assert results["query1"][0]["title"] == "Song 1"
        assert "error" in results["query2"]

    def test_create_playlist_from_ids(self, playlist_builder):
        """Test creating playlist from video IDs."""
        playlist_builder.api.create_playlist.return_value = "new_playlist_id"
        playlist_builder.api.add_to_playlist.return_value = [True, True, False]

        result = playlist_builder.create_playlist_from_ids(
            "Test Playlist",
            "Description",
            ["video1", "video2", "video3"]
        )

        assert result["playlist_id"] == "new_playlist_id"
        assert result["videos_added"] == 2
        assert result["videos_total"] == 3
        assert "youtube.com/playlist?list=new_playlist_id" in result["youtube_url"]
        assert "music.youtube.com/playlist?list=new_playlist_id" in result["music_url"]
