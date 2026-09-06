"""Tests for Knowledge Item API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.knowledge_item import KnowledgeType


class TestKnowledgeItemCreation:
    """Test knowledge item creation."""
    
    def test_create_knowledge_item(self, client: TestClient, test_user):
        """Test creating a new knowledge item."""
        payload = {
            "user_id": test_user.id,
            "title": "My First Lesson",
            "content": "# Lesson Content\n\nThis is what I learned...",
            "knowledge_type": "lesson",
            "tags": ["python", "testing"],
        }
        
        response = client.post("/api/v1/knowledge-items", json=payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My First Lesson"
        assert data["user_id"] == test_user.id
        assert data["knowledge_type"] == "lesson"
        assert "id" in data


class TestKnowledgeItemRetrieval:
    """Test knowledge item retrieval."""
    
    def test_get_knowledge_item(self, client: TestClient, test_knowledge_item):
        """Test retrieving a knowledge item by ID."""
        response = client.get(f"/api/v1/knowledge-items/{test_knowledge_item.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_knowledge_item.id
        assert data["title"] == test_knowledge_item.title


class TestKnowledgeItemUpdate:
    """Test knowledge item updates."""
    
    def test_update_knowledge_item(self, client: TestClient, test_knowledge_item):
        """Test updating a knowledge item."""
        update_payload = {
            "title": "Updated Title",
            "content": "# Updated Content\n\nNew information here...",
            "tags": ["updated", "new-tag"],
        }
        
        response = client.put(
            f"/api/v1/knowledge-items/{test_knowledge_item.id}",
            json=update_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["tags"] == ["updated", "new-tag"]


class TestKnowledgeItemDeletion:
    """Test knowledge item deletion."""
    
    def test_delete_knowledge_item(self, client: TestClient, test_knowledge_item):
        """Test deleting a knowledge item."""
        response = client.delete(f"/api/v1/knowledge-items/{test_knowledge_item.id}")
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/knowledge-items/{test_knowledge_item.id}")
        assert get_response.status_code == 404


class TestKnowledgeItemList:
    """Test knowledge item listing."""
    
    def test_list_knowledge_items(self, client: TestClient, test_knowledge_item):
        """Test listing all knowledge items."""
        response = client.get("/api/v1/knowledge-items")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(item["id"] == test_knowledge_item.id for item in data)
    
    def test_list_knowledge_items_by_user(self, client: TestClient, test_user, test_knowledge_item):
        """Test filtering knowledge items by user ID."""
        response = client.get(f"/api/v1/knowledge-items?user_id={test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["user_id"] == test_user.id for item in data)
    
    def test_list_knowledge_items_by_type(self, client: TestClient, test_knowledge_item):
        """Test filtering knowledge items by type."""
        response = client.get(f"/api/v1/knowledge-items?knowledge_type={KnowledgeType.LESSON.value}")
        
        assert response.status_code == 200
        data = response.json()
        assert all(item["knowledge_type"] == "lesson" for item in data)
    
    def test_list_knowledge_items_by_tag(self, client: TestClient, test_knowledge_item):
        """Test filtering knowledge items by tag."""
        response = client.get("/api/v1/knowledge-items?tag=fastapi")
        
        assert response.status_code == 200
        data = response.json()
        # Should contain the item with 'fastapi' tag
        assert len(data) >= 1
