"""API routes for content drafts and quality checks."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.content_draft import (
    ContentDraftCreate,
    ContentDraftUpdate,
    ContentDraft,
    ContentDraftWithDetails,
    ContentDraftStateTransition,
    ContentDraftApproval,
    ContentDraftRejection,
    QualityCheckCreate,
    QualityCheck,
)
from app.services.content_draft import ContentDraftService, QualityCheckService
from app.models.content_draft import DraftState

router = APIRouter(prefix="/content-drafts", tags=["Content Drafts"])


@router.post("/", response_model=ContentDraft, status_code=status.HTTP_201_CREATED)
def create_draft(
    draft_data: ContentDraftCreate,
    db: Session = Depends(get_db),
):
    """Create a new content draft."""
    return ContentDraftService.create_draft(
        db=db,
        title=draft_data.title,
        content=draft_data.content,
        format=draft_data.format,
        content_idea_id=draft_data.content_idea_id,
        content_pillar=draft_data.content_pillar,
        tags=draft_data.tags,
    )


@router.get("/{draft_id}", response_model=ContentDraftWithDetails)
def get_draft(draft_id: int, db: Session = Depends(get_db)):
    """Get a content draft by ID with quality checks."""
    draft = ContentDraftService.get_draft(db, draft_id)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft with id {draft_id} not found",
        )
    return draft


@router.get("/", response_model=List[ContentDraft])
def list_drafts(
    state: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List content drafts with optional state filter."""
    state_enum = None
    if state:
        try:
            state_enum = DraftState(state)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid state: {state}. Valid states: {[s.value for s in DraftState]}",
            )
    
    return ContentDraftService.list_drafts(
        db=db,
        state=state_enum,
        limit=limit,
        offset=offset,
    )


@router.put("/{draft_id}", response_model=ContentDraft)
def update_draft(
    draft_id: int,
    draft_data: ContentDraftUpdate,
    db: Session = Depends(get_db),
):
    """Update a content draft's content fields."""
    draft = ContentDraftService.update_draft(
        db=db,
        draft_id=draft_id,
        title=draft_data.title,
        content=draft_data.content,
        format=draft_data.format,
        content_pillar=draft_data.content_pillar,
        tags=draft_data.tags,
    )
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Draft with id {draft_id} not found",
        )
    return draft


@router.post("/{draft_id}/transition", response_model=ContentDraft)
def transition_state(
    draft_id: int,
    transition_data: ContentDraftStateTransition,
    db: Session = Depends(get_db),
):
    """Transition a draft to a new state."""
    try:
        draft = ContentDraftService.transition_state(
            db=db,
            draft_id=draft_id,
            new_state=transition_data.new_state,
            user_id=None,  # Will require auth in production
            rejection_reason=transition_data.rejection_reason,
        )
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Draft with id {draft_id} not found",
            )
        return draft
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{draft_id}/approve", response_model=ContentDraft)
def approve_draft(
    draft_id: int,
    approval_data: ContentDraftApproval,
    db: Session = Depends(get_db),
):
    """Approve a content draft for publishing."""
    try:
        draft = ContentDraftService.transition_state(
            db=db,
            draft_id=draft_id,
            new_state=DraftState.APPROVED,
            user_id=approval_data.user_id,
        )
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Draft with id {draft_id} not found",
            )
        return draft
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{draft_id}/reject", response_model=ContentDraft)
def reject_draft(
    draft_id: int,
    rejection_data: ContentDraftRejection,
    db: Session = Depends(get_db),
):
    """Reject a content draft."""
    try:
        draft = ContentDraftService.transition_state(
            db=db,
            draft_id=draft_id,
            new_state=DraftState.REJECTED,
            user_id=rejection_data.user_id,
            rejection_reason=rejection_data.reason,
        )
        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Draft with id {draft_id} not found",
            )
        return draft
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{draft_id}/can-publish")
def check_can_publish(draft_id: int, db: Session = Depends(get_db)):
    """Check if a draft can be published (is in APPROVED state)."""
    can_publish = ContentDraftService.can_publish(db, draft_id)
    return {"draft_id": draft_id, "can_publish": can_publish}


# Quality Check endpoints
quality_router = APIRouter(prefix="/quality-checks", tags=["Quality Checks"])


@router.post("/quality-checks", response_model=QualityCheck, status_code=status.HTTP_201_CREATED)
def create_quality_check(
    qc_data: QualityCheckCreate,
    db: Session = Depends(get_db),
):
    """Create a quality check for a draft."""
    return QualityCheckService.create_quality_check(
        db=db,
        draft_id=qc_data.draft_id,
        passed=qc_data.passed,
        warnings=qc_data.warnings,
        errors=qc_data.errors,
        suggested_changes=qc_data.suggested_changes,
        checks=qc_data.checks,
    )


@router.get("/drafts/{draft_id}/quality-checks", response_model=List[QualityCheck])
def get_quality_checks(draft_id: int, db: Session = Depends(get_db)):
    """Get all quality checks for a draft."""
    return QualityCheckService.get_quality_checks(db, draft_id)


@router.get("/drafts/{draft_id}/quality-checks/latest", response_model=QualityCheck)
def get_latest_quality_check(draft_id: int, db: Session = Depends(get_db)):
    """Get the most recent quality check for a draft."""
    qc = QualityCheckService.get_latest_quality_check(db, draft_id)
    if not qc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quality checks found for draft {draft_id}",
        )
    return qc
