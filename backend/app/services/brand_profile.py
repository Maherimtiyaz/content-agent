"""Brand Profile service."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.brand_profile import BrandProfile, ContentPillar
from app.schemas.brand_profile import (
    BrandProfileCreate,
    BrandProfileUpdate,
    BrandProfileRead,
    ContentPillarCreate,
)


class BrandProfileService:
    """Service for brand profile business logic."""
    
    model = BrandProfile
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, profile_in: BrandProfileCreate) -> BrandProfileRead:
        """Create a new brand profile.
        
        Args:
            profile_in: Brand profile data
            
        Returns:
            Created brand profile
        """
        # Create brand profile
        profile_data = profile_in.model_dump(exclude={'content_pillars'})
        db_profile = BrandProfile(**profile_data)
        self.db.add(db_profile)
        self.db.flush()  # Get the ID
        
        # Create content pillars if provided
        if profile_in.content_pillars:
            for pillar_in in profile_in.content_pillars:
                pillar = ContentPillar(
                    brand_profile_id=db_profile.id,
                    **pillar_in.model_dump()
                )
                self.db.add(pillar)
        
        self.db.commit()
        self.db.refresh(db_profile)
        
        return BrandProfileRead.model_validate(db_profile)
    
    def get(self, profile_id: int) -> Optional[BrandProfileRead]:
        """Get a brand profile by ID.
        
        Args:
            profile_id: Brand profile ID
            
        Returns:
            Brand profile or None
        """
        profile = self.db.query(BrandProfile).filter(
            BrandProfile.id == profile_id
        ).first()
        
        if not profile:
            return None
        
        return BrandProfileRead.model_validate(profile)
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BrandProfileRead]:
        """List brand profiles.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of brand profiles
        """
        profiles = self.db.query(BrandProfile).offset(skip).limit(limit).all()
        return [BrandProfileRead.model_validate(p) for p in profiles]
    
    def update(
        self,
        profile_id: int,
        profile_in: BrandProfileUpdate,
    ) -> Optional[BrandProfileRead]:
        """Update a brand profile.
        
        Args:
            profile_id: Brand profile ID
            profile_in: Updated brand profile data
            
        Returns:
            Updated brand profile or None
        """
        profile = self.db.query(BrandProfile).filter(
            BrandProfile.id == profile_id
        ).first()
        
        if not profile:
            return None
        
        # Update fields
        update_data = profile_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        self.db.commit()
        self.db.refresh(profile)
        
        return BrandProfileRead.model_validate(profile)
    
    def delete(self, profile_id: int) -> bool:
        """Delete a brand profile.
        
        Args:
            profile_id: Brand profile ID
            
        Returns:
            True if deleted, False if not found
        """
        profile = self.db.query(BrandProfile).filter(
            BrandProfile.id == profile_id
        ).first()
        
        if not profile:
            return False
        
        self.db.delete(profile)
        self.db.commit()
        return True
