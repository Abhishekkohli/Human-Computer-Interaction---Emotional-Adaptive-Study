"""
Database connection and session management.
Uses SQLAlchemy for ORM with PostgreSQL.

Connection: postgresql://postgres@localhost:5432/postgres
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

# Create SQLAlchemy engine for PostgreSQL
engine = create_engine(DATABASE_URL)

# Create session factory - each request gets a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Dependency injection for database sessions.
    Ensures proper session cleanup after each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - creates all tables.
    Called on application startup.
    """
    from . import models  # Import to register all models
    Base.metadata.create_all(bind=engine)

