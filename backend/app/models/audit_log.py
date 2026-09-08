"""Audit Log model for tracking important actions."""

from datetime import datetime
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class AuditAction(str, enum.Enum):
    """Types of auditable actions."""
    # Content workflow
    DRAFT_CREATED = "draft_created"
    DRAFT_UPDATED = "draft_updated"
    STATE_TRANSITION = "state_transition"
    QUALITY_CHECK_RUN = "quality_check_run"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    
    # Scheduling & Publishing
    POST_SCHEDULED = "post_scheduled"
    POST_CANCELLED = "post_cancelled"
    PUBLISH_ATTEMPT = "publish_attempt"
    PUBLISH_SUCCESS = "publish_success"
    PUBLISH_FAILURE = "publish_failure"
    
    # Data management
    KNOWLEDGE_CREATED = "knowledge_created"
    KNOWLEDGE_UPDATED = "knowledge_updated"
    KNOWLEDGE_DELETED = "knowledge_deleted"
    BRAND_PROFILE_UPDATED = "brand_profile_updated"
    
    # System
    SCHEDULER_RUN = "scheduler_run"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"


class AuditLog(Base):
    """Audit log entry for tracking important system actions."""
    
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Action details
    action: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # User context (if applicable)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Outcome
    success: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    # Relationships
    user = relationship("User", backref="audit_logs")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action.value}, entity={self.entity_type}:{self.entity_id})>"
