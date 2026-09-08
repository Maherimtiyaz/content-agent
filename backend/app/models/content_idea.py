"""Content Idea model for generating content drafts."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ContentIdea(Base):
    """Content idea generated from brand profile, knowledge, and research."""
    
    __tablename__ = "content_ideas"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Idea content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Classification
    content_pillar: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    suggested_format: Mapped[str] = mapped_column(String(100), nullable=False)  # short_post, thread, etc.
    
    # Confidence score (0.0 to 1.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    
    # Status
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    # Relationships - drafts generated from this idea
    drafts = relationship("ContentDraft", back_populates="content_idea")
    
    def __repr__(self) -> str:
        return f"<ContentIdea(id={self.id}, title='{self.title}')>"
