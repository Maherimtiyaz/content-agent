"""Brand Profile and Content Pillar models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class BrandProfile(Base):
    """Brand profile representing the user's professional identity.
    
    This becomes core context for content generation.
    """
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Professional identity
    name = Column(String(255), nullable=False)
    professional_description = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)  # Career history, achievements
    
    # Technical focus
    technical_interests = Column(JSON, nullable=True)  # List of interests
    skills = Column(JSON, nullable=True)  # List of skills
    
    # Audience & positioning
    target_audience = Column(Text, nullable=True)
    
    # Content strategy
    content_pillars = relationship("ContentPillar", back_populates="brand_profile", cascade="all, delete-orphan")
    
    # Writing style
    writing_style = Column(Text, nullable=True)
    tone = Column(String(100), nullable=True)
    opinions = Column(Text, nullable=True)  # Strong opinions to express
    topics_to_avoid = Column(Text, nullable=True)
    
    # Examples & goals
    example_posts = Column(JSON, nullable=True)  # List of example post texts
    personal_goals = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="brand_profile")


class ContentPillar(Base):
    """Content pillar defining a主题 area for the brand.
    
    Content pillars help organize and focus content creation.
    """
    __tablename__ = "content_pillars"

    id = Column(Integer, primary_key=True, index=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    brand_profile = relationship("BrandProfile", back_populates="content_pillars")
