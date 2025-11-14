from sqlmodel import Session

from src.backend.db.database import engine


def get_session():
    """Dependency that yields a SQLModel Session."""
    with Session(engine) as session:
        yield session
