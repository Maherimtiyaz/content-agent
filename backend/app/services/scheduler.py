"""Database-backed scheduler for scheduled posts.

This scheduler uses a simple polling mechanism to find and process
scheduled posts that are due for publication. It does not require
Redis, Celery, or any external queue system.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.scheduled_post import ScheduledPost, ScheduleStatus
from app.models.content_draft import ContentDraft, DraftState
from app.models.published_post import PublishedPost
from app.services.social_publisher import SocialPublisher, PostContent, PublishResult
from app.services.audit_service import AuditService, AuditAction


class SchedulerError(Exception):
    """Base exception for scheduler errors."""
    pass


class DuplicatePublishingError(SchedulerError):
    """Raised when a duplicate publish attempt is detected."""
    pass


class ApprovalRequiredError(SchedulerError):
    """Raised when attempting to publish unapproved content."""
    pass


class DatabaseScheduler:
    """Database-backed scheduler for scheduled posts.
    
    This scheduler:
    - Polls the database for pending scheduled posts
    - Enforces human approval requirement before publishing
    - Prevents duplicate publishing via idempotency keys
    - Supports retry logic with exponential backoff
    - Logs all actions for auditability
    """
    
    def __init__(
        self,
        db_session: Session,
        publisher: SocialPublisher,
        audit_service: AuditService,
    ):
        self.db = db_session
        self.publisher = publisher
        self.audit = audit_service
    
    def get_due_posts(self, now: Optional[datetime] = None) -> list[ScheduledPost]:
        """Get all scheduled posts that are due for publication.
        
        Args:
            now: Current time (defaults to utcnow)
            
        Returns:
            List of scheduled posts ready to be published
        """
        if now is None:
            now = datetime.utcnow()
        
        query = select(ScheduledPost).where(
            ScheduledPost.status == ScheduleStatus.PENDING,
            ScheduledPost.scheduled_at <= now,
        )
        
        results = self.db.execute(query).scalars().all()
        return list(results)
    
    def process_scheduled_post(self, scheduled_post: ScheduledPost) -> bool:
        """Process a single scheduled post for publication.
        
        Args:
            scheduled_post: The scheduled post to process
            
        Returns:
            True if successfully published, False otherwise
            
        Raises:
            ApprovalRequiredError: If the draft is not approved
            DuplicatePublishingError: If this is a duplicate publish attempt
        """
        # Mark as processing
        scheduled_post.status = ScheduleStatus.PROCESSING
        scheduled_post.retry_count += 1
        self.db.commit()
        
        # Get the associated draft
        draft = scheduled_post.draft
        if draft is None:
            scheduled_post.status = ScheduleStatus.FAILED
            scheduled_post.last_error = "Associated draft not found"
            self.db.commit()
            return False
        
        # CRITICAL: Verify human approval
        if draft.state != DraftState.APPROVED:
            error_msg = f"Cannot publish draft in state '{draft.state.value}'. Human approval required."
            scheduled_post.status = ScheduleStatus.FAILED
            scheduled_post.last_error = error_msg
            self.db.commit()
            
            self.audit.log_publish_attempt(
                draft_id=draft.id,
                scheduled_post_id=scheduled_post.id,
                success=False,
                error_message=error_msg,
            )
            
            raise ApprovalRequiredError(error_msg)
        
        # Prepare content for publishing
        post_content = PostContent(
            title=draft.title,
            content=draft.content,
            idempotency_key=scheduled_post.idempotency_key,
        )
        
        # Attempt to publish
        try:
            result = self.publisher.publish(post_content)
        except Exception as e:
            # Publisher error
            error_msg = f"Publisher error: {str(e)}"
            scheduled_post.last_error = error_msg
            scheduled_post.status = ScheduleStatus.FAILED
            
            # Check if retry is possible
            if scheduled_post.can_retry():
                scheduled_post.status = ScheduleStatus.PENDING
                scheduled_post.next_retry_at = self._calculate_next_retry(scheduled_post.retry_count)
            
            self.db.commit()
            
            self.audit.log_publish_attempt(
                draft_id=draft.id,
                scheduled_post_id=scheduled_post.id,
                success=False,
                error_message=error_msg,
            )
            
            return False
        
        if not result.success:
            # Publishing failed (e.g., duplicate detection)
            error_msg = result.error_message or "Unknown publishing error"
            scheduled_post.last_error = error_msg
            scheduled_post.status = ScheduleStatus.FAILED
            
            # Check if it's a duplicate - don't retry duplicates
            if "Duplicate" not in error_msg and scheduled_post.can_retry():
                scheduled_post.status = ScheduleStatus.PENDING
                scheduled_post.next_retry_at = self._calculate_next_retry(scheduled_post.retry_count)
            
            self.db.commit()
            
            self.audit.log_publish_attempt(
                draft_id=draft.id,
                scheduled_post_id=scheduled_post.id,
                success=False,
                error_message=error_msg,
            )
            
            if "Duplicate" in error_msg:
                raise DuplicatePublishingError(error_msg)
            
            return False
        
        # Success! Create published post record
        published_post = PublishedPost(
            content_draft_id=draft.id,
            x_post_id=result.post_id,
            published_title=draft.title,
            published_content=draft.content,
            published_at=datetime.utcnow(),
        )
        self.db.add(published_post)
        self.db.flush()  # Get the ID
        
        # Update scheduled post
        scheduled_post.published_post_id = published_post.id
        scheduled_post.status = ScheduleStatus.PUBLISHED
        scheduled_post.processed_at = datetime.utcnow()
        
        # Update draft state to PUBLISHED
        draft.state = DraftState.PUBLISHED
        
        self.db.commit()
        
        # Log successful publish
        self.audit.log_publish_attempt(
            draft_id=draft.id,
            scheduled_post_id=scheduled_post.id,
            success=True,
            x_post_id=result.post_id,
        )
        
        return True
    
    def run_scheduler_cycle(self) -> dict:
        """Run one cycle of the scheduler.
        
        Processes all due scheduled posts and returns statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        now = datetime.utcnow()
        due_posts = self.get_due_posts(now)
        
        stats = {
            "total_due": len(due_posts),
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
        }
        
        for scheduled_post in due_posts:
            try:
                if self.process_scheduled_post(scheduled_post):
                    stats["successful"] += 1
                else:
                    stats["failed"] += 1
            except ApprovalRequiredError as e:
                stats["failed"] += 1
                stats["errors"].append(f"Draft {scheduled_post.content_draft_id}: {str(e)}")
            except DuplicatePublishingError as e:
                stats["skipped"] += 1
                stats["errors"].append(f"Draft {scheduled_post.content_draft_id}: Duplicate - {str(e)}")
            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append(f"Draft {scheduled_post.content_draft_id}: Unexpected error - {str(e)}")
        
        # Log the scheduler run
        self.audit.log_scheduler_run(
            processed_count=stats["total_due"],
            error_count=stats["failed"],
            errors=stats["errors"] if stats["errors"] else None,
        )
        
        return stats
    
    def _calculate_next_retry(self, retry_count: int) -> datetime:
        """Calculate next retry time with exponential backoff.
        
        Args:
            retry_count: Current retry count
            
        Returns:
            Datetime for next retry attempt
        """
        # Exponential backoff: 1min, 5min, 15min, then give up
        delays = [1, 5, 15]
        delay_minutes = delays[min(retry_count - 1, len(delays) - 1)]
        return datetime.utcnow() + timedelta(minutes=delay_minutes)
    
    def cancel_scheduled_post(self, scheduled_post_id: int) -> bool:
        """Cancel a scheduled post.
        
        Args:
            scheduled_post_id: ID of the scheduled post to cancel
            
        Returns:
            True if cancelled, False if not found or already processed
        """
        scheduled_post = self.db.get(ScheduledPost, scheduled_post_id)
        if scheduled_post is None:
            return False
        
        if scheduled_post.status not in [ScheduleStatus.PENDING, ScheduleStatus.PROCESSING]:
            return False
        
        scheduled_post.status = ScheduleStatus.CANCELLED
        self.db.commit()
        
        self.audit.log(
            action=AuditAction.POST_CANCELLED,
            entity_type="scheduled_post",
            entity_id=scheduled_post_id,
            description=f"Scheduled post cancelled",
        )
        
        return True
