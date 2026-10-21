from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from fastapi_azure_auth.user import User
from pydantic import BaseModel
from typing import Optional
import time

from app.core.config import settings

router = APIRouter()

# Azure AD auth scheme for bootstrap endpoint
azure_scheme = None
if settings.azure_tenant_id and settings.azure_client_id:
    azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
        tenant_id=settings.azure_tenant_id,
        app_client_id=settings.azure_client_id,
    )


class BootstrapResponse(BaseModel):
    gateway_token: str
    bootstrap_expires_at: int


async def get_current_user() -> User:
    """Dependency for Azure AD authenticated user."""
    if not azure_scheme:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Azure AD not configured",
        )
    # This will be overridden by the actual Security dependency
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Auth scheme not initialized",
    )


@router.get("", response_model=BootstrapResponse)
async def bootstrap_endpoint(
    user: User = Security(azure_scheme) if azure_scheme else Depends(get_current_user),
) -> BootstrapResponse:
    """
    Bootstrap endpoint for LLM gateway.
    Validates Azure AD token and returns it as gateway token with expiry.
    Client MUST call acquireTokenSilent() before each request to refresh expired tokens.
    """
    username = user.preferred_username.lower() if user.preferred_username else "unknown"
    
    # Return the access token as gateway token with its expiry
    return BootstrapResponse(
        gateway_token=user.access_token,
        bootstrap_expires_at=user.claims.get("exp", int(time.time()) + 3600),
    )


@router.get("/config")
async def bootstrap_config():
    """Public configuration for bootstrap client."""
    return {
        "azure_tenant_id": settings.azure_tenant_id,
        "azure_client_id": settings.azure_client_id,
        "requires_token_refresh": True,
        "token_refresh_guidance": "Call acquireTokenSilent() via MSAL before each bootstrap request. Do not cache access tokens beyond their expiry.",
    }