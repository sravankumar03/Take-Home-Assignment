# Asana Workspace Simulation

Realistic synthetic dataset simulating a B2B SaaS company's Asana workspace for RL environment seed data.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate database
python src/main.py

# Output: output/asana_simulation.sqlite
```

## Configuration

Edit `config.py` to adjust:

```python
NUM_USERS = 500           # Total employees
NUM_TEAMS = 35            # Departments/squads
NUM_PROJECTS = 100        # Active + archived projects
NUM_TASKS = 5000          # Total tasks (scalable to 8000)
HISTORY_MONTHS = 18       # Months of historical data
```

## Project Structure

```
├── README.md                    # This file
├── requirements.txt             # Dependencies (faker)
├── schema.sql                   # SQLite DDL (12 tables)
├── config.py                    # Generation parameters
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── DOCUMENTATION.md             # Full schema & methodology docs
├── src/
│   ├── main.py                  # Entry point / orchestration
│   ├── database.py              # SQLite operations
│   ├── scrapers/                # Data loading modules
│   │   └── data_loader.py       # Loads pre-curated JSON files
│   ├── generators/              # Data generation logic
│   │   ├── organizations.py
│   │   ├── teams.py
│   │   ├── users.py
│   │   ├── team_memberships.py
│   │   ├── projects.py
│   │   ├── sections.py
│   │   ├── tasks.py
│   │   ├── subtasks.py
│   │   ├── comments.py
│   │   ├── custom_fields.py
│   │   └── tags.py
│   ├── models/                  # Data models (dataclasses)
│   │   └── entities.py          # Entity definitions
│   └── utils/                   # Helpers
│       ├── dates.py             # Temporal generation
│       ├── distributions.py     # Statistical helpers
│       └── names.py             # Name generation
├── data/                        # Pre-curated realistic data
│   ├── first_names.json         # Census-based first names
│   └── last_names.json          # Census-based last names
└── output/
    └── asana_simulation.sqlite  # Generated database
```

## Data Realism

| Metric | Value | Source |
|--------|-------|--------|
| Sprint duration | 2 weeks | Parabol 2023 (59% of teams) |
| Team size | 12-17 members | Scrum Guide |
| Task cycle time | Median 3.4 days | Typo Engineering Benchmarks |
| Unassigned tasks | 15% | Asana best practices |
| Overdue tasks | 5% | Realistic estimate |
| Empty descriptions | 20% | Common pattern |

## Database Schema

12 tables covering:
- **Core**: organizations, teams, users, team_memberships
- **Projects**: projects, sections
- **Tasks**: tasks (with subtask support via parent_task_id)
- **Collaboration**: comments
- **Metadata**: custom_field_definitions, custom_field_values, tags, task_tags

See `schema.sql` for complete DDL and `DOCUMENTATION.md` for full methodology.

## Requirements

- Python 3.8+
- SQLite 3 (included with Python)
- See `requirements.txt` for Python packages

## Verify Database

```bash
python check_db.py
```

## License

MIT
