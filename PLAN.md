# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

bedrock-version-preservation

## Roadmap

### skeleton — FastAPI/React skeleton with Docker Compose

Status: done

Acceptance:
- FastAPI app runs with health endpoint
- React + TypeScript + Vite frontend builds
- Docker Compose starts backend, frontend, Keycloak
- Backend tests pass (pytest)
- Frontend typecheck and tests pass

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/api/health.py`, `backend/requirements.txt`, `backend/tests/test_health.py`, `frontend/package.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/tests/App.test.tsx`, `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`

Tests: `backend/tests/test_health.py`, `frontend/tests/App.test.tsx`

### bedrock-region-resolver — Bedrock cross-region inference profile resolver

Status: done

Acceptance:
- Maps AWS regions to correct geographic prefix (us/eu/au/apac)
- Resolves foundation model IDs to invokeable inference profile IDs per region
- Handles AU region (ap-southeast-2) → au.anthropic.* profiles
- Unit tests cover all region mappings and model resolution

Implementation: `backend/app/models/bedrock.py`, `backend/app/services/bedrock_resolver.py`, `backend/app/api/bedrock.py`, `backend/tests/test_bedrock_resolver.py`

Tests: `backend/tests/test_bedrock_resolver.py`

### bootstrap-token-refresh — Bootstrap endpoint with token refresh handling

Status: done

Acceptance:
- Bootstrap endpoint validates Azure AD token via fastapi_azure_auth
- Returns gateway_token and bootstrap_expires_at
- Client-side token refresh logic documented
- Integration test covers expired token rejection

Implementation: `backend/app/api/bootstrap.py`, `backend/tests/test_bootstrap.py`

Tests: `backend/tests/test_bootstrap.py`

### plugin-hooks-validator — Plugin hooks.json schema validator

Status: done

Acceptance:
- Validates hooks.json against correct schema ({"hooks": {}})
- Rejects bare array [] with clear error message
- CLI command to validate all plugin hooks.json files
- Pre-commit hook integration

Implementation: `scripts/validate-hooks.py`, `backend/tests/test_plugin_validator.py`

Tests: `backend/tests/test_plugin_validator.py`

### mcp-json-validator — MCP JSON configuration validator

Status: done

Acceptance:
- Validates .mcp.json files for syntax and structure
- Detects missing commas, unclosed braces
- CLI command validates all .mcp.json in plugin directories
- CI integration

Implementation: `scripts/validate-mcp.py`, `backend/tests/test_plugin_validator.py`

Tests: `backend/tests/test_plugin_validator.py`

### frontend-dashboard — React dashboard with Bedrock region configuration

Status: done

Acceptance:
- Dashboard shows Bedrock region selector
- Displays resolved inference profile prefix for selected region
- Shows model invocation test results
- Loading/error/empty states

Implementation: `frontend/src/components/BedrockRegionSelector.tsx`, `frontend/src/pages/Dashboard.tsx`, `frontend/tests/App.test.tsx`

Tests: `frontend/tests/App.test.tsx`

### bedrock-version-preservation — Bedrock inference profile version preservation and caching

Status: done

Acceptance:
- Preserves Bedrock model version suffixes (v1:0, v2:0) in inference profile resolution
- Handles date-suffixed model IDs (e.g., claude-3-opus-20240229-v1:0)
- LRU caching on model extraction for repeated resolutions
- Unit tests cover version preservation and caching behavior

Implementation: `backend/app/services/bedrock_resolver.py`, `backend/tests/test_bedrock_resolver.py`

Tests: `backend/tests/test_bedrock_resolver.py`

