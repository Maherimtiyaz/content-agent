"""Scheduled Post model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class ScheduleStatus(str, enum.Enum):
    """Scheduled post status."""
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledPost(Base):
    """Scheduled post awaiting publication."""
    
    __tablename__ = "scheduled_posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Reference to approved draft
    content_draft_id: Mapped[int] = mapped_column(
        ForeignKey("content_drafts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # One schedule per draft
    )
    
    # Scheduling
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[ScheduleStatus] = mapped_column(
        SQLEnum(ScheduleStatus),
        default=ScheduleStatus.PENDING,
        nullable=False
    )
    
    # Publication tracking
    published_post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("published_posts.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Error handling
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(default=3, nullable=False)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Idempotency key to prevent duplicate publishing
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    draft = relationship("ContentDraft", backref="scheduled_post")
    published_post = relationship("PublishedPost", backref="scheduled_post")
    
    def can_retry(self) -> bool:
        """Check if this scheduled post can be retried."""
        return self.retry_count < self.max_retries
    
    def __repr__(self) -> str:
        return f"<ScheduledPost(id={self.id}, draft_id={self.content_draft_id}, status={self.status.value})>"
