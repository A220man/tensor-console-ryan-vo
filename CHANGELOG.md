# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-21

### Added
- FastAPI backend with health, bootstrap, and Bedrock resolver endpoints
- React + TypeScript + Vite frontend with dashboard
- Bedrock region resolver: maps 32 AWS regions to geographic prefixes (us/eu/au/apac)
- Cross-region inference profile resolution for Anthropic Claude models
- AU region (ap-southeast-2, ap-southeast-4) support with `au.anthropic.*` profiles
- Bootstrap endpoint with Azure AD token validation via fastapi_azure_auth
- Plugin hooks.json schema validator (detects bare `[]` bug)
- Plugin .mcp.json syntax validator (detects missing commas, unclosed braces)
- Keycloak OIDC integration with realm export (viewer/operator/admin roles)
- Docker Compose with backend, frontend, and Keycloak
- Comprehensive test suite (backend pytest, frontend vitest)
- CI-ready configuration

### Security
- OIDC authorization-code flow with PKCE
- Role-based access control on all data endpoints
- Non-root Docker users
- Environment-based secret management
- No hardcoded credentials

## [Unreleased]

### Planned
- Database models and persistence layer
- Audit logging for configuration changes
- LLM adapter implementations (OpenAI, Anthropic, Gemini, Ollama)
- Model invocation test execution (not just resolution)
- Plugin marketplace integration
- SAML identity broker documentation
- Production deployment guide