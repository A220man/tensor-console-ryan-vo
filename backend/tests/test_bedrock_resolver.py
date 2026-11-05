import pytest
from app.services.bedrock_resolver import BedrockResolverService
from app.models.bedrock import REGION_PREFIX_MAP, RegionPrefix, ANTHROPIC_MODELS


service = BedrockResolverService()


class TestRegionPrefixMapping:
    """Test region to geographic prefix mapping."""

    def test_us_regions_map_to_us(self):
        us_regions = ["us-east-1", "us-east-2", "us-west-1", "us-west-2"]
        for region in us_regions:
            assert service.get_region_prefix(region) == RegionPrefix.US

    def test_eu_regions_map_to_eu(self):
        eu_regions = ["eu-west-1", "eu-west-2", "eu-central-1", "eu-north-1"]
        for region in eu_regions:
            assert service.get_region_prefix(region) == RegionPrefix.EU

    def test_au_regions_map_to_au(self):
        au_regions = ["ap-southeast-2", "ap-southeast-4"]
        for region in au_regions:
            assert service.get_region_prefix(region) == RegionPrefix.AU

    def test_apac_regions_map_to_apac(self):
        apac_regions = ["ap-southeast-1", "ap-northeast-1", "ap-south-1"]
        for region in apac_regions:
            assert service.get_region_prefix(region) == RegionPrefix.APAC

    def test_unknown_region_defaults_to_us(self):
        assert service.get_region_prefix("unknown-region-1") == RegionPrefix.US
        assert service.get_region_prefix("") == RegionPrefix.US

    def test_case_insensitive(self):
        assert service.get_region_prefix("US-EAST-1") == RegionPrefix.US
        assert service.get_region_prefix("Ap-Southeast-2") == RegionPrefix.AU


class TestInferenceProfileResolution:
    """Test foundation model to inference profile resolution."""

    def test_au_region_resolves_to_au_profile(self):
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved.startswith("au.anthropic.")
        assert "claude-3-5-sonnet" in resolved
        assert resolved.endswith(":0"), "Version suffix should be preserved"

    def test_eu_region_resolves_to_eu_profile(self):
        model_id = "anthropic.claude-3-opus-20240229-v1:0"
        resolved = service.resolve_inference_profile("eu-west-1", model_id)
        assert resolved.startswith("eu.anthropic.")
        assert "claude-3-opus" in resolved
        assert resolved.endswith(":0"), "Version suffix should be preserved"

    def test_us_region_resolves_to_us_profile(self):
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        resolved = service.resolve_inference_profile("us-east-1", model_id)
        assert resolved.startswith("us.anthropic.")
        assert "claude-3-haiku" in resolved
        assert resolved.endswith(":0"), "Version suffix should be preserved"

    def test_apac_region_resolves_to_apac_profile(self):
        model_id = "anthropic.claude-sonnet-4-20250514-v1:0"
        resolved = service.resolve_inference_profile("ap-northeast-1", model_id)
        assert resolved.startswith("apac.anthropic.")
        assert "claude-sonnet-4" in resolved
        assert resolved.endswith(":0"), "Version suffix should be preserved"

    def test_unknown_model_falls_back_to_extracted_name(self):
        model_id = "anthropic.unknown-model-123:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.unknown-model-123:0", "Version should be preserved for unknown models too"

    def test_model_id_without_provider_prefix(self):
        model_id = "claude-3-5-sonnet-20241022-v2:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved.startswith("au.anthropic.")
        assert "claude-3-5-sonnet" in resolved
        assert resolved.endswith(":0"), "Version suffix should be preserved"

    def test_version_preservation_v1(self):
        """Test that v1:0 version format is preserved."""
        model_id = "anthropic.claude-3-opus-20240229-v1:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.claude-3-opus:v1:0"

    def test_version_preservation_v2(self):
        """Test that v2:0 version format is preserved."""
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.claude-3-5-sonnet:v2:0"

    def test_trailing_colon_no_version(self):
        """Test that trailing colon without version doesn't add empty version."""
        model_id = "anthropic.claude-3-5-sonnet:"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.claude-3-5-sonnet", "Should not add empty version suffix"

    def test_multiple_colons_ignores_invalid_version(self):
        """Test that extra colons with non-version content are ignored."""
        model_id = "anthropic.claude-3-5-sonnet:v2:0:extra"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.claude-3-5-sonnet", "Should ignore non-standard version suffix"

    def test_colon_with_numeric_version(self):
        """Test that :N version format is handled (legacy format)."""
        model_id = "anthropic.claude-3-5-sonnet:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.claude-3-5-sonnet:0", "Numeric version after colon should be preserved"

    def test_model_without_version_or_colon(self):
        """Test model ID without any version or colon."""
        model_id = "anthropic.claude-3-5-sonnet"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.claude-3-5-sonnet", "Should work without version"


class TestRegionMapCompleteness:
    """Test region map covers all major AWS regions."""

    def test_all_mapped_regions_have_prefix(self):
        for region, prefix in REGION_PREFIX_MAP.items():
            assert prefix in RegionPrefix
            assert isinstance(prefix, RegionPrefix)

    def test_key_regions_present(self):
        required_regions = [
            "us-east-1", "us-west-2",
            "eu-west-1", "eu-central-1",
            "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
            "ca-central-1", "sa-east-1",
        ]
        for region in required_regions:
            assert region in REGION_PREFIX_MAP, f"Missing required region: {region}"


class TestResolveModelAPI:
    """Test the resolve_model service method."""

    def test_au_region_returns_inference_profile(self):
        result = service.resolve_model("ap-southeast-2", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        assert result.is_inference_profile is True
        assert result.resolved_model.startswith("au.anthropic.")
        assert result.resolved_model.endswith(":0")
        assert result.prefix_used == "au"

    def test_us_region_returns_foundation_model(self):
        result = service.resolve_model("us-east-1", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        assert result.is_inference_profile is False
        assert result.resolved_model == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert result.prefix_used == "us"

    def test_region_info_au_requires_profile(self):
        info = service.get_region_info("ap-southeast-2")
        assert info.supports_on_demand is False
        assert info.supports_inference_profiles is True
        assert info.inference_profile_prefix == "au.anthropic"

    def test_region_info_us_supports_on_demand(self):
        info = service.get_region_info("us-east-1")
        assert info.supports_on_demand is True
        assert info.inference_profile_prefix == "us.anthropic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import time

class TestLRUCaching:
    """Test LRU caching behavior on model extraction."""

    def test_extract_base_model_cache_hit(self):
        """Test that repeated calls with same model ID use cache."""
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        # Clear cache first
        service._extract_base_model.cache_clear()
        
        # First call - cache miss
        result1 = service._extract_base_model(model_id)
        cache_info_after_first = service._extract_base_model.cache_info()
        
        # Second call - should hit cache
        result2 = service._extract_base_model(model_id)
        cache_info_after_second = service._extract_base_model.cache_info()
        
        assert result1 == result2 == ("claude-3-5-sonnet", "v2:0")
        # Cache hit should increment hits counter
        assert cache_info_after_second.hits == cache_info_after_first.hits + 1
        assert cache_info_after_second.misses == cache_info_after_first.misses

    def test_extract_base_model_cache_different_inputs(self):
        """Test that different model IDs produce different cache entries."""
        model_ids = [
            "anthropic.claude-3-opus-20240229-v1:0",
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
        ]
        
        results = [service._extract_base_model(mid) for mid in model_ids]
        
        assert results[0] == ("claude-3-opus", "v1:0")
        assert results[1] == ("claude-3-5-sonnet", "v2:0")
        assert results[2] == ("claude-3-haiku", "v1:0")
        
        # Repeated calls should all hit cache
        for mid, expected in zip(model_ids, results):
            assert service._extract_base_model(mid) == expected

    def test_resolve_inference_profile_uses_cache(self):
        """Test that resolve_inference_profile benefits from cached extraction."""
        region = "ap-southeast-2"
        model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        # First resolution - cache miss on extraction
        start = time.perf_counter()
        result1 = service.resolve_inference_profile(region, model_id)
        first_time = time.perf_counter() - start
        
        # Second resolution - should hit extraction cache
        start = time.perf_counter()
        result2 = service.resolve_inference_profile(region, model_id)
        second_time = time.perf_counter() - start
        
        assert result1 == result2 == "au.anthropic.claude-3-5-sonnet:v2:0"
        # Second call should be faster due to cache
        assert second_time < first_time / 2, "Cached resolution should be faster"

    def test_cache_maxsize_respected(self):
        """Test that cache respects maxsize limit (256 entries)."""
        # Clear any existing cache
        service._extract_base_model.cache_clear()
        
        # Generate 300 unique model IDs (exceeds maxsize=256)
        model_ids = [f"anthropic.custom-model-{i}:0" for i in range(300)]
        
        for mid in model_ids:
            service._extract_base_model(mid)
        
        # Cache info should show max 256 entries
        cache_info = service._extract_base_model.cache_info()
        assert cache_info.currsize <= 256
        assert cache_info.maxsize == 256
    pytest.main([__file__, "-v"])
