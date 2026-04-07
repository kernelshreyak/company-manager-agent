#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from company_manager.db import SessionLocal
from company_manager.seed import seed_demo_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo company data")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    with SessionLocal() as session:
        seed_demo_data(session, seed=args.seed)
    print(f"Seeded demo company data with seed={args.seed}")


if __name__ == "__main__":
    main()
