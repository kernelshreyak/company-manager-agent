---
name: company-manager
description: Read company data from a SQLite database and create executive tasks or meetings using the company manager Python CLI.
metadata: { "openclaw": { "emoji": "🏢", "requires": { "bins": ["python3"] } } }
---

# company-manager

Use this skill when the user asks about company operations, employees, products, orders, meetings, or wants you to assign work inside the company manager demo database.

Project root: `/home/shreyak/programming/company-manager-agent`

Before first use in a fresh environment:

- `cd /home/shreyak/programming/company-manager-agent`
- `python3 -m venv .venv`
- `.venv/bin/pip install -e .`
- `.venv/bin/python scripts/migrate.py`
- `.venv/bin/python scripts/seed_demo_data.py`

Use these commands and prefer JSON output exactly as printed:

- Company snapshot: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py summary`
- Employees: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py employees --limit 20`
- Employees by department: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py employees --department Engineering --limit 20`
- Products: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py products --limit 20`
- Orders: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py orders --limit 20`
- Orders by status: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py orders --status pending --limit 20`
- Upcoming meetings: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py meetings --limit 10`
- Tasks: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py tasks --limit 20`
- Create task: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py create-task --title "Prepare board update" --description "Summarize pipeline and delivery risk." --owner-email ava.patel21@northstar.example --priority high --due-date 2026-04-12`
- Update task status: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py update-task-status --task-id 3 --status in_progress`
- Schedule meeting: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py schedule-meeting --title "CEO staff sync" --start-at 2026-04-08T15:00:00 --duration-minutes 45 --location Zoom --agenda "Weekly exec review" --attendee-email ava.patel10@northstar.example --attendee-email ethan.kim11@northstar.example --created-by agent`

Rules:

- Query the database before answering. Do not invent metrics, people, order counts, or task state.
- When assigning work, create or update a task instead of only replying in prose.
- When arranging follow-ups, schedule a meeting if the user asked for a meeting or review.
- If the user asks for a status summary, call `summary` first and then drill down with `orders`, `tasks`, or `meetings` as needed.
