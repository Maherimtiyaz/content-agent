"""Published Post model."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PublishedPost(Base):
    """Published post on X (Twitter)."""
    
    __tablename__ = "published_posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Reference to source draft
    content_draft_id: Mapped[int] = mapped_column(
        ForeignKey("content_drafts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # One published post per draft
    )
    
    # X/Twitter specific fields
    x_post_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    x_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Content snapshot at time of publishing
    published_content: Mapped[str] = mapped_column(Text, nullable=False)
    published_title: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Publication metadata
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships
    draft = relationship("ContentDraft", backref="published_post")
    
    def __repr__(self) -> str:
        return f"<PublishedPost(id={self.id}, x_post_id='{self.x_post_id}')>"
