from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "tensor-console"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = "sqlite+aiosqlite:///./tensor_console.db"

    # Keycloak / OIDC
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "tensor-console"
    keycloak_client_id: str = "tensor-console-backend"
    keycloak_client_secret: Optional[str] = None

    # Azure AD (for bootstrap)
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None

    # LLM Providers
    llm_provider: str = "openai-compatible"
    llm_model: str = "gpt-4o-mini"
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None

    # AWS Bedrock
    aws_default_region: str = "us-east-1"
    aws_role_arn: Optional[str] = None

    # Frontend
    frontend_url: str = "http://localhost:5173"


settings = Settings()