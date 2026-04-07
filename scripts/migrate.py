#!/usr/bin/env python3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from company_manager.db import Base, get_engine
from company_manager import models  # noqa: F401


def main() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    print(f"Initialized schema at {engine.url.render_as_string(hide_password=False)}")


if __name__ == "__main__":
    main()
