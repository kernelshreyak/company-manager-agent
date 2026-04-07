#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text

from company_manager.db import Base, get_engine
from company_manager import models  # noqa: F401


def ensure_schema_updates() -> None:
    engine = get_engine()
    inspector = inspect(engine)
    if "meetings" not in inspector.get_table_names():
        return
    meeting_columns = {column["name"] for column in inspector.get_columns("meetings")}
    with engine.begin() as connection:
        if "status" not in meeting_columns:
            connection.execute(
                text("ALTER TABLE meetings ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'scheduled'")
            )


def main() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    ensure_schema_updates()
    print(f"Initialized schema at {engine.url.render_as_string(hide_password=False)}")


if __name__ == "__main__":
    main()
