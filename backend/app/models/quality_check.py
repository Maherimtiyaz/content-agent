"""Quality Check model for content validation."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QualityCheck(Base):
    """Quality check results for content drafts."""
    
    __tablename__ = "quality_checks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Reference to draft
    draft_id: Mapped[int] = mapped_column(
        ForeignKey("content_drafts.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Check results
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    # Structured results
    warnings: Mapped[List[str]] = mapped_column(JSON, default=list)
    errors: Mapped[List[str]] = mapped_column(JSON, default=list)
    suggested_changes: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Detailed checks (stored as JSON for flexibility)
    checks: Mapped[dict] = mapped_column(JSON, default=dict)
    # Example structure:
    # {
    #     "factual_consistency": {"passed": true, "details": "..."},
    #     "unsupported_claims": {"passed": false, "details": "..."},
    #     "hallucinated_experiences": {"passed": true, "details": "..."},
    #     ...
    # }
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    # Relationship
    draft = relationship("ContentDraft", back_populates="quality_checks")
    
    def __repr__(self) -> str:
        return f"<QualityCheck(id={self.id}, draft_id={self.draft_id}, passed={self.passed})>"
