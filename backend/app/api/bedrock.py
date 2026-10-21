from fastapi import APIRouter
from app.services.bedrock_resolver import BedrockResolverService
from app.models.bedrock import (
    RegionInfo,
    ModelResolveRequest,
    ModelResolveResponse,
)

router = APIRouter()
service = BedrockResolverService()


@router.post("/region-info", response_model=RegionInfo)
async def region_info(region: str) -> RegionInfo:
    """Get region capabilities and prefix info."""
    return service.get_region_info(region)


@router.post("/resolve-model", response_model=ModelResolveResponse)
async def resolve_model(request: ModelResolveRequest) -> ModelResolveResponse:
    """Resolve foundation model to invokeable identifier for region."""
    return service.resolve_model(request.region, request.model)


@router.get("/region-map")
async def region_map() -> dict:
    """Get full region to prefix mapping."""
    return service.get_region_map()


@router.get("/supported-models")
async def supported_models() -> list[str]:
    """Get list of known Anthropic model base names."""
    return service.get_supported_models()