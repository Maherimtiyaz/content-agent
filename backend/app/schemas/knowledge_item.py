"""Knowledge Item schemas."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.schemas.common import BaseSchema


class KnowledgeType(str, Enum):
    """Types of knowledge items."""
    PROJECT = "project"
    LESSON = "lesson"
    EXPERIENCE = "experience"
    TECHNICAL_NOTE = "technical_note"
    OPINION = "opinion"
    EXPERIMENT = "experiment"
    IDEA = "idea"


class KnowledgeItemBase(BaseSchema):
    """Base schema for knowledge item."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    knowledge_type: KnowledgeType
    tags: Optional[List[str]] = None


class KnowledgeItemCreate(KnowledgeItemBase):
    """Schema for creating a knowledge item."""
    user_id: int


class KnowledgeItemUpdate(BaseModel):
    """Schema for updating a knowledge item (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    knowledge_type: Optional[KnowledgeType] = None
    tags: Optional[List[str]] = None


class KnowledgeItemRead(KnowledgeItemBase):
    """Schema for reading a knowledge item."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, value):
        """Convert comma-separated string to list if needed."""
        if isinstance(value, str):
            return [tag.strip() for tag in value.split(',') if tag.strip()]
        return value
