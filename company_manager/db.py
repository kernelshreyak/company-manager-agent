from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "data" / "company_manager.db"


class Base(DeclarativeBase):
    pass


def get_database_url() -> str:
    url = os.environ.get("COMPANY_MANAGER_DB_URL")
    if url:
        return url
    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DEFAULT_DB_PATH}"


def get_engine(echo: bool = False):
    return create_engine(get_database_url(), echo=echo, future=True)


SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)
