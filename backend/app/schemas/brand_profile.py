"""Brand Profile schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.schemas.common import BaseSchema


# Content Pillar Schemas
class ContentPillarBase(BaseSchema):
    """Base schema for content pillar."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ContentPillarCreate(ContentPillarBase):
    """Schema for creating a content pillar."""
    pass


class ContentPillarUpdate(BaseModel):
    """Schema for updating a content pillar (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class ContentPillarRead(ContentPillarBase):
    """Schema for reading a content pillar."""
    id: int
    brand_profile_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Brand Profile Schemas
class BrandProfileBase(BaseSchema):
    """Base schema for brand profile."""
    name: str = Field(..., min_length=1, max_length=255)
    professional_description: Optional[str] = None
    experience: Optional[str] = None
    technical_interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    target_audience: Optional[str] = None
    writing_style: Optional[str] = None
    tone: Optional[str] = Field(None, max_length=100)
    opinions: Optional[str] = None
    topics_to_avoid: Optional[str] = None
    example_posts: Optional[List[str]] = None
    personal_goals: Optional[str] = None


class BrandProfileCreate(BrandProfileBase):
    """Schema for creating a brand profile."""
    user_id: int
    content_pillars: Optional[List[ContentPillarCreate]] = None


class BrandProfileUpdate(BaseModel):
    """Schema for updating a brand profile (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    professional_description: Optional[str] = None
    experience: Optional[str] = None
    technical_interests: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    target_audience: Optional[str] = None
    writing_style: Optional[str] = None
    tone: Optional[str] = Field(None, max_length=100)
    opinions: Optional[str] = None
    topics_to_avoid: Optional[str] = None
    example_posts: Optional[List[str]] = None
    personal_goals: Optional[str] = None


class BrandProfileRead(BrandProfileBase):
    """Schema for reading a brand profile."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    content_pillars: List[ContentPillarRead] = []

    class Config:
        from_attributes = True
