"""Pydantic schemas for content drafts and quality checks."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class DraftStateEnum(str, Enum):
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


# Quality Check Schemas
class QualityCheckBase(BaseModel):
    """Base schema for quality check."""
    passed: bool
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    suggested_changes: List[str] = Field(default_factory=list)
    checks: dict = Field(default_factory=dict)


class QualityCheckCreate(QualityCheckBase):
    """Schema for creating a quality check."""
    draft_id: int


class QualityCheck(QualityCheckBase):
    """Schema for quality check response."""
    id: int
    draft_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Content Draft Schemas
class ContentDraftBase(BaseModel):
    """Base schema for content draft."""
    title: str = Field(..., min_length=1, max_length=500)
    content: str
    format: str = Field(..., min_length=1, max_length=100)
    content_pillar: Optional[str] = Field(None, max_length=200)
    tags: List[str] = Field(default_factory=list)


class ContentDraftCreate(ContentDraftBase):
    """Schema for creating a content draft."""
    content_idea_id: Optional[int] = None
    state: DraftStateEnum = DraftStateEnum.DRAFT


class ContentDraftUpdate(BaseModel):
    """Schema for updating a content draft."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    format: Optional[str] = Field(None, min_length=1, max_length=100)
    content_pillar: Optional[str] = Field(None, max_length=200)
    tags: Optional[List[str]] = None
    state: Optional[DraftStateEnum] = None


class ContentDraftStateTransition(BaseModel):
    """Schema for state transition request."""
    new_state: DraftStateEnum
    rejection_reason: Optional[str] = None  # Only used when transitioning to REJECTED


class ContentDraftApproval(BaseModel):
    """Schema for approving a content draft."""
    user_id: int


class ContentDraftRejection(BaseModel):
    """Schema for rejecting a content draft."""
    user_id: int
    reason: str


class ContentDraft(ContentDraftBase):
    """Schema for content draft response."""
    id: int
    state: DraftStateEnum
    content_idea_id: Optional[int] = None
    quality_check_passed: bool
    quality_check_run_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ContentDraftWithDetails(ContentDraft):
    """Schema for content draft with related data."""
    quality_checks: List[QualityCheck] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
