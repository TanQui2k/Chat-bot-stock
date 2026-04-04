"""Google OAuth Service - Xác thực Google Access Token thông qua Userinfo API."""

import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleAuthError(Exception):
    """Raised when Google authentication fails."""
    pass


class GoogleUserInfo:
    """Parsed Google user information."""
    def __init__(self, data: dict):
        self.google_id: str = data.get("sub", "")
        self.email: Optional[str] = data.get("email")
        self.email_verified: bool = data.get("email_verified", False)
        self.full_name: Optional[str] = data.get("name")
        self.avatar_url: Optional[str] = data.get("picture")
        self.locale: Optional[str] = data.get("locale")

    def to_dict(self) -> dict:
        return {
            "google_id": self.google_id,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
        }


async def verify_google_access_token(access_token: str) -> GoogleUserInfo:
    """
    Verify a Google OAuth2 access token by calling Google's Userinfo endpoint.
    
    Args:
        access_token: The OAuth2 access token from the frontend Google login flow.
        
    Returns:
        GoogleUserInfo with the user's profile data from Google.
        
    Raises:
        GoogleAuthError: If the token is invalid, expired, or the API call fails.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        if response.status_code == 401:
            raise GoogleAuthError("Google access token is invalid or expired")
        
        if response.status_code != 200:
            logger.error(f"Google Userinfo API returned status {response.status_code}: {response.text}")
            raise GoogleAuthError(f"Google API error (status {response.status_code})")
        
        data = response.json()
        
        if not data.get("sub"):
            raise GoogleAuthError("Google response missing user ID (sub)")
        
        logger.info(f"Google auth verified for user: {data.get('email', 'unknown')}")
        return GoogleUserInfo(data)
        
    except GoogleAuthError:
        raise  # Re-raise our own errors without wrapping
    except httpx.TimeoutException:
        raise GoogleAuthError("Google API request timed out")
    except httpx.RequestError as e:
        logger.error(f"Google API request failed: {e}")
        raise GoogleAuthError("Failed to connect to Google API")
