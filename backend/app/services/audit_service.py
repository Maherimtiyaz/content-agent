"""Audit service for logging important actions."""

from datetime import datetime
from typing import Optional, Any
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog, AuditAction


class AuditService:
    """Service for recording audit log entries.
    
    All critical system actions should be logged through this service
    for traceability and debugging.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[int] = None,
        description: str = "",
        user_id: Optional[int] = None,
        metadata: Optional[dict] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """Record an audit log entry.
        
        Args:
            action: The type of action being logged
            entity_type: Type of entity involved (e.g., 'content_draft', 'scheduled_post')
            entity_id: ID of the entity if applicable
            description: Human-readable description of the action
            user_id: ID of the user performing the action if applicable
            metadata: Additional structured data about the action
            success: Whether the action succeeded
            error_message: Error message if the action failed
            
        Returns:
            The created AuditLog entry
        """
        entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            user_id=user_id,
            action_metadata=metadata,
            success=success,
            error_message=error_message,
        )
        
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    def log_content_state_change(
        self,
        draft_id: int,
        old_state: str,
        new_state: str,
        user_id: Optional[int] = None,
    ) -> AuditLog:
        """Log a content draft state transition."""
        return self.log(
            action=AuditAction.STATE_TRANSITION,
            entity_type="content_draft",
            entity_id=draft_id,
            description=f"State changed from '{old_state}' to '{new_state}'",
            user_id=user_id,
            metadata={"old_state": old_state, "new_state": new_state},
        )
    
    def log_publish_attempt(
        self,
        draft_id: int,
        scheduled_post_id: int,
        success: bool,
        error_message: Optional[str] = None,
        x_post_id: Optional[str] = None,
    ) -> AuditLog:
        """Log a publish attempt."""
        action = AuditAction.PUBLISH_SUCCESS if success else AuditAction.PUBLISH_FAILURE
        
        return self.log(
            action=action,
            entity_type="content_draft",
            entity_id=draft_id,
            description=f"Publish {'succeeded' if success else 'failed'}" + 
                       (f" with X post ID: {x_post_id}" if x_post_id else ""),
            success=success,
            error_message=error_message,
            metadata={
                "scheduled_post_id": scheduled_post_id,
                "x_post_id": x_post_id,
            },
        )
    
    def log_scheduler_run(
        self,
        processed_count: int,
        error_count: int = 0,
        errors: Optional[list[str]] = None,
    ) -> AuditLog:
        """Log a scheduler execution run."""
        return self.log(
            action=AuditAction.SCHEDULER_RUN,
            entity_type="scheduler",
            description=f"Scheduler run completed: {processed_count} processed, {error_count} errors",
            success=error_count == 0,
            error_message="\n".join(errors) if errors else None,
            metadata={
                "processed_count": processed_count,
                "error_count": error_count,
            },
        )
