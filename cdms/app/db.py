from sqlmodel import SQLModel, create_engine

from app import models  # noqa: F401
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
