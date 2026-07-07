import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Use SQLite with file-based database
DB_PATH = os.path.join(os.path.dirname(__file__), "rules_engine.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# For SQLite, use StaticPool to avoid threading issues
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency injection for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)
