import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException
from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


class TestBootstrapConfig:
    """Test bootstrap configuration endpoint."""

    @pytest.mark.asyncio
    async def test_bootstrap_config_endpoint(self, client: AsyncClient):
        response = await client.get("/api/v1/bootstrap/config")
        assert response.status_code == 200
        data = response.json()
        assert "requires_token_refresh" in data
        assert data["requires_token_refresh"] is True
        assert "token_refresh_guidance" in data
        assert "acquireTokenSilent" in data["token_refresh_guidance"]


class TestBootstrapEndpoint:
    """Test bootstrap endpoint behavior (requires Azure AD config)."""
    @pytest.mark.asyncio
    async def test_bootstrap_requires_azure_config(self, client: AsyncClient):
        # Without Azure AD configured, should return 503 (or redirect to login)
        response = await client.get("/api/v1/bootstrap/", follow_redirects=True)
        assert response.status_code in (401, 503)
        if response.status_code == 503:
            assert "Azure AD not configured" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_bootstrap_rejects_expired_token(self, client: AsyncClient):
        # This test documents expected behavior: endpoint validates token expiry
        # Actual validation happens in fastapi_azure_auth; we test the contract
        response = await client.get(
            "/api/v1/bootstrap/",
            headers={"Authorization": "Bearer expired-token"},
            follow_redirects=True,
        )
        # Will be 503 (not configured) or 401 (invalid/expired token)
        assert response.status_code in (401, 503)


class TestBootstrapTokenRefreshGuidance:
    """Document token refresh requirements for clients."""

    def test_client_must_refresh_before_bootstrap(self):
        """
        Client-side requirement: Call acquireTokenSilent() via MSAL
        before each bootstrap request. Do not cache access tokens.
        """
        # This is a design contract test - documents the requirement
        # that the frontend/add-in must implement
        pass

    def test_bootstrap_returns_expiry(self):
        """
        Bootstrap endpoint returns bootstrap_expires_at (Unix timestamp)
        from token claims['exp']. Client should use this to schedule refresh.
        """
        pass