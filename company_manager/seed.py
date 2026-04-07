from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.orm import Session

from company_manager.models import (
    Company,
    Customer,
    Department,
    Employee,
    Meeting,
    MeetingAttendee,
    Order,
    OrderItem,
    OrderStatus,
    Priority,
    Product,
    Task,
    TaskStatus,
)


FIRST_NAMES = [
    "Ava",
    "Ethan",
    "Mia",
    "Noah",
    "Sophia",
    "Liam",
    "Olivia",
    "Arjun",
    "Isha",
    "Daniel",
    "Harper",
    "Zara",
]
LAST_NAMES = [
    "Patel",
    "Nguyen",
    "Smith",
    "Johnson",
    "Garcia",
    "Kim",
    "Brown",
    "Taylor",
    "Lee",
    "Martinez",
]
LOCATIONS = ["Bengaluru", "Mumbai", "London", "Singapore", "New York", "Remote"]


def _money(value: int | float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def seed_demo_data(session: Session, seed: int = 42) -> None:
    random.seed(seed)

    for model in [MeetingAttendee, Task, Meeting, OrderItem, Order, Product, Customer, Employee, Department, Company]:
        session.execute(delete(model))

    company = Company(name="Northstar Dynamics", industry="Industrial SaaS", headquarters="Bengaluru")
    session.add(company)
    session.flush()

    departments = [
        Department(company_id=company.id, name="Executive", budget_usd=_money(1800000)),
        Department(company_id=company.id, name="Sales", budget_usd=_money(3200000)),
        Department(company_id=company.id, name="Engineering", budget_usd=_money(5800000)),
        Department(company_id=company.id, name="Operations", budget_usd=_money(2100000)),
        Department(company_id=company.id, name="Customer Success", budget_usd=_money(1700000)),
    ]
    session.add_all(departments)
    session.flush()

    title_map = {
        "Executive": ["CEO", "COO", "CFO"],
        "Sales": ["VP Sales", "Account Executive", "Sales Ops Lead"],
        "Engineering": ["VP Engineering", "Engineering Manager", "Senior Engineer"],
        "Operations": ["Director of Operations", "Program Manager", "Supply Analyst"],
        "Customer Success": ["Head of CS", "Customer Success Manager", "Support Lead"],
    }

    employees: list[Employee] = []
    for department in departments:
        for idx in range(5 if department.name != "Executive" else 3):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            email = f"{first_name.lower()}.{last_name.lower()}{department.id}{idx}@northstar.example"
            employee = Employee(
                department_id=department.id,
                first_name=first_name,
                last_name=last_name,
                title=title_map[department.name][min(idx, len(title_map[department.name]) - 1)],
                email=email,
                location=random.choice(LOCATIONS),
                hire_date=date.today() - timedelta(days=random.randint(60, 2200)),
                salary_usd=_money(random.randint(65000, 260000)),
                active=True,
            )
            employees.append(employee)
    session.add_all(employees)
    session.flush()

    employees_by_department: dict[str, list[Employee]] = {}
    for employee in employees:
        department_name = next(d.name for d in departments if d.id == employee.department_id)
        employees_by_department.setdefault(department_name, []).append(employee)

    for _, department_employees in employees_by_department.items():
        manager = department_employees[0]
        for employee in department_employees[1:]:
            employee.manager_id = manager.id

    product_specs = [
        ("FactorySense Core", "Industrial Analytics", 499),
        ("FactorySense Edge", "Industrial Analytics", 899),
        ("Northstar Planner", "Planning", 349),
        ("Northstar Mobile", "Field Ops", 99),
        ("Northstar Vision", "Quality", 799),
        ("Northstar Integrations", "Platform", 199),
    ]
    products = []
    for idx, (name, category, price) in enumerate(product_specs, start=1):
        products.append(
            Product(
                company_id=company.id,
                name=name,
                sku=f"NS-{idx:03d}",
                category=category,
                price_usd=_money(price),
                inventory_count=random.randint(20, 250),
                active=True,
            )
        )
    session.add_all(products)
    session.flush()

    customers = []
    for idx in range(18):
        customers.append(
            Customer(
                company_id=company.id,
                name=f"{random.choice(['Atlas', 'Beacon', 'Cobalt', 'Delta', 'Evergreen', 'Frontier'])} Holdings {idx + 1}",
                email=f"buyer{idx + 1}@customer.example",
                tier=random.choice(["Enterprise", "Mid-Market", "SMB"]),
                region=random.choice(["India", "EMEA", "North America", "APAC"]),
            )
        )
    session.add_all(customers)
    session.flush()

    orders = []
    order_items = []
    now = datetime.utcnow()
    for _ in range(36):
        customer = random.choice(customers)
        status = random.choice(list(OrderStatus))
        ordered_at = now - timedelta(days=random.randint(1, 120), hours=random.randint(0, 20))
        item_count = random.randint(1, 3)
        selected_products = random.sample(products, k=item_count)
        total = Decimal("0.00")
        order = Order(customer_id=customer.id, status=status, ordered_at=ordered_at, shipped_at=None, total_usd=_money(0), notes=None)
        session.add(order)
        session.flush()
        for product in selected_products:
            quantity = random.randint(1, 6)
            total += product.price_usd * quantity
            order_items.append(
                OrderItem(order_id=order.id, product_id=product.id, quantity=quantity, unit_price_usd=product.price_usd)
            )
        if status in {OrderStatus.shipped, OrderStatus.delivered}:
            order.shipped_at = ordered_at + timedelta(days=random.randint(1, 7))
        order.total_usd = total.quantize(Decimal("0.01"))
        orders.append(order)
    session.add_all(order_items)

    tasks = [
        Task(
            owner_id=employees_by_department["Sales"][1].id,
            title="Prepare Q2 enterprise pipeline review",
            description="Summarize top deals, close probability, and risk factors.",
            status=TaskStatus.in_progress,
            priority=Priority.high,
            due_date=date.today() + timedelta(days=3),
        ),
        Task(
            owner_id=employees_by_department["Engineering"][1].id,
            title="Assess delayed rollout for Edge firmware",
            description="Propose recovery options and staffing constraints.",
            status=TaskStatus.blocked,
            priority=Priority.critical,
            due_date=date.today() + timedelta(days=2),
        ),
        Task(
            owner_id=employees_by_department["Operations"][1].id,
            title="Review Asia-Pacific fulfillment bottlenecks",
            description="Identify top 3 causes of late shipments.",
            status=TaskStatus.todo,
            priority=Priority.high,
            due_date=date.today() + timedelta(days=5),
        ),
        Task(
            owner_id=employees_by_department["Customer Success"][1].id,
            title="Stabilize renewal plan for Beacon Holdings 7",
            description="Draft save plan and pricing options.",
            status=TaskStatus.in_progress,
            priority=Priority.medium,
            due_date=date.today() + timedelta(days=7),
        ),
    ]
    session.add_all(tasks)

    meetings = [
        Meeting(
            title="Executive business review",
            start_at=now + timedelta(days=1, hours=2),
            duration_minutes=60,
            location="Zoom",
            agenda="Revenue health, hiring plan, and product launch readiness.",
            created_by="system",
        ),
        Meeting(
            title="Operations standup",
            start_at=now + timedelta(days=1, hours=5),
            duration_minutes=30,
            location="Conference Room A",
            agenda="Order backlog, shipping risk, and warehouse staffing.",
            created_by="system",
        ),
        Meeting(
            title="Product and engineering sync",
            start_at=now + timedelta(days=2, hours=3),
            duration_minutes=45,
            location="Zoom",
            agenda="Review roadmap slippage and release plan.",
            created_by="system",
        ),
    ]
    session.add_all(meetings)
    session.flush()

    attendee_links = [
        (meetings[0], employees_by_department["Executive"][:3]),
        (meetings[1], employees_by_department["Operations"][:3]),
        (meetings[2], employees_by_department["Engineering"][:3] + employees_by_department["Executive"][:1]),
    ]
    for meeting, attendees in attendee_links:
        for employee in attendees:
            session.add(MeetingAttendee(meeting_id=meeting.id, employee_id=employee.id, role="attendee"))

    session.commit()
