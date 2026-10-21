"""Bedrock region resolver service."""

from app.models.bedrock import (
    REGION_PREFIX_MAP,
    ANTHROPIC_MODELS,
    RegionPrefix,
    RegionInfo,
    ModelResolveResponse,
)


class BedrockResolverService:
    """Service for resolving Bedrock inference profile identifiers by region."""

    INFERENCE_PROFILE_ONLY_REGIONS = {"ap-southeast-2", "ap-southeast-4"}

    def get_region_prefix(self, region: str) -> RegionPrefix:
        """Get geographic prefix for AWS region."""
        return REGION_PREFIX_MAP.get(region.lower(), RegionPrefix.US)

    def get_region_info(self, region: str) -> RegionInfo:
        """Get region capabilities and prefix info."""
        region_lower = region.lower()
        prefix = self.get_region_prefix(region_lower)

        requires_inference_profile = region_lower in self.INFERENCE_PROFILE_ONLY_REGIONS

        return RegionInfo(
            region=region_lower,
            prefix=prefix.value,
            supports_on_demand=not requires_inference_profile,
            supports_inference_profiles=True,
            inference_profile_prefix=f"{prefix.value}.anthropic",
        )

    def resolve_inference_profile(self, region: str, foundation_model_id: str) -> str:
        """Resolve foundation model ID to invokeable inference profile ID."""
        prefix = self.get_region_prefix(region)

        model_name = foundation_model_id
        if "." in foundation_model_id:
            model_name = foundation_model_id.split(".", 1)[1]
        if ":" in model_name:
            model_name = model_name.split(":", 1)[0]

        base_model = None
        for known in ANTHROPIC_MODELS:
            if known in model_name.lower():
                base_model = known
                break

        if not base_model:
            base_model = model_name

        return f"{prefix.value}.anthropic.{base_model}"

    def resolve_model(self, region: str, foundation_model_id: str) -> ModelResolveResponse:
        """Resolve foundation model to invokeable identifier for region."""
        region_lower = region.lower()
        prefix = self.get_region_prefix(region_lower)
        requires_profile = region_lower in self.INFERENCE_PROFILE_ONLY_REGIONS

        resolved = self.resolve_inference_profile(region_lower, foundation_model_id)

        return ModelResolveResponse(
            region=region_lower,
            requested_model=foundation_model_id,
            resolved_model=resolved if requires_profile else foundation_model_id,
            is_inference_profile=requires_profile,
            prefix_used=prefix.value,
        )

    def get_region_map(self) -> dict:
        """Get full region to prefix mapping."""
        return {region: prefix.value for region, prefix in REGION_PREFIX_MAP.items()}

    def get_supported_models(self) -> list[str]:
        """Get list of known Anthropic model base names."""
        return ANTHROPIC_MODELS.copy()