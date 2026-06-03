# =============================================================
# database.py
#
# PURPOSE: Create and manage the database connection.
#
# We use SQLAlchemy as an abstraction layer. This means:
# - Our code never writes raw SQL for connections
# - Switching from SQLite to PostgreSQL later requires
#   changing ONE line (the DATABASE_URL below)
# =============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------------------------------------------
# DATABASE URL
#
# SQLite format:  sqlite:///./path/to/file.db
# PostgreSQL:     postgresql://user:password@localhost/dbname
#
# To upgrade later, just change this one line.
# The rest of the code stays exactly the same.
# -------------------------------------------------------------
DATABASE_URL = "sqlite:///./database/air_quality.db"

# -------------------------------------------------------------
# ENGINE
# The engine is the core connection to the database.
# connect_args is SQLite-specific — it allows the database
# to be used across multiple threads safely.
# -------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# -------------------------------------------------------------
# SESSION
# A session is like a conversation with the database.
# You open a session, do your reads/writes, then close it.
# autocommit=False means we manually control when to save.
# -------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# -------------------------------------------------------------
# BASE
# All our database models (tables) will inherit from this.
# SQLAlchemy uses this to know which classes are DB tables.
# -------------------------------------------------------------
Base = declarative_base()


def get_db():
    """
    Provide a database session for each request.

    This is a generator function — it yields a session,
    waits for the caller to finish, then closes the session.
    FastAPI will use this to inject DB sessions into routes.

    Usage:
        db = next(get_db())   # in scripts
        # or in FastAPI:
        # def route(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Always close the session — prevents connection leaks
        db.close()