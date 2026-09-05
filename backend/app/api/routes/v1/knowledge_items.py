"""Knowledge Item API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.knowledge_item import (
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemRead,
)
from app.services.knowledge_item import KnowledgeItemService

router = APIRouter(prefix="/knowledge-items", tags=["knowledge-items"])


@router.post("", response_model=KnowledgeItemRead, status_code=status.HTTP_201_CREATED)
def create_knowledge_item(
    item_in: KnowledgeItemCreate,
    db: Session = Depends(get_db),
) -> KnowledgeItemRead:
    """Create a new knowledge item.
    
    Args:
        item_in: Knowledge item data
        db: Database session
        
    Returns:
        Created knowledge item
    """
    service = KnowledgeItemService(db)
    return service.create(item_in)


@router.get("/{item_id}", response_model=KnowledgeItemRead)
def get_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
) -> KnowledgeItemRead:
    """Get a knowledge item by ID.
    
    Args:
        item_id: Knowledge item ID
        db: Database session
        
    Returns:
        Knowledge item
        
    Raises:
        HTTPException: If item not found
    """
    service = KnowledgeItemService(db)
    item = service.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with id {item_id} not found"
        )
    return item


@router.get("", response_model=List[KnowledgeItemRead])
def list_knowledge_items(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    knowledge_type: str = None,
    tag: str = None,
    db: Session = Depends(get_db),
) -> List[KnowledgeItemRead]:
    """List knowledge items with optional filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        user_id: Filter by user ID
        knowledge_type: Filter by knowledge type
        tag: Filter by tag
        db: Database session
        
    Returns:
        List of knowledge items
    """
    service = KnowledgeItemService(db)
    return service.list(
        skip=skip,
        limit=limit,
        user_id=user_id,
        knowledge_type=knowledge_type,
        tag=tag,
    )


@router.put("/{item_id}", response_model=KnowledgeItemRead)
def update_knowledge_item(
    item_id: int,
    item_in: KnowledgeItemUpdate,
    db: Session = Depends(get_db),
) -> KnowledgeItemRead:
    """Update a knowledge item.
    
    Args:
        item_id: Knowledge item ID
        item_in: Updated knowledge item data
        db: Database session
        
    Returns:
        Updated knowledge item
        
    Raises:
        HTTPException: If item not found
    """
    service = KnowledgeItemService(db)
    item = service.update(item_id, item_in)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with id {item_id} not found"
        )
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a knowledge item.
    
    Args:
        item_id: Knowledge item ID
        db: Database session
        
    Raises:
        HTTPException: If item not found
    """
    service = KnowledgeItemService(db)
    if not service.delete(item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with id {item_id} not found"
        )
