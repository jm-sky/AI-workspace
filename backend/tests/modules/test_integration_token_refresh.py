"""Tests for integration OAuth token refresh (service cascade + GitHub provider)."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.modules.integrations.exceptions import (
    IntegrationRefreshFailedError,
    IntegrationRefreshNotSupportedError,
    IntegrationTokenExpiredError,
)
from app.modules.integrations.providers.base import IntegrationOAuthTokenResult
from app.modules.integrations.providers.github import GitHubIntegrationProvider
from app.modules.integrations.service import IntegrationTokenService


def _token_row(*, expires_at, has_refresh=True, provider="github"):
    row = MagicMock()
    row.provider = provider
    row.expires_at = expires_at
    row.encrypted_refresh_token = "encrypted-refresh" if has_refresh else None
    return row


def _repo(row):
    repo = MagicMock()
    repo.find_user_scoped = AsyncMock(return_value=row)
    repo.decrypt_access_token.return_value = "stored-access-token"
    repo.decrypt_refresh_token.return_value = "ghr_stored_refresh"
    repo.update_tokens = AsyncMock(return_value=row)
    return repo


def _registry(provider):
    registry = MagicMock()
    registry.get.return_value = provider
    return registry


class TestServiceRefresh:
    """Expiry handling in IntegrationTokenService."""

    @pytest.mark.asyncio
    async def test_valid_token_is_returned_without_refresh(self):
        row = _token_row(expires_at=datetime.now(UTC) + timedelta(hours=2))
        repo = _repo(row)
        provider = MagicMock()
        provider.refresh_access_token = AsyncMock()

        service = IntegrationTokenService(repo, registry=_registry(provider))
        result = await service.get_access_token("user-1", "github")

        assert result == "stored-access-token"
        provider.refresh_access_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_expired_token_is_refreshed_and_persisted(self):
        row = _token_row(expires_at=datetime.now(UTC) - timedelta(minutes=5))
        repo = _repo(row)
        new_expiry = datetime.now(UTC) + timedelta(hours=8)
        provider = MagicMock()
        provider.refresh_access_token = AsyncMock(
            return_value=IntegrationOAuthTokenResult(
                access_token="ghu_fresh",
                refresh_token="ghr_fresh",
                expires_at=new_expiry,
                scope="github-app",
            )
        )

        service = IntegrationTokenService(repo, registry=_registry(provider))
        result = await service.get_access_token("user-1", "github")

        assert result == "ghu_fresh"
        provider.refresh_access_token.assert_awaited_once_with("ghr_stored_refresh")
        repo.update_tokens.assert_awaited_once()
        kwargs = repo.update_tokens.await_args.kwargs
        assert kwargs["access_token"] == "ghu_fresh"
        assert kwargs["refresh_token"] == "ghr_fresh"
        assert kwargs["expires_at"] == new_expiry

    @pytest.mark.asyncio
    async def test_token_expiring_within_skew_is_refreshed(self):
        row = _token_row(expires_at=datetime.now(UTC) + timedelta(seconds=30))
        repo = _repo(row)
        provider = MagicMock()
        provider.refresh_access_token = AsyncMock(return_value=IntegrationOAuthTokenResult(access_token="ghu_fresh"))

        service = IntegrationTokenService(repo, registry=_registry(provider))
        result = await service.get_access_token("user-1", "github")

        assert result == "ghu_fresh"
        provider.refresh_access_token.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_expired_without_refresh_token_raises(self):
        row = _token_row(expires_at=datetime.now(UTC) - timedelta(minutes=5), has_refresh=False)
        repo = _repo(row)
        repo.decrypt_refresh_token.return_value = None

        service = IntegrationTokenService(repo, registry=_registry(MagicMock()))

        with pytest.raises(IntegrationTokenExpiredError, match="no refresh token"):
            await service.get_access_token("user-1", "github")

    @pytest.mark.asyncio
    async def test_provider_without_refresh_support_raises_expired(self):
        row = _token_row(expires_at=datetime.now(UTC) - timedelta(minutes=5))
        repo = _repo(row)
        provider = MagicMock()
        provider.refresh_access_token = AsyncMock(side_effect=IntegrationRefreshNotSupportedError("cannot refresh"))

        service = IntegrationTokenService(repo, registry=_registry(provider))

        with pytest.raises(IntegrationTokenExpiredError, match="re-authenticate"):
            await service.get_access_token("user-1", "github")
        repo.update_tokens.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_refresh_rejected_by_provider_raises_expired(self):
        row = _token_row(expires_at=datetime.now(UTC) - timedelta(minutes=5))
        repo = _repo(row)
        provider = MagicMock()
        provider.refresh_access_token = AsyncMock(side_effect=IntegrationRefreshFailedError("bad_refresh_token"))

        service = IntegrationTokenService(repo, registry=_registry(provider))

        with pytest.raises(IntegrationTokenExpiredError, match="bad_refresh_token"):
            await service.get_access_token("user-1", "github")
        repo.update_tokens.assert_not_awaited()


def _patch_httpx(monkeypatch, handler):
    """Route the provider's httpx client through a MockTransport.

    ``github.httpx`` is the httpx module itself, so bind the real class first —
    otherwise the replacement recurses into the patched attribute.
    """
    real_client = httpx.AsyncClient

    def factory(*_args, **_kwargs):
        return real_client(transport=httpx.MockTransport(handler))

    monkeypatch.setattr("app.modules.integrations.providers.github.httpx.AsyncClient", factory)


class TestGitHubProviderRefresh:
    """GitHub-specific refresh behaviour."""

    def _configure(self, monkeypatch, *, app_id="12345"):
        for name, value in (
            ("github_oauth_client_id", "Iv1.client"),
            ("github_oauth_client_secret", "secret"),
            ("github_oauth_redirect_uri", "https://example.test/cb"),
            ("github_app_id", app_id),
        ):
            monkeypatch.setattr(
                f"app.modules.integrations.providers.github.settings.integrations.{name}",
                value,
            )

    @pytest.mark.asyncio
    async def test_oauth_app_cannot_refresh(self, monkeypatch):
        self._configure(monkeypatch, app_id="")
        provider = GitHubIntegrationProvider()

        with pytest.raises(IntegrationRefreshNotSupportedError):
            await provider.refresh_access_token("ghr_x")

    @pytest.mark.asyncio
    async def test_successful_refresh_parses_response(self, monkeypatch):
        self._configure(monkeypatch)
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/login/oauth/access_token":
                captured["accept"] = request.headers["accept"]
                captured["body"] = request.content.decode()
                return httpx.Response(
                    200,
                    json={
                        "access_token": "ghu_fresh",
                        "expires_in": 28800,
                        "refresh_token": "ghr_fresh",
                        "refresh_token_expires_in": 15897600,
                        "scope": "",
                        "token_type": "bearer",
                    },
                )
            return httpx.Response(200, json={"login": "octocat"})

        _patch_httpx(monkeypatch, handler)

        provider = GitHubIntegrationProvider()
        result = await provider.refresh_access_token("ghr_stored")

        assert result.access_token == "ghu_fresh"
        assert result.refresh_token == "ghr_fresh"
        assert result.provider_metadata["login"] == "octocat"
        # GitHub only returns JSON for this exact Accept header.
        assert captured["accept"] == "application/json"
        assert "grant_type=refresh_token" in captured["body"]
        assert result.expires_at > datetime.now(UTC) + timedelta(hours=7)

    @pytest.mark.asyncio
    async def test_error_payload_raises_refresh_failed(self, monkeypatch):
        self._configure(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                json={
                    "error": "bad_refresh_token",
                    "error_description": "The refresh token expired.",
                },
            )

        _patch_httpx(monkeypatch, handler)

        provider = GitHubIntegrationProvider()
        with pytest.raises(IntegrationRefreshFailedError, match="refresh token expired"):
            await provider.refresh_access_token("ghr_stale")

    @pytest.mark.asyncio
    async def test_transport_error_raises_refresh_failed(self, monkeypatch):
        self._configure(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("boom")

        _patch_httpx(monkeypatch, handler)

        provider = GitHubIntegrationProvider()
        with pytest.raises(IntegrationRefreshFailedError):
            await provider.refresh_access_token("ghr_x")
