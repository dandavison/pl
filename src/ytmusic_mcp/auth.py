import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ytmusicapi.auth.oauth import OAuthCredentials, RefreshingToken
from ytmusicapi import YTMusic

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, oauth_path: str = "oauth.json", creds_path: str = "oauth_creds.json"):
        self.oauth_path = Path(oauth_path)
        self.creds_path = Path(creds_path)
        self._pending_credentials: Optional[OAuthCredentials] = None

    def is_authenticated(self) -> bool:
        return self.oauth_path.exists()

    def get_ytmusic(self) -> YTMusic:
        if not self.is_authenticated():
            raise RuntimeError("Not authenticated. Please run auth flow.")

        # Check if credentials file exists
        if self.creds_path.exists():
            # Load credentials from separate file
            with open(self.creds_path, 'r') as f:
                creds_data = json.load(f)

            creds = OAuthCredentials(
                client_id=creds_data['client_id'],
                client_secret=creds_data['client_secret']
            )
            # Pass oauth_credentials as separate parameter
            return YTMusic(auth=str(self.oauth_path), oauth_credentials=creds)
        else:
            # Legacy support: check if credentials are in oauth.json
            with open(self.oauth_path, 'r') as f:
                oauth_data = json.load(f)

            if 'oauth_credentials' in oauth_data:
                # Extract and save them separately
                creds_data = oauth_data['oauth_credentials']
                with open(self.creds_path, 'w') as f:
                    json.dump(creds_data, f, indent=2)

                # Clean the oauth.json file
                del oauth_data['oauth_credentials']
                with open(self.oauth_path, 'w') as f:
                    json.dump(oauth_data, f, indent=2)

                # Now use the credentials
                creds = OAuthCredentials(
                    client_id=creds_data['client_id'],
                    client_secret=creds_data['client_secret']
                )
                return YTMusic(auth=str(self.oauth_path), oauth_credentials=creds)
            else:
                # No credentials available - this might fail on token refresh
                logger.warning("No OAuth credentials found. Token refresh may fail.")
                return YTMusic(auth=str(self.oauth_path))

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
        Saves the token to oauth.json and credentials separately.
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

        # Save token WITHOUT credentials
        refreshing_token.store_token(str(self.oauth_path))

        # Save credentials separately
        creds_dict = {
            'client_id': self._pending_credentials.client_id,
            'client_secret': self._pending_credentials.client_secret
        }
        with open(self.creds_path, 'w') as f:
            json.dump(creds_dict, f, indent=2)

        # Clear pending
        self._pending_credentials = None

        return "Authentication successful. oauth.json and oauth_creds.json created."
