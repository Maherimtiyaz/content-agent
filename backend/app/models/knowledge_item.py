"""Knowledge Item model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from datetime import datetime
import enum

from app.db.base import Base


class KnowledgeType(str, enum.Enum):
    """Types of knowledge items."""
    PROJECT = "project"
    LESSON = "lesson"
    EXPERIENCE = "experience"
    TECHNICAL_NOTE = "technical_note"
    OPINION = "opinion"
    EXPERIMENT = "experiment"
    IDEA = "idea"


class KnowledgeItem(Base):
    """Knowledge item containing user's personal engineering knowledge.
    
    This is manually added content that forms the basis for content generation.
    """
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Markdown/text content
    
    knowledge_type = Column(SQLEnum(KnowledgeType), nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated tags for simplicity
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def get_tags_list(self) -> list[str]:
        """Return tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    def set_tags_list(self, tags: list[str]) -> None:
        """Set tags from a list."""
        self.tags = ", ".join(tags) if tags else ""
