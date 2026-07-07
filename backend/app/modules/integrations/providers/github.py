"""GitHub App OAuth provider for workspace integrations (user-to-server tokens)."""

from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.modules.integrations.providers.base import (
    IntegrationOAuthProvider,
    IntegrationOAuthTokenResult,
)
from app.modules.integrations.types import DEFAULT_GITHUB_SCOPES


class GitHubIntegrationProvider(IntegrationOAuthProvider):
    """GitHub App user authorization — not a standalone OAuth App.

    User-to-server tokens inherit permissions from the GitHub App manifest.
    Installation tokens (org-wide) are a separate flow — planned later.
    """

    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_API_URL = "https://api.github.com/user"

    def _client_id(self) -> str:
        return settings.integrations.github_oauth_client_id

    def _client_secret(self) -> str:
        return settings.integrations.github_oauth_client_secret

    def _redirect_uri(self) -> str:
        return settings.integrations.github_oauth_redirect_uri

    def _is_github_app(self) -> bool:
        return bool(settings.integrations.github_app_id)

    def _api_headers(self, access_token: str | None = None) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"{settings.app.name}-integrations",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        return headers

    def is_configured(self) -> bool:
        return bool(self._client_id() and self._client_secret() and self._redirect_uri())

    def get_authorization_url(self, *, state: str, scopes: list[str]) -> str:
        if not self.is_configured():
            raise ValueError("GitHub integration is not configured")

        params: dict[str, str] = {
            "client_id": self._client_id(),
            "redirect_uri": self._redirect_uri(),
            "state": state,
        }
        # GitHub App user tokens use manifest permissions — scope query is ignored.
        if not self._is_github_app():
            scope_list = scopes or DEFAULT_GITHUB_SCOPES
            params["scope"] = " ".join(scope_list)

        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(
        self, code: str, *, scopes: list[str]
    ) -> IntegrationOAuthTokenResult:
        if not self.is_configured():
            raise ValueError("GitHub integration is not configured")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self._client_id(),
                    "client_secret": self._client_secret(),
                    "code": code,
                    "redirect_uri": self._redirect_uri(),
                },
                headers=self._api_headers(),
                timeout=15.0,
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise ValueError(
                    data.get("error_description") or data.get("error", "GitHub OAuth error")
                )

            access_token = data["access_token"]
            metadata = await self._fetch_user_metadata(client, access_token)
            if self._is_github_app():
                metadata["githubAppId"] = settings.integrations.github_app_id

            expires_at = None
            if data.get("expires_in"):
                expires_at = datetime.now(UTC) + timedelta(seconds=int(data["expires_in"]))

            granted_scope = data.get("scope")
            if not granted_scope and not self._is_github_app():
                granted_scope = " ".join(scopes or DEFAULT_GITHUB_SCOPES)
            elif self._is_github_app():
                granted_scope = granted_scope or "github-app"

            return IntegrationOAuthTokenResult(
                access_token=access_token,
                token_type=data.get("token_type", "Bearer"),
                scope=granted_scope,
                refresh_token=data.get("refresh_token"),
                expires_at=expires_at,
                provider_metadata=metadata,
            )

    async def _fetch_user_metadata(
        self, client: httpx.AsyncClient, access_token: str
    ) -> dict[str, Any]:
        response = await client.get(
            self.USER_API_URL,
            headers=self._api_headers(access_token),
            timeout=15.0,
        )
        response.raise_for_status()
        user_data = response.json()
        return {
            "login": user_data.get("login"),
            "name": user_data.get("name"),
            "avatarUrl": user_data.get("avatar_url"),
            "htmlUrl": user_data.get("html_url"),
        }
