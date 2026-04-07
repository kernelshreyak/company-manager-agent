---
name: company-manager
description: Use the local Northstar Dynamics SQLite database for company operations questions, including asks like "what meetings do I have this week", meeting schedules, company status, employee lookups, and creating, rescheduling, cancelling, or deleting executive meetings and tasks.
metadata: { "openclaw": { "emoji": "🏢", "requires": { "bins": ["python3"] } } }
---

# company-manager

Use this skill when the user asks about company operations, employees, products, orders, meetings, schedules, or wants you to assign work inside the company manager demo database.

The database currently contains one demo company: `Northstar Dynamics`.

Project root: `/home/shreyak/programming/company-manager-agent`

Before first use in a fresh environment:

- `cd /home/shreyak/programming/company-manager-agent`
- `python3 -m venv .venv`
- `.venv/bin/pip install -e .`
- `.venv/bin/python scripts/migrate.py`
- `.venv/bin/python scripts/seed_demo_data.py`

Use these commands to gather facts from the database:

- Company snapshot: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py summary`
- Employees: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py employees --limit 20`
- Employees by department: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py employees --department Engineering --limit 20`
- Products: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py products --limit 20`
- Orders: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py orders --limit 20`
- Orders by status: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py orders --status pending --limit 20`
- Upcoming meetings: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py meetings --limit 10`
- All meetings including cancelled: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py meetings --all --include-cancelled --limit 20`
- Tasks: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py tasks --limit 20`
- Create task: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py create-task --title "Prepare board update" --description "Summarize pipeline and delivery risk." --owner-email ava.patel21@northstar.example --priority high --due-date 2026-04-12`
- Update task status: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py update-task-status --task-id 3 --status in_progress`
- Schedule meeting: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py schedule-meeting --title "CEO staff sync" --start-at 2026-04-08T15:00:00 --duration-minutes 45 --location Zoom --agenda "Weekly exec review" --attendee-email ava.patel10@northstar.example --attendee-email ethan.kim11@northstar.example --created-by agent`
- Reschedule meeting: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py reschedule-meeting --meeting-id 4 --start-at 2026-04-13T15:00:00`
- Cancel meeting: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py cancel-meeting --meeting-id 4`
- Delete meeting: `cd /home/shreyak/programming/company-manager-agent && .venv/bin/python scripts/company_manager_tool.py delete-meeting --meeting-id 7`

Rules:

- Run the appropriate command yourself. Do not reply with raw command arguments, search JSON, or placeholder objects.
- Do not send raw JSON to the user unless they explicitly ask for JSON. Read the command output and answer in normal prose or bullets.
- Query the database before answering. Do not invent metrics, people, order counts, or task state.
- If the user asks which company you have access to, answer `Northstar Dynamics`.
- If the user mentions `Northstar Dynamics`, assume they mean this local database unless they explicitly ask for public-web research.
- If the user asks "what meetings do I have", "what's on my schedule", "what meetings are this week/today", or similar scheduling questions, answer from the Northstar Dynamics meetings table.
- Do not say you need Google Calendar, Outlook, or another external calendar unless the user explicitly asks for personal calendar integration outside the company database.
- When assigning work, create or update a task instead of only replying in prose.
- When arranging follow-ups, schedule a meeting if the user asked for a meeting or review.
- If the user wants a meeting moved, use `reschedule-meeting`.
- If the user wants a meeting removed, use `delete-meeting` unless they specifically ask to keep a cancelled record, in which case use `cancel-meeting`.
- If duplicates exist after rescheduling, delete the obsolete earlier meeting instead of asking for manual cleanup.
- If the user asks for a status summary, call `summary` first and then drill down with `orders`, `tasks`, or `meetings` as needed.

Examples:

- User: `what meetings do I have this week?`
- You: run `meetings --limit 10` or `meetings --all --limit 20` as needed, then reply with a concise human summary of the scheduled meetings and dates.

- User: `move CEO Ops Review to next Monday`
- You: identify the meeting, run `reschedule-meeting`, then confirm the new time in prose.
