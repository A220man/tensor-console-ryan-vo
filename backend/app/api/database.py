"""Database API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.database_service import DatabaseService
from app.models.database import ResolutionHistory, PluginValidationLog, AuditLog

router = APIRouter(prefix="/database", tags=["database"])


@router.on_event("startup")
async def startup_db():
    """Initialize database on startup."""
    from app.core.database import init_db
    await init_db()


@router.post("/resolution-history", response_model=dict)
async def save_resolution_history(
    region: str,
    requested_model: str,
    resolved_model: str,
    is_inference_profile: bool,
    prefix_used: str,
    db: AsyncSession = Depends(get_db),
):
    """Save a model resolution to history."""
    service = DatabaseService(db)
    history = await service.save_resolution(
        region=region,
        requested_model=requested_model,
        resolved_model=resolved_model,
        is_inference_profile=is_inference_profile,
        prefix_used=prefix_used,
    )
    return history.to_dict()


@router.get("/resolution-history", response_model=list[dict])
async def get_resolution_history(
    region: Optional[str] = Query(None, description="Filter by region"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get resolution history with optional region filter."""
    service = DatabaseService(db)
    history = await service.get_resolution_history(region=region, limit=limit, offset=offset)
    return [h.to_dict() for h in history]


@router.get("/resolution-history/count", response_model=int)
async def get_resolution_count(
    region: Optional[str] = Query(None, description="Filter by region"),
    db: AsyncSession = Depends(get_db),
):
    """Get total count of resolution history."""
    service = DatabaseService(db)
    return await service.get_resolution_count(region=region)


@router.post("/plugin-validation", response_model=dict)
async def save_plugin_validation(
    plugin_path: str,
    validation_type: str,
    status: str,
    error_message: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Save plugin validation result."""
    service = DatabaseService(db)
    log = await service.save_plugin_validation(
        plugin_path=plugin_path,
        validation_type=validation_type,
        status=status,
        error_message=error_message,
    )
    return log.to_dict()


@router.get("/plugin-validation", response_model=list[dict])
async def get_plugin_validations(
    validation_type: Optional[str] = Query(None, description="Filter by validation type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get plugin validation logs."""
    service = DatabaseService(db)
    logs = await service.get_plugin_validations(validation_type=validation_type, limit=limit, offset=offset)
    return [log.to_dict() for log in logs]


@router.post("/audit-log", response_model=dict)
async def save_audit_log(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Save audit log entry."""
    service = DatabaseService(db)
    log = await service.save_audit_log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details,
        ip_address=ip_address,
    )
    return log.to_dict()


@router.get("/audit-log", response_model=list[dict])
async def get_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs with optional filters."""
    service = DatabaseService(db)
    logs = await service.get_audit_logs(action=action, resource_type=resource_type, limit=limit, offset=offset)
    return [log.to_dict() for log in logs]
