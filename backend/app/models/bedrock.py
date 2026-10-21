"""Bedrock region and model data models."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class RegionPrefix(str, Enum):
    US = "us"
    EU = "eu"
    AU = "au"
    APAC = "apac"


class RegionInfo(BaseModel):
    region: str
    prefix: str
    supports_on_demand: bool
    supports_inference_profiles: bool
    inference_profile_prefix: str


class ModelResolveRequest(BaseModel):
    region: str
    model: str = Field(..., description="Foundation model identifier")


class ModelResolveResponse(BaseModel):
    region: str
    requested_model: str
    resolved_model: str
    is_inference_profile: bool
    prefix_used: str


class RegionMapResponse(BaseModel):
    regions: Dict[str, str]


class SupportedModelsResponse(BaseModel):
    models: List[str]


# Region to prefix mapping
REGION_PREFIX_MAP: Dict[str, RegionPrefix] = {
    "us-east-1": RegionPrefix.US,
    "us-east-2": RegionPrefix.US,
    "us-west-1": RegionPrefix.US,
    "us-west-2": RegionPrefix.US,
    "eu-west-1": RegionPrefix.EU,
    "eu-west-2": RegionPrefix.EU,
    "eu-west-3": RegionPrefix.EU,
    "eu-central-1": RegionPrefix.EU,
    "eu-central-2": RegionPrefix.EU,
    "eu-north-1": RegionPrefix.EU,
    "eu-south-1": RegionPrefix.EU,
    "eu-south-2": RegionPrefix.EU,
    "ap-southeast-2": RegionPrefix.AU,
    "ap-southeast-4": RegionPrefix.AU,
    "ap-southeast-1": RegionPrefix.APAC,
    "ap-southeast-3": RegionPrefix.APAC,
    "ap-northeast-1": RegionPrefix.APAC,
    "ap-northeast-2": RegionPrefix.APAC,
    "ap-northeast-3": RegionPrefix.APAC,
    "ap-east-1": RegionPrefix.APAC,
    "ap-south-1": RegionPrefix.APAC,
    "ap-south-2": RegionPrefix.APAC,
    "ca-central-1": RegionPrefix.US,
    "ca-west-1": RegionPrefix.US,
    "me-south-1": RegionPrefix.EU,
    "me-central-1": RegionPrefix.EU,
    "af-south-1": RegionPrefix.EU,
    "sa-east-1": RegionPrefix.US,
    "us-gov-east-1": RegionPrefix.US,
    "us-gov-west-1": RegionPrefix.US,
}

ANTHROPIC_MODELS = [
    "claude-opus-4",
    "claude-sonnet-4",
    "claude-haiku-4",
    "claude-3-5-sonnet",
    "claude-3-5-haiku",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
]