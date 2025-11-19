import pytest
from unittest.mock import MagicMock, patch
from ytmusic_mcp.auth import AuthManager

@pytest.fixture
def mock_oauth_credentials():
    with patch('ytmusic_mcp.auth.OAuthCredentials') as mock:
        yield mock

@pytest.fixture
def mock_refreshing_token():
    with patch('ytmusic_mcp.auth.RefreshingToken') as mock:
        yield mock

def test_start_oauth(mock_oauth_credentials):
    # Setup
    mock_instance = mock_oauth_credentials.return_value
    mock_instance.get_code.return_value = {
        "verification_url": "http://google.com/device",
        "user_code": "ABCD-1234",
        "device_code": "device-code-xyz",
        "interval": 5
    }

    manager = AuthManager()
    result = manager.start_oauth("client_id", "client_secret")

    assert result["verification_url"] == "http://google.com/device"
    assert result["user_code"] == "ABCD-1234"
    assert result["device_code"] == "device-code-xyz"
    mock_oauth_credentials.assert_called_with("client_id", "client_secret")

def test_complete_oauth(mock_oauth_credentials, mock_refreshing_token, tmp_path):
    # Setup
    manager = AuthManager(oauth_path=str(tmp_path / "oauth.json"))

    # Simulate start
    mock_creds_instance = mock_oauth_credentials.return_value
    manager._pending_credentials = mock_creds_instance

    # Mock token response
    mock_creds_instance.token_from_code.return_value = {"access_token": "fake-token"}

    result = manager.complete_oauth("device-code-xyz")

    assert "successful" in result
    mock_creds_instance.token_from_code.assert_called_with("device-code-xyz")
    mock_refreshing_token.assert_called()
    # Check that store_token was called
    mock_refreshing_token.return_value.store_token.assert_called_with(str(tmp_path / "oauth.json"))

