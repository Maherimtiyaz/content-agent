"""Content Draft service for managing drafts and quality checks."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.models.content_draft import ContentDraft, DraftState
from app.models.quality_check import QualityCheck


class ContentDraftService:
    """Service for managing content drafts."""
    
    @staticmethod
    def create_draft(
        db: Session,
        title: str,
        content: str,
        format: str,
        content_idea_id: Optional[int] = None,
        content_pillar: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> ContentDraft:
        """Create a new content draft."""
        draft = ContentDraft(
            title=title,
            content=content,
            format=format,
            content_idea_id=content_idea_id,
            content_pillar=content_pillar,
            tags=tags or [],
            state=DraftState.DRAFT,
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)
        return draft
    
    @staticmethod
    def get_draft(db: Session, draft_id: int) -> Optional[ContentDraft]:
        """Get a draft by ID with related quality checks."""
        return (
            db.query(ContentDraft)
            .options(
                joinedload(ContentDraft.quality_checks),
                joinedload(ContentDraft.content_idea),
            )
            .filter(ContentDraft.id == draft_id)
            .first()
        )
    
    @staticmethod
    def list_drafts(
        db: Session,
        state: Optional[DraftState] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ContentDraft]:
        """List drafts with optional state filter."""
        query = db.query(ContentDraft).options(
            joinedload(ContentDraft.quality_checks)
        )
        
        if state:
            query = query.filter(ContentDraft.state == state)
        
        return query.order_by(ContentDraft.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def update_draft(
        db: Session,
        draft_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        format: Optional[str] = None,
        content_pillar: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Optional[ContentDraft]:
        """Update a draft's content fields."""
        draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
        if not draft:
            return None
        
        if title is not None:
            draft.title = title
        if content is not None:
            draft.content = content
        if format is not None:
            draft.format = format
        if content_pillar is not None:
            draft.content_pillar = content_pillar
        if tags is not None:
            draft.tags = tags
        
        draft.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(draft)
        return draft
    
    @staticmethod
    def transition_state(
        db: Session,
        draft_id: int,
        new_state: DraftState,
        user_id: Optional[int] = None,
        rejection_reason: Optional[str] = None,
    ) -> Optional[ContentDraft]:
        """Transition a draft to a new state."""
        draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
        if not draft:
            return None
        
        # Validate state transition
        if not draft.can_transition_to(new_state):
            raise ValueError(
                f"Invalid state transition from {draft.state.value} to {new_state.value}"
            )
        
        # Handle approval
        if new_state == DraftState.APPROVED:
            if user_id is None:
                raise ValueError("user_id required for approval")
            draft.approved_by = user_id
            draft.approved_at = datetime.utcnow()
            draft.rejection_reason = None
        
        # Handle rejection
        elif new_state == DraftState.REJECTED:
            if user_id is None:
                raise ValueError("user_id required for rejection")
            draft.rejected_by = user_id
            draft.rejected_at = datetime.utcnow()
            draft.rejection_reason = rejection_reason or "No reason provided"
        
        # Clear approval/rejection when going back to draft
        elif new_state == DraftState.DRAFT:
            draft.approved_by = None
            draft.approved_at = None
            draft.rejected_by = None
            draft.rejected_at = None
            draft.rejection_reason = None
        
        draft.state = new_state
        draft.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(draft)
        return draft
    
    @staticmethod
    def can_publish(db: Session, draft_id: int) -> bool:
        """Check if a draft can be published (must be in APPROVED state)."""
        draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
        if not draft:
            return False
        return draft.state == DraftState.APPROVED


class QualityCheckService:
    """Service for managing quality checks."""
    
    @staticmethod
    def create_quality_check(
        db: Session,
        draft_id: int,
        passed: bool,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        suggested_changes: Optional[List[str]] = None,
        checks: Optional[dict] = None,
    ) -> QualityCheck:
        """Create a quality check for a draft."""
        qc = QualityCheck(
            draft_id=draft_id,
            passed=passed,
            warnings=warnings or [],
            errors=errors or [],
            suggested_changes=suggested_changes or [],
            checks=checks or {},
        )
        db.add(qc)
        
        # Update draft's quality check status
        draft = db.query(ContentDraft).filter(ContentDraft.id == draft_id).first()
        if draft:
            draft.quality_check_passed = passed
            draft.quality_check_run_at = datetime.utcnow()
        
        db.commit()
        db.refresh(qc)
        return qc
    
    @staticmethod
    def get_quality_checks(db: Session, draft_id: int) -> List[QualityCheck]:
        """Get all quality checks for a draft."""
        return (
            db.query(QualityCheck)
            .filter(QualityCheck.draft_id == draft_id)
            .order_by(QualityCheck.created_at.desc())
            .all()
        )
    
    @staticmethod
    def get_latest_quality_check(
        db: Session, 
        draft_id: int
    ) -> Optional[QualityCheck]:
        """Get the most recent quality check for a draft."""
        return (
            db.query(QualityCheck)
            .filter(QualityCheck.draft_id == draft_id)
            .order_by(QualityCheck.created_at.desc())
            .first()
        )
