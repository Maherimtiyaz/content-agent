"""Tests for Brand Profile API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestBrandProfileCreation:
    """Test brand profile creation."""
    
    def test_create_brand_profile(self, client: TestClient, test_user, db_session: Session):
        """Test creating a new brand profile."""
        payload = {
            "user_id": test_user.id,
            "name": "My Brand",
            "professional_description": "Senior Software Engineer",
            "experience": "10 years in tech",
            "technical_interests": ["AI", "Cloud", "Security"],
            "skills": ["Python", "AWS", "Kubernetes"],
            "target_audience": "Engineering leaders",
            "writing_style": "Clear and concise",
            "tone": "Professional",
        }
        
        response = client.post("/api/v1/brand-profiles", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Brand"
        assert data["user_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data


class TestBrandProfileRetrieval:
    """Test brand profile retrieval."""
    
    def test_get_brand_profile(self, client: TestClient, test_brand_profile):
        """Test retrieving a brand profile by ID."""
        response = client.get(f"/api/v1/brand-profiles/{test_brand_profile.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_brand_profile.id
        assert data["name"] == test_brand_profile.name


class TestBrandProfileUpdate:
    """Test brand profile updates."""
    
    def test_update_brand_profile(self, client: TestClient, test_brand_profile):
        """Test updating a brand profile."""
        update_payload = {
            "name": "Updated Brand Name",
            "tone": "Casual and friendly",
        }
        
        response = client.put(
            f"/api/v1/brand-profiles/{test_brand_profile.id}",
            json=update_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Brand Name"
        assert data["tone"] == "Casual and friendly"
        assert data["id"] == test_brand_profile.id


class TestBrandProfileDeletion:
    """Test brand profile deletion."""
    
    def test_delete_brand_profile(self, client: TestClient, test_brand_profile):
        """Test deleting a brand profile."""
        response = client.delete(f"/api/v1/brand-profiles/{test_brand_profile.id}")
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/brand-profiles/{test_brand_profile.id}")
        assert get_response.status_code == 404


class TestBrandProfileList:
    """Test brand profile listing."""
    
    def test_list_brand_profiles(self, client: TestClient, test_brand_profile):
        """Test listing brand profiles."""
        response = client.get("/api/v1/brand-profiles")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(p["id"] == test_brand_profile.id for p in data)
