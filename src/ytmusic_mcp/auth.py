import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken
from ytmusicapi import YTMusic

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, oauth_path: str = "oauth.json"):
        self.oauth_path = Path(oauth_path)
        self._pending_credentials: Optional[OAuthCredentials] = None

    def is_authenticated(self) -> bool:
        return self.oauth_path.exists()

    def get_ytmusic(self) -> YTMusic:
        if not self.is_authenticated():
            raise RuntimeError("Not authenticated. Please run auth flow.")
        return YTMusic(str(self.oauth_path))

    def start_oauth(self, client_id: str, client_secret: str) -> Dict[str, str]:
        """
        Starts the OAuth flow.
        Returns a dictionary with 'verification_url' and 'user_code'.
        """
        self._pending_credentials = OAuthCredentials(client_id, client_secret)
        code = self._pending_credentials.get_code()
        return {
            "verification_url": code["verification_url"],
            "user_code": code["user_code"],
            "device_code": code["device_code"],
            "interval": str(code.get("interval", 5))
        }

    def complete_oauth(self, device_code: str) -> str:
        """
        Completes the OAuth flow using the device code.
        Saves the token to oauth.json.
        """
        if not self._pending_credentials:
            raise RuntimeError("No pending OAuth flow. Call start_oauth first.")

        # We need to verify the device code matches if we want to be strict, 
        # but ytmusicapi's token_from_code just takes the code.
        # However, we need the SAME OAuthCredentials instance because it has the client_id/secret.
        
        token = self._pending_credentials.token_from_code(device_code)
        
        # Create RefreshingToken to save it properly
        refreshing_token = RefreshingToken(
            credentials=self._pending_credentials,
            **token
        )
        
        # Save to file
        refreshing_token.store_token(str(self.oauth_path))
        
        # Clear pending
        self._pending_credentials = None
        
        return "Authentication successful. oauth.json created."
