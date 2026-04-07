# company-manager-agent

Executive-facing company operations assistant built on OpenClaw, Telegram, SQLAlchemy, and SQLite.

This project is a proof of concept for a CEO or senior operator who wants to ask natural-language questions like:

- "Give me a company snapshot and highlight the biggest delivery risk."
- "What meetings do I have this week?"
- "Assign a high-priority task to the operations lead."
- "Move CEO Ops Review to next Monday."

The assistant answers from a local company database, writes operational changes back to that database, and is exposed through OpenClaw so it can be used from Telegram.

## What this project demonstrates

- End-to-end executive chat workflow from Telegram to OpenClaw to a live SQLite company database
- Read operations for company health, employees, products, orders, meetings, and tasks
- Write operations for task creation, task status updates, meeting creation, meeting rescheduling, meeting cancellation, and meeting deletion
- A custom OpenClaw skill that teaches the agent how to answer operational questions from the local company dataset
- A deterministic SQLAlchemy-backed data layer that can be seeded for repeatable demos

## Architecture

```text
Telegram
  -> OpenClaw Gateway
    -> company-manager skill
      -> Python CLI
        -> SQLAlchemy
          -> SQLite
```

Core pieces:

- `company_manager/models.py`
  Defines the data model for companies, departments, employees, products, customers, orders, meetings, meeting attendees, and tasks.
- `company_manager/tooling.py`
  Implements the query and mutation layer used by the agent-facing CLI.
- `scripts/company_manager_tool.py`
  Exposes operational read and write commands in a simple CLI that returns structured JSON.
- `scripts/migrate.py`
  Creates the initial schema and applies lightweight schema updates needed for local evolution.
- `scripts/seed_demo_data.py`
  Seeds a demo company, `Northstar Dynamics`, with realistic sample operating data.
- `openclaw_skills/company-manager/SKILL.md`
  Teaches OpenClaw when and how to use the local company manager tooling.

## Current capabilities

### Read visibility

- Company summary:
  employee count, product count, order count, open orders, active tasks, booked revenue, task breakdown
- Employees:
  browse people by department, title, email, and location
- Products:
  catalog, SKU, category, price, inventory
- Orders:
  recent orders, filtered orders by status, line items, customer, order totals
- Meetings:
  upcoming or full meeting schedule, attendees, agendas, status
- Tasks:
  task owner, priority, status, due dates, descriptions

### Write actions

- Create tasks
- Update task status
- Schedule meetings
- Reschedule meetings
- Cancel meetings
- Delete meetings
- Clean up duplicate operational meetings directly from the assistant workflow

## Demo dataset

The seeded database contains one demo company:

- `Northstar Dynamics`

The sample data includes:

- 5 departments
- 23 employees
- 6 products
- 18 customers
- 36 orders
- multiple executive and operating meetings
- live tasks across sales, engineering, operations, and customer success

Database location:

- `data/company_manager.db`

## Setup

```bash
cd /home/shreyak/programming/company-manager-agent
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python scripts/migrate.py
.venv/bin/python scripts/seed_demo_data.py
```

## Local CLI usage

### Read commands

```bash
.venv/bin/python scripts/company_manager_tool.py summary
.venv/bin/python scripts/company_manager_tool.py employees --department Engineering --limit 10
.venv/bin/python scripts/company_manager_tool.py products --limit 10
.venv/bin/python scripts/company_manager_tool.py orders --status pending --limit 10
.venv/bin/python scripts/company_manager_tool.py meetings --limit 10
.venv/bin/python scripts/company_manager_tool.py meetings --all --include-cancelled --limit 20
.venv/bin/python scripts/company_manager_tool.py tasks --limit 10
```

### Write commands

```bash
.venv/bin/python scripts/company_manager_tool.py create-task \
  --title "Prepare weekly board summary" \
  --description "Summarize revenue, delivery risk, and hiring bottlenecks." \
  --owner-email ethan.johnson40@northstar.example \
  --priority high \
  --due-date 2026-04-12

.venv/bin/python scripts/company_manager_tool.py update-task-status \
  --task-id 5 \
  --status in_progress

.venv/bin/python scripts/company_manager_tool.py schedule-meeting \
  --title "CEO Ops Review" \
  --start-at 2026-04-13T15:00:00 \
  --duration-minutes 45 \
  --location Zoom \
  --agenda "Review shipping backlog and assigned actions." \
  --attendee-email ethan.johnson40@northstar.example \
  --created-by agent

.venv/bin/python scripts/company_manager_tool.py reschedule-meeting \
  --meeting-id 8 \
  --start-at 2026-04-14T15:00:00

.venv/bin/python scripts/company_manager_tool.py cancel-meeting --meeting-id 8
.venv/bin/python scripts/company_manager_tool.py delete-meeting --meeting-id 8
```

## OpenClaw integration

The OpenClaw skill for this project lives here:

- `openclaw_skills/company-manager/SKILL.md`

OpenClaw needs that folder added to `skills.load.extraDirs` in `~/.openclaw/openclaw.json`.

Example:

```json
{
  "skills": {
    "load": {
      "extraDirs": [
        "/home/shreyak/programming/company-manager-agent/openclaw_skills"
      ]
    }
  }
}
```

You can verify discovery with:

```bash
openclaw skills info company-manager
```

## Telegram workflow

Once OpenClaw is running and Telegram is configured, the assistant can be used from chat as a company manager bot.

Example prompts:

- "Give me a company snapshot and highlight the biggest delivery risk."
- "What meetings do I have this week?"
- "Assign a high-priority task to Ethan Johnson to reduce shipment delays."
- "Move CEO Ops Review to next Monday."
- "Delete the earlier duplicate CEO Ops Review meeting."
- "Show me pending orders and the largest backlog risk."

## Example operating loop

1. Executive asks a question in Telegram.
2. OpenClaw receives the message and routes it to the main agent.
3. The `company-manager` skill instructs the agent to use the local Python CLI.
4. The CLI reads or writes the SQLite database through SQLAlchemy.
5. The assistant returns a human-readable answer or confirmation back to Telegram.

This gives you a narrow but real closed loop:

- conversational input
- operational database reads
- operational database writes
- human-readable output in chat

## Project status

This is a working proof of concept, not a finished production system.

What is solid today:

- local data model
- repeatable seeding
- read and write operations
- OpenClaw skill loading
- Telegram-facing demo workflow

What is intentionally simplified:

- SQLite instead of Postgres
- one demo company instead of multi-tenant isolation
- no auth or RBAC around business actions
- no audit UI beyond DB state and OpenClaw session logs
- no external ERP, CRM, HRIS, or calendar sync yet

## Recommended next steps

- Move from SQLite to Postgres
- Add explicit action audit logs
- Add richer analytics queries for revenue, delays, and operating KPIs
- Add role-aware permissions for CEO, COO, VP, and manager actions
- Add connectors for real calendar, CRM, ERP, and ticketing systems
- Expose direct command-dispatch for common scheduling flows to reduce LLM ambiguity further

## License

MIT
