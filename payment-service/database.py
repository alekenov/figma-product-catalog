"""
Database connection and session management
"""
from sqlmodel import SQLModel, create_engine, Session
from config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session (dependency)"""
    with Session(engine) as session:
        yield session
