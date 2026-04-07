#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from company_manager.db import SessionLocal
from company_manager.tooling import (
    cancel_meeting,
    company_snapshot,
    create_task,
    delete_meeting,
    list_employees,
    list_meetings,
    list_orders,
    list_products,
    list_tasks,
    reschedule_meeting,
    schedule_meeting,
    update_task_status,
)


def emit(payload: dict | list) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Company manager DB tool")
    subparsers = root.add_subparsers(dest="command", required=True)

    subparsers.add_parser("summary")

    employee_parser = subparsers.add_parser("employees")
    employee_parser.add_argument("--department")
    employee_parser.add_argument("--limit", type=int, default=20)

    product_parser = subparsers.add_parser("products")
    product_parser.add_argument("--limit", type=int, default=20)

    order_parser = subparsers.add_parser("orders")
    order_parser.add_argument("--status")
    order_parser.add_argument("--limit", type=int, default=20)

    meeting_parser = subparsers.add_parser("meetings")
    meeting_parser.add_argument("--all", action="store_true")
    meeting_parser.add_argument("--include-cancelled", action="store_true")
    meeting_parser.add_argument("--limit", type=int, default=10)

    task_parser = subparsers.add_parser("tasks")
    task_parser.add_argument("--status")
    task_parser.add_argument("--limit", type=int, default=20)

    create_task_parser = subparsers.add_parser("create-task")
    create_task_parser.add_argument("--title", required=True)
    create_task_parser.add_argument("--description", default="")
    create_task_parser.add_argument("--owner-email")
    create_task_parser.add_argument("--priority", default="medium", choices=["low", "medium", "high", "critical"])
    create_task_parser.add_argument("--due-date")

    update_task_parser = subparsers.add_parser("update-task-status")
    update_task_parser.add_argument("--task-id", type=int, required=True)
    update_task_parser.add_argument("--status", required=True, choices=["todo", "in_progress", "blocked", "done"])

    schedule_parser = subparsers.add_parser("schedule-meeting")
    schedule_parser.add_argument("--title", required=True)
    schedule_parser.add_argument("--start-at", required=True, help="ISO timestamp, example 2026-04-08T15:00:00")
    schedule_parser.add_argument("--duration-minutes", type=int, default=30)
    schedule_parser.add_argument("--location", default="Zoom")
    schedule_parser.add_argument("--agenda", default="")
    schedule_parser.add_argument("--attendee-email", action="append", default=[])
    schedule_parser.add_argument("--created-by", default="agent")

    reschedule_parser = subparsers.add_parser("reschedule-meeting")
    reschedule_parser.add_argument("--meeting-id", type=int, required=True)
    reschedule_parser.add_argument("--start-at", required=True, help="ISO timestamp, example 2026-04-13T15:00:00")
    reschedule_parser.add_argument("--duration-minutes", type=int)
    reschedule_parser.add_argument("--location")
    reschedule_parser.add_argument("--agenda")
    reschedule_parser.add_argument("--title")

    cancel_parser = subparsers.add_parser("cancel-meeting")
    cancel_parser.add_argument("--meeting-id", type=int, required=True)

    delete_parser = subparsers.add_parser("delete-meeting")
    delete_parser.add_argument("--meeting-id", type=int, required=True)

    return root


def main() -> None:
    args = parser().parse_args()
    with SessionLocal() as session:
        if args.command == "summary":
            emit(company_snapshot(session))
        elif args.command == "employees":
            emit(list_employees(session, department=args.department, limit=args.limit))
        elif args.command == "products":
            emit(list_products(session, limit=args.limit))
        elif args.command == "orders":
            emit(list_orders(session, status=args.status, limit=args.limit))
        elif args.command == "meetings":
            emit(
                list_meetings(
                    session,
                    upcoming_only=not args.all,
                    include_cancelled=args.include_cancelled,
                    limit=args.limit,
                )
            )
        elif args.command == "tasks":
            emit(list_tasks(session, status=args.status, limit=args.limit))
        elif args.command == "create-task":
            emit(
                create_task(
                    session,
                    title=args.title,
                    description=args.description,
                    owner_email=args.owner_email,
                    priority=args.priority,
                    due_date_value=args.due_date,
                )
            )
        elif args.command == "update-task-status":
            emit(update_task_status(session, task_id=args.task_id, status=args.status))
        elif args.command == "schedule-meeting":
            emit(
                schedule_meeting(
                    session,
                    title=args.title,
                    start_at=args.start_at,
                    duration_minutes=args.duration_minutes,
                    location=args.location,
                    agenda=args.agenda,
                    attendee_emails=args.attendee_email,
                    created_by=args.created_by,
                )
            )
        elif args.command == "reschedule-meeting":
            emit(
                reschedule_meeting(
                    session,
                    meeting_id=args.meeting_id,
                    start_at=args.start_at,
                    duration_minutes=args.duration_minutes,
                    location=args.location,
                    agenda=args.agenda,
                    title=args.title,
                )
            )
        elif args.command == "cancel-meeting":
            emit(cancel_meeting(session, meeting_id=args.meeting_id))
        elif args.command == "delete-meeting":
            emit(delete_meeting(session, meeting_id=args.meeting_id))


if __name__ == "__main__":
    main()
