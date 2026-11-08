import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import ResolutionHistory, PluginValidationLog, AuditLog
from app.services.database_service import DatabaseService
from app.core.database import init_db, get_db_session, engine
from app.models.database import Base

@pytest_asyncio.fixture
async def db_session():
    """Create a fresh database session for each test."""
    await init_db()
    async with get_db_session() as session:
        yield session
    # Cleanup after test
    async with get_db_session() as session:
        await session.execute(delete(ResolutionHistory))
        await session.execute(delete(PluginValidationLog))
        await session.execute(delete(AuditLog))
        await session.commit()

@pytest_asyncio.fixture
async def db_service(db_session: AsyncSession):
    """Create a DatabaseService instance."""
    return DatabaseService(db_session)

class TestResolutionHistoryModel:
    """Test ResolutionHistory model."""

    def test_to_dict(self):
        """Test to_dict method."""
        history = ResolutionHistory(
            id=1,
            region="ap-southeast-2",
            requested_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            resolved_model="au.anthropic.claude-3-5-sonnet:v2:0",
            is_inference_profile=1,
            prefix_used="au",
        )
        data = history.to_dict()
        assert data["id"] == 1
        assert data["region"] == "ap-southeast-2"
        assert data["requested_model"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert data["resolved_model"] == "au.anthropic.claude-3-5-sonnet:v2:0"
        assert data["is_inference_profile"] is True
        assert data["prefix_used"] == "au"
        assert data["created_at"] is None  # Not set

class TestPluginValidationLogModel:
    """Test PluginValidationLog model."""

    def test_to_dict(self):
        """Test to_dict method."""
        log = PluginValidationLog(
            id=1,
            plugin_path="/plugins/my-plugin/hooks.json",
            validation_type="hooks",
            status="pass",
            error_message=None,
        )
        data = log.to_dict()
        assert data["id"] == 1
        assert data["plugin_path"] == "/plugins/my-plugin/hooks.json"
        assert data["validation_type"] == "hooks"
        assert data["status"] == "pass"
        assert data["error_message"] is None
        assert data["created_at"] is None

class TestAuditLogModel:
    """Test AuditLog model."""

    def test_to_dict(self):
        """Test to_dict method."""
        log = AuditLog(
            id=1,
            action="test_action",
            resource_type="test_resource",
        )
        data = log.to_dict()
        assert data["id"] == 1
        assert data["action"] == "test_action"
        assert data["resource_type"] == "test_resource"
        assert data["resource_id"] is None
        assert data["user_id"] is None
        assert data["details"] is None
        assert data["ip_address"] is None
        assert data["created_at"] is None

class TestDatabaseService:
    """Test DatabaseService operations."""

    @pytest.mark.asyncio
    async def test_save_resolution(self, db_service: DatabaseService):
        """Test saving a resolution."""
        history = await db_service.save_resolution(
            region="ap-southeast-2",
            requested_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            resolved_model="au.anthropic.claude-3-5-sonnet:v2:0",
            is_inference_profile=True,
            prefix_used="au",
        )
        assert history.id is not None
        assert history.region == "ap-southeast-2"
        assert history.is_inference_profile == 1

    @pytest.mark.asyncio
    async def test_get_resolution_history(self, db_service: DatabaseService):
        """Test getting resolution history."""
        # Save some resolutions
        await db_service.save_resolution(
            region="ap-southeast-2",
            requested_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            resolved_model="au.anthropic.claude-3-5-sonnet:v2:0",
            is_inference_profile=True,
            prefix_used="au",
        )
        await db_service.save_resolution(
            region="us-east-1",
            requested_model="anthropic.claude-3-opus-20240229-v1:0",
            resolved_model="us.anthropic.claude-3-opus:v1:0",
            is_inference_profile=True,
            prefix_used="us",
        )

        # Get all
        history = await db_service.get_resolution_history()
        assert len(history) == 2

        # Filter by region
        au_history = await db_service.get_resolution_history(region="ap-southeast-2")
        assert len(au_history) == 1
        assert au_history[0].region == "ap-southeast-2"

    @pytest.mark.asyncio
    async def test_get_resolution_count(self, db_service: DatabaseService):
        """Test getting resolution count."""
        await db_service.save_resolution(
            region="ap-southeast-2",
            requested_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            resolved_model="au.anthropic.claude-3-5-sonnet:v2:0",
            is_inference_profile=True,
            prefix_used="au",
        )
        count = await db_service.get_resolution_count()
        assert count == 1

        au_count = await db_service.get_resolution_count(region="ap-southeast-2")
        assert au_count == 1

        us_count = await db_service.get_resolution_count(region="us-east-1")
        assert us_count == 0

    @pytest.mark.asyncio
    async def test_save_plugin_validation(self, db_service: DatabaseService):
        """Test saving plugin validation."""
        log = await db_service.save_plugin_validation(
            plugin_path="/plugins/test/hooks.json",
            validation_type="hooks",
            status="pass",
        )
        assert log.id is not None
        assert log.validation_type == "hooks"
        assert log.status == "pass"

    @pytest.mark.asyncio
    async def test_get_plugin_validations(self, db_service: DatabaseService):
        """Test getting plugin validations."""
        await db_service.save_plugin_validation(
            plugin_path="/plugins/test/hooks.json",
            validation_type="hooks",
            status="pass",
        )
        await db_service.save_plugin_validation(
            plugin_path="/plugins/test/.mcp.json",
            validation_type="mcp",
            status="fail",
            error_message="Missing comma",
        )

        logs = await db_service.get_plugin_validations()
        assert len(logs) == 2

        hooks_logs = await db_service.get_plugin_validations(validation_type="hooks")
        assert len(hooks_logs) == 1
        assert hooks_logs[0].validation_type == "hooks"

    @pytest.mark.asyncio
    async def test_save_audit_log(self, db_service: DatabaseService):
        """Test saving audit log."""
        log = await db_service.save_audit_log(
            action="model_resolution",
            resource_type="bedrock_model",
            resource_id="claude-3-5-sonnet",
            user_id="user123",
            details="Resolved to au profile",
            ip_address="192.168.1.1",
        )
        assert log.id is not None
        assert log.action == "model_resolution"
        assert log.resource_id == "claude-3-5-sonnet"

    @pytest.mark.asyncio
    async def test_get_audit_logs(self, db_service: DatabaseService):
        """Test getting audit logs."""
        await db_service.save_audit_log(
            action="model_resolution",
            resource_type="bedrock_model",
        )
        await db_service.save_audit_log(
            action="plugin_validation",
            resource_type="hooks_json",
        )

        logs = await db_service.get_audit_logs()
        assert len(logs) == 2

        resolution_logs = await db_service.get_audit_logs(action="model_resolution")
        assert len(resolution_logs) == 1
        assert resolution_logs[0].action == "model_resolution"
