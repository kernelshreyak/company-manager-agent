from __future__ import annotations

from collections import Counter
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from company_manager.models import Department, Employee, Meeting, MeetingAttendee, Order, OrderItem, OrderStatus, Priority, Product, Task, TaskStatus


def company_snapshot(session: Session) -> dict:
    employee_count = session.scalar(select(func.count()).select_from(Employee)) or 0
    active_tasks = session.scalar(select(func.count()).select_from(Task).where(Task.status != TaskStatus.done)) or 0
    product_count = session.scalar(select(func.count()).select_from(Product)) or 0
    order_count = session.scalar(select(func.count()).select_from(Order)) or 0
    open_orders = session.scalar(
        select(func.count()).select_from(Order).where(
            Order.status.in_([OrderStatus.pending, OrderStatus.processing, OrderStatus.shipped])
        )
    ) or 0
    revenue = session.scalar(select(func.coalesce(func.sum(Order.total_usd), 0)).select_from(Order)) or 0

    task_statuses = Counter(row[0] for row in session.execute(select(Task.status)).all())

    return {
        "employees": employee_count,
        "products": product_count,
        "orders": order_count,
        "open_orders": open_orders,
        "active_tasks": active_tasks,
        "booked_revenue_usd": float(revenue),
        "task_status_breakdown": dict(task_statuses),
    }


def list_employees(session: Session, department: str | None = None, limit: int = 20) -> list[dict]:
    query = select(Employee)
    if department:
        query = query.join(Department).where(func.lower(Department.name) == department.lower())
    query = query.order_by(Employee.last_name, Employee.first_name).limit(limit)
    rows = session.scalars(query).all()
    return [
        {
            "id": row.id,
            "name": row.full_name,
            "title": row.title,
            "email": row.email,
            "location": row.location,
            "department_id": row.department_id,
        }
        for row in rows
    ]


def list_products(session: Session, limit: int = 20) -> list[dict]:
    rows = session.scalars(select(Product).order_by(Product.name).limit(limit)).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "sku": row.sku,
            "category": row.category,
            "price_usd": float(row.price_usd),
            "inventory_count": row.inventory_count,
        }
        for row in rows
    ]


def list_orders(session: Session, status: str | None = None, limit: int = 20) -> list[dict]:
    query = (
        select(Order)
        .options(joinedload(Order.customer), joinedload(Order.items).joinedload(OrderItem.product))
        .order_by(Order.ordered_at.desc())
    )
    if status:
        query = query.where(Order.status == OrderStatus(status))
    query = query.limit(limit)
    rows = session.scalars(query).unique().all()
    return [
        {
            "id": row.id,
            "customer": row.customer.name,
            "status": row.status.value,
            "ordered_at": row.ordered_at.isoformat(),
            "total_usd": float(row.total_usd),
            "items": [
                {
                    "product": item.product.name,
                    "quantity": item.quantity,
                    "unit_price_usd": float(item.unit_price_usd),
                }
                for item in row.items
            ],
        }
        for row in rows
    ]


def list_meetings(session: Session, upcoming_only: bool = True, limit: int = 10) -> list[dict]:
    query = (
        select(Meeting)
        .options(joinedload(Meeting.attendees).joinedload(MeetingAttendee.employee))
        .order_by(Meeting.start_at.asc())
    )
    if upcoming_only:
        query = query.where(Meeting.start_at >= datetime.utcnow())
    query = query.limit(limit)
    rows = session.scalars(query).unique().all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "start_at": row.start_at.isoformat(),
            "duration_minutes": row.duration_minutes,
            "location": row.location,
            "agenda": row.agenda,
            "attendees": [attendee.employee.full_name for attendee in row.attendees],
        }
        for row in rows
    ]


def list_tasks(session: Session, status: str | None = None, limit: int = 20) -> list[dict]:
    query = select(Task).options(joinedload(Task.owner)).order_by(Task.created_at.desc())
    if status:
        query = query.where(Task.status == TaskStatus(status))
    query = query.limit(limit)
    rows = session.scalars(query).all()
    return [
        {
            "id": row.id,
            "title": row.title,
            "description": row.description,
            "status": row.status.value,
            "priority": row.priority.value,
            "owner": row.owner.full_name if row.owner else None,
            "owner_id": row.owner_id,
            "due_date": row.due_date.isoformat() if row.due_date else None,
        }
        for row in rows
    ]


def create_task(
    session: Session,
    title: str,
    description: str,
    owner_email: str | None,
    priority: str,
    due_date_value: str | None,
) -> dict:
    owner = None
    if owner_email:
        owner = session.scalar(select(Employee).where(func.lower(Employee.email) == owner_email.lower()))
    task = Task(
        owner_id=owner.id if owner else None,
        title=title,
        description=description,
        priority=Priority(priority),
        due_date=date.fromisoformat(due_date_value) if due_date_value else None,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "owner": owner.full_name if owner else None,
        "status": task.status.value,
        "priority": task.priority.value,
        "due_date": task.due_date.isoformat() if task.due_date else None,
    }


def update_task_status(session: Session, task_id: int, status: str) -> dict:
    task = session.get(Task, task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    task.status = TaskStatus(status)
    session.commit()
    session.refresh(task)
    return {"id": task.id, "status": task.status.value, "updated_at": task.updated_at.isoformat()}


def schedule_meeting(
    session: Session,
    title: str,
    start_at: str,
    duration_minutes: int,
    location: str,
    agenda: str,
    attendee_emails: list[str],
    created_by: str,
) -> dict:
    meeting = Meeting(
        title=title,
        start_at=datetime.fromisoformat(start_at),
        duration_minutes=duration_minutes,
        location=location,
        agenda=agenda,
        created_by=created_by,
    )
    session.add(meeting)
    session.flush()
    attendees = []
    for email in attendee_emails:
        employee = session.scalar(select(Employee).where(func.lower(Employee.email) == email.lower()))
        if employee:
            attendees.append(employee.full_name)
            session.add(MeetingAttendee(meeting_id=meeting.id, employee_id=employee.id, role="attendee"))
    session.commit()
    return {
        "id": meeting.id,
        "title": meeting.title,
        "start_at": meeting.start_at.isoformat(),
        "location": meeting.location,
        "attendees": attendees,
    }
