"""Database service for persistence operations."""

from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import ResolutionHistory, PluginValidationLog, AuditLog


class DatabaseService:
    """Service for database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Resolution History
    async def save_resolution(
        self,
        region: str,
        requested_model: str,
        resolved_model: str,
        is_inference_profile: bool,
        prefix_used: str,
    ) -> ResolutionHistory:
        """Save a model resolution to history."""
        history = ResolutionHistory(
            region=region,
            requested_model=requested_model,
            resolved_model=resolved_model,
            is_inference_profile=1 if is_inference_profile else 0,
            prefix_used=prefix_used,
        )
        self.session.add(history)
        await self.session.flush()
        return history

    async def get_resolution_history(
        self,
        region: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ResolutionHistory]:
        """Get resolution history with optional region filter."""
        query = select(ResolutionHistory).order_by(desc(ResolutionHistory.created_at))
        if region:
            query = query.where(ResolutionHistory.region == region)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_resolution_count(self, region: Optional[str] = None) -> int:
        """Get total count of resolution history."""
        from sqlalchemy import func
        query = select(func.count(ResolutionHistory.id))
        if region:
            query = query.where(ResolutionHistory.region == region)
        result = await self.session.execute(query)
        return result.scalar() or 0

    # Plugin Validation Log
    async def save_plugin_validation(
        self,
        plugin_path: str,
        validation_type: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> PluginValidationLog:
        """Save plugin validation result."""
        log = PluginValidationLog(
            plugin_path=plugin_path,
            validation_type=validation_type,
            status=status,
            error_message=error_message,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_plugin_validations(
        self,
        validation_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PluginValidationLog]:
        """Get plugin validation logs."""
        query = select(PluginValidationLog).order_by(desc(PluginValidationLog.created_at))
        if validation_type:
            query = query.where(PluginValidationLog.validation_type == validation_type)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # Audit Log
    async def save_audit_log(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Save audit log entry."""
        log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_audit_logs(
        self,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditLog]:
        """Get audit logs with optional filters."""
        query = select(AuditLog).order_by(desc(AuditLog.created_at))
        if action:
            query = query.where(AuditLog.action == action)
        if resource_type:
            query = query.where(AuditLog.resource_type == resource_type)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
