"""
Database Configuration for AI Triage System

This module sets up SQLAlchemy database connection and session management.
Uses SQLite for simplicity but can be easily switched to PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - Using SQLite for simplicity
# For PostgreSQL, use: postgresql://user:password@localhost/triage_db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./triage_database.db")

# Create SQLAlchemy engine
# connect_args is only needed for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    Call this function to set up the database schema.
    """
    # Import models here to avoid circular imports
    from backend import models
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
