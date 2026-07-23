"""Gmail / Google OAuth provider for workspace integrations."""

from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.modules.integrations.exceptions import IntegrationRefreshFailedError
from app.modules.integrations.providers.base import (
    IntegrationOAuthProvider,
    IntegrationOAuthTokenResult,
)
from app.modules.integrations.types import DEFAULT_GMAIL_SCOPES


class GmailIntegrationProvider(IntegrationOAuthProvider):
    """Google OAuth for Gmail API (readonly) with refresh tokens."""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def _client_id(self) -> str:
        return settings.integrations.gmail_oauth_client_id

    def _client_secret(self) -> str:
        return settings.integrations.gmail_oauth_client_secret

    def _redirect_uri(self) -> str:
        return settings.integrations.gmail_oauth_redirect_uri

    def is_configured(self) -> bool:
        return bool(self._client_id() and self._client_secret() and self._redirect_uri())

    def get_authorization_url(self, *, state: str, scopes: list[str]) -> str:
        if not self.is_configured():
            raise ValueError("Gmail integration is not configured")

        scope_list = scopes or DEFAULT_GMAIL_SCOPES
        params = {
            "client_id": self._client_id(),
            "redirect_uri": self._redirect_uri(),
            "response_type": "code",
            "scope": " ".join(scope_list),
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str, *, scopes: list[str]) -> IntegrationOAuthTokenResult:
        if not self.is_configured():
            raise ValueError("Gmail integration is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self._client_id(),
                    "client_secret": self._client_secret(),
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self._redirect_uri(),
                },
                headers={"Accept": "application/json"},
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise ValueError(data.get("error_description") or data.get("error", "Google OAuth error"))

            access_token = data["access_token"]
            metadata = await self._fetch_user_metadata(client, access_token)

            expires_at = None
            if data.get("expires_in"):
                expires_at = datetime.now(UTC) + timedelta(seconds=int(data["expires_in"]))

            return IntegrationOAuthTokenResult(
                access_token=access_token,
                token_type=data.get("token_type", "Bearer"),
                scope=data.get("scope") or " ".join(scopes or DEFAULT_GMAIL_SCOPES),
                refresh_token=data.get("refresh_token"),
                expires_at=expires_at,
                provider_metadata=metadata,
            )

    async def refresh_access_token(self, refresh_token: str) -> IntegrationOAuthTokenResult:
        if not self.is_configured():
            raise ValueError("Gmail integration is not configured")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self._client_id(),
                        "client_secret": self._client_secret(),
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    },
                    headers={"Accept": "application/json"},
                    timeout=15.0,
                )
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as exc:
                raise IntegrationRefreshFailedError(f"Gmail refresh request failed: {exc}") from exc

            if "error" in data:
                raise IntegrationRefreshFailedError(data.get("error_description") or data["error"])

            access_token = data["access_token"]
            metadata = await self._fetch_user_metadata(client, access_token)

            expires_at = None
            if data.get("expires_in"):
                expires_at = datetime.now(UTC) + timedelta(seconds=int(data["expires_in"]))

            return IntegrationOAuthTokenResult(
                access_token=access_token,
                token_type=data.get("token_type", "Bearer"),
                scope=data.get("scope"),
                # Google may omit refresh_token on refresh — keep caller’s existing one.
                refresh_token=data.get("refresh_token") or refresh_token,
                expires_at=expires_at,
                provider_metadata=metadata,
            )

    async def _fetch_user_metadata(self, client: httpx.AsyncClient, access_token: str) -> dict[str, Any]:
        response = await client.get(
            self.USERINFO_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            timeout=15.0,
        )
        response.raise_for_status()
        user_data = response.json()
        return {
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "avatarUrl": user_data.get("picture"),
            "login": user_data.get("email"),
            "googleId": str(user_data.get("id")) if user_data.get("id") else None,
        }
