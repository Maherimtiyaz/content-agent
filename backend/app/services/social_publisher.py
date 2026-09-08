"""Social publisher interface and mock implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class PublishResult:
    """Result of a publish operation."""
    success: bool
    post_id: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[dict] = None


@dataclass
class PostContent:
    """Content to be published."""
    title: str
    content: str
    idempotency_key: str  # To prevent duplicate publishing


class SocialPublisher(ABC):
    """Interface for social media publishing."""
    
    @abstractmethod
    def publish(self, content: PostContent) -> PublishResult:
        """Publish a post to the social platform.
        
        Args:
            content: The content to publish
            
        Returns:
            PublishResult with success status and post ID
        """
        pass
    
    @abstractmethod
    def get_post(self, post_id: str) -> Optional[dict]:
        """Retrieve a published post by ID.
        
        Args:
            post_id: The platform-specific post ID
            
        Returns:
            Post data or None if not found
        """
        pass


class MockSocialPublisher(SocialPublisher):
    """Mock publisher for development and testing.
    
    Simulates publishing behavior without calling real APIs.
    Tracks published posts in memory for verification.
    """
    
    def __init__(self):
        self._published_posts: dict[str, dict] = {}
        self._publish_count = 0
    
    def publish(self, content: PostContent) -> PublishResult:
        """Simulate publishing a post.
        
        Uses idempotency key to prevent duplicate publishing.
        """
        # Check for duplicate via idempotency key
        for existing in self._published_posts.values():
            if existing.get('idempotency_key') == content.idempotency_key:
                return PublishResult(
                    success=False,
                    error_message=f"Duplicate publish attempt. Post already exists with ID: {existing['post_id']}"
                )
        
        # Simulate successful publish
        self._publish_count += 1
        post_id = f"mock_post_{self._publish_count}"
        
        post_data = {
            'post_id': post_id,
            'title': content.title,
            'content': content.content,
            'idempotency_key': content.idempotency_key,
            'published_at': datetime.utcnow().isoformat(),
            'platform': 'mock'
        }
        
        self._published_posts[post_id] = post_data
        
        return PublishResult(
            success=True,
            post_id=post_id,
            raw_response=post_data
        )
    
    def get_post(self, post_id: str) -> Optional[dict]:
        """Retrieve a mock published post."""
        return self._published_posts.get(post_id)
    
    def get_all_posts(self) -> list[dict]:
        """Get all published posts (for testing)."""
        return list(self._published_posts.values())
    
    def clear(self):
        """Clear all published posts (for testing)."""
        self._published_posts.clear()
        self._publish_count = 0
