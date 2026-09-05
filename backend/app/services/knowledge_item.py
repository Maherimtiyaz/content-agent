"""Knowledge Item service."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.knowledge_item import KnowledgeItem, KnowledgeType
from app.schemas.knowledge_item import (
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemRead,
)


class KnowledgeItemService:
    """Service for knowledge item business logic."""
    
    model = KnowledgeItem
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, item_in: KnowledgeItemCreate) -> KnowledgeItemRead:
        """Create a new knowledge item.
        
        Args:
            item_in: Knowledge item data
            
        Returns:
            Created knowledge item
        """
        # Convert tags list to comma-separated string
        item_data = item_in.model_dump()
        if item_data.get('tags'):
            item_data['tags'] = ", ".join(item_data['tags'])
        
        db_item = KnowledgeItem(**item_data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        
        return KnowledgeItemRead.model_validate(db_item)
    
    def get(self, item_id: int) -> Optional[KnowledgeItemRead]:
        """Get a knowledge item by ID.
        
        Args:
            item_id: Knowledge item ID
            
        Returns:
            Knowledge item or None
        """
        item = self.db.query(KnowledgeItem).filter(
            KnowledgeItem.id == item_id
        ).first()
        
        if not item:
            return None
        
        return KnowledgeItemRead.model_validate(item)
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        knowledge_type: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[KnowledgeItemRead]:
        """List knowledge items with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Filter by user ID
            knowledge_type: Filter by knowledge type
            tag: Filter by tag
            
        Returns:
            List of knowledge items
        """
        query = self.db.query(KnowledgeItem)
        
        if user_id is not None:
            query = query.filter(KnowledgeItem.user_id == user_id)
        
        if knowledge_type is not None:
            try:
                kt = KnowledgeType(knowledge_type)
                query = query.filter(KnowledgeItem.knowledge_type == kt)
            except ValueError:
                pass  # Invalid knowledge type, ignore filter
        
        if tag is not None:
            # Search for tag in comma-separated list
            query = query.filter(
                KnowledgeItem.tags.ilike(f"%{tag}%")
            )
        
        items = query.offset(skip).limit(limit).all()
        return [KnowledgeItemRead.model_validate(i) for i in items]
    
    def update(
        self,
        item_id: int,
        item_in: KnowledgeItemUpdate,
    ) -> Optional[KnowledgeItemRead]:
        """Update a knowledge item.
        
        Args:
            item_id: Knowledge item ID
            item_in: Updated knowledge item data
            
        Returns:
            Updated knowledge item or None
        """
        item = self.db.query(KnowledgeItem).filter(
            KnowledgeItem.id == item_id
        ).first()
        
        if not item:
            return None
        
        # Update fields
        update_data = item_in.model_dump(exclude_unset=True)
        
        # Convert tags list to comma-separated string if provided
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = ", ".join(update_data['tags'])
        
        for field, value in update_data.items():
            setattr(item, field, value)
        
        self.db.commit()
        self.db.refresh(item)
        
        return KnowledgeItemRead.model_validate(item)
    
    def delete(self, item_id: int) -> bool:
        """Delete a knowledge item.
        
        Args:
            item_id: Knowledge item ID
            
        Returns:
            True if deleted, False if not found
        """
        item = self.db.query(KnowledgeItem).filter(
            KnowledgeItem.id == item_id
        ).first()
        
        if not item:
            return False
        
        self.db.delete(item)
        self.db.commit()
        return True
