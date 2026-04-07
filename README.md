# company-manager-agent

Proof of concept for an executive-facing OpenClaw assistant backed by a SQLite company database.

## What it includes

- SQLAlchemy models for companies, departments, employees, products, customers, orders, meetings, and tasks
- Dedicated DDL bootstrap script: `scripts/migrate.py`
- Demo data generator: `scripts/seed_demo_data.py`
- Agent-facing JSON CLI for read and write actions: `scripts/company_manager_tool.py`
- OpenClaw skill: `openclaw_skills/company-manager/SKILL.md`

## Setup

```bash
cd /home/shreyak/programming/company-manager-agent
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python scripts/migrate.py
.venv/bin/python scripts/seed_demo_data.py
```

The SQLite database is created at `data/company_manager.db` by default.

## DB tool examples

```bash
.venv/bin/python scripts/company_manager_tool.py summary
.venv/bin/python scripts/company_manager_tool.py employees --department Engineering
.venv/bin/python scripts/company_manager_tool.py orders --status pending
.venv/bin/python scripts/company_manager_tool.py create-task \
  --title "Prepare weekly board summary" \
  --description "Summarize revenue, delivery risk, and hiring bottlenecks." \
  --owner-email ava.patel21@northstar.example \
  --priority high \
  --due-date 2026-04-12
```

## OpenClaw wiring

The custom skill lives in `openclaw_skills/company-manager`. Add that directory to `skills.load.extraDirs` in `~/.openclaw/openclaw.json` so the gateway can discover it without copying files around.

After that, start a new OpenClaw session and ask the agent for:

- company health summaries
- employee or product lookups
- order backlog or meeting schedules
- task assignment and task status updates

## Telegram usage

Your Telegram channel is already configured in OpenClaw. Once the skill is visible and the database is seeded, DM or mention the bot and ask operational questions like:

- "Give me a company snapshot and highlight the biggest delivery risk."
- "Assign a high-priority task to the operations lead to reduce shipment delays."
- "Schedule an exec review tomorrow at 3 PM IST with the CEO and COO."
