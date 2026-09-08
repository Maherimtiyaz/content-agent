"""Test fixtures and configuration."""

import os
import sys

# MUST set TESTING before any app imports to ensure correct config loading
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Clear ANY cached app modules IMMEDIATELY - before any other imports
# This is critical because pytest may have already imported some app modules
for mod_name in list(sys.modules.keys()):
    if 'app' in mod_name or 'pydantic_settings' in mod_name:
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


@pytest.fixture(scope="function", autouse=True)
def _setup_test_db():
    """Ensure database tables exist before any test fixtures run."""
    Base.metadata.create_all(bind=test_engine)
    yield
    # Don't drop tables here - let session fixture handle cleanup


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a test client with overridden database dependency."""
    # Ensure tables are created before any API calls
    Base.metadata.create_all(bind=test_engine)
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app=app, base_url="http://testserver") as test_client:
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
