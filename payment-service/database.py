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
    """Create all database tables and run migrations"""
    # Create tables from models
    SQLModel.metadata.create_all(engine)

    # Run migrations for schema changes
    with Session(engine) as session:
        # Migration: Add device_token column if not exists
        try:
            from sqlalchemy import text
            session.exec(text("""
                ALTER TABLE paymentconfig
                ADD COLUMN IF NOT EXISTS device_token VARCHAR(20);
            """))
            session.commit()
            print("✅ Migration: device_token column added/verified")
        except Exception as e:
            print(f"⚠️  Migration warning: {e}")
            session.rollback()


def get_session():
    """Get database session (dependency)"""
    with Session(engine) as session:
        yield session
