# Changelog

## 1.5.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.4.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.3.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.2.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

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

### Added (this checkpoint)
- Bedrock inference profile version preservation: extracts and preserves `v1:0`, `v2:0` version suffixes
- Date suffix handling: strips `-20240229`, `-20241022`, `-20250514` date patterns from model IDs
- LRU caching (maxsize=256) on model extraction for repeated inference profile resolutions
- New unit tests: `test_version_preservation_v1`, `test_version_preservation_v2`

### Added (this round)
- LRU caching validation tests: `test_extract_base_model_cache_hit`, `test_extract_base_model_cache_different_inputs`, `test_resolve_inference_profile_uses_cache`, `test_cache_maxsize_respected`

### Added (database persistence layer)
- SQLAlchemy async database models: ResolutionHistory, PluginValidationLog, AuditLog
- Database initialization and session management with lifespan handlers
- DatabaseService for CRUD operations on all models
- REST API endpoints under `/api/v1/database/*` for history and audit queries
- Unit tests for all models and service operations (10 tests)

### Added (resolution history integration)
- POST `/api/v1/bedrock/resolve-model` now persists resolutions to database
- Frontend Dashboard shows Resolution History section with persisted entries
- History table displays: timestamp, region, requested model, resolved model, type (profile/on-demand), prefix
- History auto-refreshes after new model resolutions
- New API client function: `fetchResolutionHistory`
- New frontend component: `ResolutionHistory`
- Unit tests updated to mock database API calls

### Planned
- Audit logging for configuration changes
- LLM adapter implementations (OpenAI, Anthropic, Gemini, Ollama)
- Model invocation test execution (not just resolution)
- Plugin marketplace integration
- SAML identity broker documentation
- Production deployment guide
