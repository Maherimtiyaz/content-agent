"""Brand Profile API routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.brand_profile import (
    BrandProfileCreate,
    BrandProfileUpdate,
    BrandProfileRead,
    ContentPillarCreate,
    ContentPillarRead,
)
from app.services.brand_profile import BrandProfileService
from app.models.user import User

router = APIRouter(prefix="/brand-profiles", tags=["brand-profiles"])


@router.post("", response_model=BrandProfileRead, status_code=status.HTTP_201_CREATED)
def create_brand_profile(
    profile_in: BrandProfileCreate,
    db: Session = Depends(get_db),
) -> BrandProfileRead:
    """Create a new brand profile.
    
    Args:
        profile_in: Brand profile data
        db: Database session
        
    Returns:
        Created brand profile
        
    Raises:
        HTTPException: If user doesn't exist or profile already exists for user
    """
    # Verify user exists
    user = db.query(User).filter(User.id == profile_in.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {profile_in.user_id} not found"
        )
    
    # Check if profile already exists for user
    existing = db.query(BrandProfileService.model).filter(
        BrandProfileService.model.user_id == profile_in.user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand profile already exists for this user"
        )
    
    service = BrandProfileService(db)
    return service.create(profile_in)


@router.get("/{profile_id}", response_model=BrandProfileRead)
def get_brand_profile(
    profile_id: int,
    db: Session = Depends(get_db),
) -> BrandProfileRead:
    """Get a brand profile by ID.
    
    Args:
        profile_id: Brand profile ID
        db: Database session
        
    Returns:
        Brand profile
        
    Raises:
        HTTPException: If profile not found
    """
    service = BrandProfileService(db)
    profile = service.get(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand profile with id {profile_id} not found"
        )
    return profile


@router.get("", response_model=List[BrandProfileRead])
def list_brand_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[BrandProfileRead]:
    """List all brand profiles.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of brand profiles
    """
    service = BrandProfileService(db)
    return service.list(skip=skip, limit=limit)


@router.put("/{profile_id}", response_model=BrandProfileRead)
def update_brand_profile(
    profile_id: int,
    profile_in: BrandProfileUpdate,
    db: Session = Depends(get_db),
) -> BrandProfileRead:
    """Update a brand profile.
    
    Args:
        profile_id: Brand profile ID
        profile_in: Updated brand profile data
        db: Database session
        
    Returns:
        Updated brand profile
        
    Raises:
        HTTPException: If profile not found
    """
    service = BrandProfileService(db)
    profile = service.update(profile_id, profile_in)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand profile with id {profile_id} not found"
        )
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand_profile(
    profile_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a brand profile.
    
    Args:
        profile_id: Brand profile ID
        db: Database session
        
    Raises:
        HTTPException: If profile not found
    """
    service = BrandProfileService(db)
    if not service.delete(profile_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand profile with id {profile_id} not found"
        )
