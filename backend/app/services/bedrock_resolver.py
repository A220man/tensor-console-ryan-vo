"""Bedrock region resolver service."""

from functools import lru_cache
import re
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

    @lru_cache(maxsize=256)
    def _extract_base_model(self, foundation_model_id: str) -> tuple[str, str | None]:
        """Extract base model name and version from foundation model ID.
        
        Returns (base_model, version) where version includes the full version suffix
        e.g., "anthropic.claude-3-5-sonnet-20241022-v2:0" -> ("claude-3-5-sonnet", "v2:0")
        """
        model_name = foundation_model_id
        version = None
        
        # Remove provider prefix (e.g., "anthropic.")
        if "." in model_name:
            model_name = model_name.split(".", 1)[1]
        
        # Extract version suffix (e.g., "v1:0", "v2:0") - pattern is v<number>:<number> at end
        version_match = re.search(r'(v\d+:\d+)$', model_name)
        if version_match:
            version = version_match.group(1)
            model_name = model_name[:version_match.start()].rstrip('-')
        elif ":" in model_name:
            # Fallback: just take everything after the last colon
            parts = model_name.split(":")
            version = parts[-1]
            model_name = ":".join(parts[:-1]).rstrip('-')
            if version.isdigit():
                version = f":{version}"
            else:
                version = f":{version}"
        
        # Remove date suffix if present (e.g., -20240229, -20241022, -20250514)
        model_name = re.sub(r'-\d{8}$', '', model_name)
        
        # Extract base model from known list (after cleaning)
        base_model = None
        for known in ANTHROPIC_MODELS:
            if known in model_name.lower():
                base_model = known
                break

        if not base_model:
            base_model = model_name
            
        return base_model, version

    def resolve_inference_profile(self, region: str, foundation_model_id: str) -> str:
        """Resolve foundation model ID to invokeable inference profile ID."""
        prefix = self.get_region_prefix(region)

        base_model, version = self._extract_base_model(foundation_model_id)

        profile = f"{prefix.value}.anthropic.{base_model}"
        if version:
            # Version already includes prefix like 'v1:0' or ':0', add separator
            profile += version if version.startswith(':') else f":{version}"
            
        return profile

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
