"""Test fixtures and configuration."""

import os
import sys

# MUST set TESTING before any app imports to ensure correct config loading
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Clear ANY cached app modules IMMEDIATELY - before any other imports
# This is critical because pytest may have already imported some app modules
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith('app') or 'pydantic_settings' in mod_name:
        del sys.modules[mod_name]

import pytest
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Import models FIRST to register them with Base metadata
from app.models import Base  # This imports all models and registers them

# Now import app modules after models are registered
from app.main import app
from app.db.session import get_db

# Use SQLite in-memory database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Remove existing test.db to start fresh
if os.path.exists("test.db"):
    os.remove("test.db")

# Enable foreign keys for SQLite
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key support in SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    """Create all test tables before running tests."""
    # Create all tables in the test database ONCE at session start
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test with proper transaction handling."""
    # Ensure tables exist
    Base.metadata.create_all(bind=test_engine)
    
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session", autouse=True)
def _setup_test_db():
    """Ensure database tables exist before any test fixtures run."""
    Base.metadata.create_all(bind=test_engine)
    yield
    # Don't drop tables here - let session fixture handle cleanup


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency.
    
    This fixture creates its own session and manages the full lifecycle.
    Tests that need pre-existing data should use the test_user, test_brand_profile,
    etc. fixtures which will use the same session through the db override.
    """
    # Create a fresh session for this test with proper transaction isolation
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app=app, base_url="http://testserver") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_user(client: TestClient) -> dict:
    """Create a test user directly in the database.
    
    Uses the client's database session to ensure consistency.
    Returns the user data as a dict.
    """
    from app.models.user import User
    
    # Get the session from the app's dependency override
    db = next(app.dependency_overrides[get_db]())
    
    user = User(
        email="test@example.com",
        name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"id": user.id, "email": user.email, "name": user.name}


@pytest.fixture
def test_brand_profile(client: TestClient, test_user: dict):
    """Create a test brand profile."""
    from app.models.brand_profile import BrandProfile
    
    # Get the session from the app's dependency override
    db = next(app.dependency_overrides[get_db]())
    
    profile = BrandProfile(
        user_id=test_user["id"],
        name="Test Brand",
        professional_description="Software Engineer specializing in AI",
        experience="5 years building distributed systems",
        technical_interests=["AI", "Distributed Systems", "Python"],
        skills=["Python", "FastAPI", "PostgreSQL"],
        target_audience="Software engineers interested in AI",
        writing_style="Technical but accessible",
        tone="Professional and friendly",
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile


@pytest.fixture
def test_knowledge_item(client: TestClient, test_user: dict):
    """Create a test knowledge item."""
    from app.models.knowledge_item import KnowledgeItem, KnowledgeType
    
    # Get the session from the app's dependency override
    db = next(app.dependency_overrides[get_db]())
    
    item = KnowledgeItem(
        user_id=test_user["id"],
        title="Building FastAPI Applications",
        content="# FastAPI Best Practices\n\nHere are some lessons learned...",
        knowledge_type=KnowledgeType.LESSON,
        tags="fastapi, python, api",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item
