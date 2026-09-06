"""Test fixtures and configuration."""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import get_settings

# Use SQLite in-memory database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield engine
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app=app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user."""
    from app.models.user import User
    
    user = User(
        email="test@example.com",
        name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture
def test_brand_profile(db_session: Session, test_user):
    """Create a test brand profile."""
    from app.models.brand_profile import BrandProfile
    
    profile = BrandProfile(
        user_id=test_user.id,
        name="Test Brand",
        professional_description="Software Engineer specializing in AI",
        experience="5 years building distributed systems",
        technical_interests=["AI", "Distributed Systems", "Python"],
        skills=["Python", "FastAPI", "PostgreSQL"],
        target_audience="Software engineers interested in AI",
        writing_style="Technical but accessible",
        tone="Professional and friendly",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    
    return profile


@pytest.fixture
def test_knowledge_item(db_session: Session, test_user):
    """Create a test knowledge item."""
    from app.models.knowledge_item import KnowledgeItem, KnowledgeType
    
    item = KnowledgeItem(
        user_id=test_user.id,
        title="Building FastAPI Applications",
        content="# FastAPI Best Practices\n\nHere are some lessons learned...",
        knowledge_type=KnowledgeType.LESSON,
        tags="fastapi, python, api",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    
    return item
