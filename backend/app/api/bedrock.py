from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.bedrock_resolver import BedrockResolverService
from app.models.bedrock import (
    RegionInfo,
    ModelResolveRequest,
    ModelResolveResponse,
)
from app.core.database import get_db
from app.services.database_service import DatabaseService

router = APIRouter()
service = BedrockResolverService()


@router.post("/region-info", response_model=RegionInfo)
async def region_info(region: str) -> RegionInfo:
    """Get region capabilities and prefix info."""
    return service.get_region_info(region)


@router.post("/resolve-model", response_model=ModelResolveResponse)
async def resolve_model(
    request: ModelResolveRequest,
    db: AsyncSession = Depends(get_db)
) -> ModelResolveResponse:
    """Resolve foundation model to invokeable identifier for region."""
    response = service.resolve_model(request.region, request.model)

    # Save resolution to history
    db_service = DatabaseService(db)
    await db_service.save_resolution(
        region=request.region,
        requested_model=request.model,
        resolved_model=response.resolved_model,
        is_inference_profile=response.is_inference_profile,
        prefix_used=response.prefix_used,
    )

    return response


@router.get("/region-map")
async def region_map() -> dict:
    """Get full region to prefix mapping."""
    return service.get_region_map()


@router.get("/supported-models")
async def supported_models() -> list[str]:
    """Get list of known Anthropic model base names."""
    return service.get_supported_models()
