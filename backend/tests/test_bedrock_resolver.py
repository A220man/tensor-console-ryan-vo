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

    def test_eu_region_resolves_to_eu_profile(self):
        model_id = "anthropic.claude-3-opus-20240229-v1:0"
        resolved = service.resolve_inference_profile("eu-west-1", model_id)
        assert resolved.startswith("eu.anthropic.")
        assert "claude-3-opus" in resolved

    def test_us_region_resolves_to_us_profile(self):
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        resolved = service.resolve_inference_profile("us-east-1", model_id)
        assert resolved.startswith("us.anthropic.")
        assert "claude-3-haiku" in resolved

    def test_apac_region_resolves_to_apac_profile(self):
        model_id = "anthropic.claude-sonnet-4-20250514-v1:0"
        resolved = service.resolve_inference_profile("ap-northeast-1", model_id)
        assert resolved.startswith("apac.anthropic.")
        assert "claude-sonnet-4" in resolved

    def test_unknown_model_falls_back_to_extracted_name(self):
        model_id = "anthropic.unknown-model-123:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved == "au.anthropic.unknown-model-123"

    def test_model_id_without_provider_prefix(self):
        model_id = "claude-3-5-sonnet-20241022-v2:0"
        resolved = service.resolve_inference_profile("ap-southeast-2", model_id)
        assert resolved.startswith("au.anthropic.")
        assert "claude-3-5-sonnet" in resolved


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