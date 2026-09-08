"""Content Draft model with state machine."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class DraftState(str, enum.Enum):
    """Content draft state machine states."""
    IDEA = "idea"
    DRAFT = "draft"
    QUALITY_CHECKED = "quality_checked"
    REVIEW = "review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ContentDraft(Base):
    """Content draft with state machine for approval workflow."""
    
    __tablename__ = "content_drafts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Content fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(String(100), nullable=False)  # short_post, thread, etc.
    
    # State machine
    state: Mapped[DraftState] = mapped_column(
        SQLEnum(DraftState), 
        default=DraftState.DRAFT, 
        nullable=False
    )
    
    # References to source material (provenance)
    content_idea_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("content_ideas.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Metadata
    content_pillar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    
    # Quality check status
    quality_check_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    quality_check_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Approval workflow
    approved_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejected_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True
    )
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    content_idea = relationship("ContentIdea", back_populates="drafts")
    approver = relationship("User", foreign_keys=[approved_by])
    rejector = relationship("User", foreign_keys=[rejected_by])
    quality_checks = relationship("QualityCheck", back_populates="draft", cascade="all, delete-orphan")
    
    def can_transition_to(self, new_state: DraftState) -> bool:
        """Check if state transition is valid."""
        valid_transitions = {
            DraftState.IDEA: [DraftState.DRAFT, DraftState.ARCHIVED],
            DraftState.DRAFT: [DraftState.QUALITY_CHECKED, DraftState.ARCHIVED],
            DraftState.QUALITY_CHECKED: [DraftState.REVIEW, DraftState.DRAFT, DraftState.ARCHIVED],
            DraftState.REVIEW: [DraftState.APPROVED, DraftState.REJECTED, DraftState.DRAFT],
            DraftState.APPROVED: [DraftState.SCHEDULED, DraftState.DRAFT],
            DraftState.SCHEDULED: [DraftState.PUBLISHED, DraftState.DRAFT],
            DraftState.PUBLISHED: [],  # Terminal state
            DraftState.REJECTED: [DraftState.DRAFT, DraftState.ARCHIVED],
            DraftState.ARCHIVED: [],  # Terminal state
        }
        return new_state in valid_transitions.get(self.state, [])
    
    def __repr__(self) -> str:
        return f"<ContentDraft(id={self.id}, title='{self.title}', state={self.state.value})>"
