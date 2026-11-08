"""Database models for persistence layer."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ResolutionHistory(Base):
    __tablename__ = "resolution_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region = Column(String(64), nullable=False, index=True)
    requested_model = Column(String(256), nullable=False)
    resolved_model = Column(String(256), nullable=False)
    is_inference_profile = Column(Integer, nullable=False)
    prefix_used = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        Index("ix_resolution_history_region_created", "region", "created_at"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "region": self.region,
            "requested_model": self.requested_model,
            "resolved_model": self.resolved_model,
            "is_inference_profile": bool(self.is_inference_profile),
            "prefix_used": self.prefix_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PluginValidationLog(Base):
    __tablename__ = "plugin_validation_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plugin_path = Column(String(512), nullable=False, index=True)
    validation_type = Column(String(32), nullable=False)
    status = Column(String(16), nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "plugin_path": self.plugin_path,
            "validation_type": self.validation_type,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(256), nullable=True)
    user_id = Column(String(256), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
