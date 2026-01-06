"""
Configuration for Asana Workspace Simulation

Adjust these parameters to control the scale and characteristics
of the generated dataset.
"""

import os
from datetime import datetime, timedelta

# =============================================================================
# SCALE PARAMETERS
# =============================================================================

# Organization
ORGANIZATION_NAME = "Cloudvance Technologies"
ORGANIZATION_DOMAIN = "cloudvance.com"

# User counts
NUM_USERS = 500                    # Total employees (range: 500-10000)
INACTIVE_USER_RATE = 0.05          # 5% turnover/deactivated accounts

# Team structure
NUM_TEAMS = 35                     # Number of teams (range: 30-40)
MIN_TEAM_SIZE = 8                  # Minimum members per team
MAX_TEAM_SIZE = 20                 # Maximum members per team

# Projects
NUM_PROJECTS = 100                 # Total projects
ARCHIVED_PROJECT_RATE = 0.30       # 30% of old projects archived

# Tasks
NUM_TASKS = 5000                   # Total tasks (scalable to 8000)
SUBTASK_RATE = 0.25                # 25% of tasks have subtasks
AVG_SUBTASKS_PER_TASK = 3          # Average subtasks when present

# Comments
AVG_COMMENTS_PER_TASK = 2.5        # Average comments per task

# =============================================================================
# TEMPORAL PARAMETERS
# =============================================================================

# History window
HISTORY_MONTHS = 18                # Months of data to generate
SIMULATION_END = datetime.now()
SIMULATION_START = SIMULATION_END - timedelta(days=HISTORY_MONTHS * 30)

# Organization founding (slightly before history start)
ORG_CREATED_AT = SIMULATION_START - timedelta(days=180)

# =============================================================================
# DISTRIBUTION PARAMETERS (Research-Based)
# =============================================================================

# Department distribution (percentages)
DEPARTMENT_DISTRIBUTION = {
    "Engineering": 0.40,           # 40% of teams
    "Product": 0.15,               # 15%
    "Marketing": 0.15,             # 15%
    "Sales": 0.15,                 # 15%
    "Operations": 0.10,            # 10%
    "HR": 0.05,                    # 5%
}

# User role distribution
ROLE_DISTRIBUTION = {
    "junior": 0.40,                # 40% junior
    "mid": 0.35,                   # 35% mid-level
    "senior": 0.20,                # 20% senior
    "lead": 0.05,                  # 5% leads
}

# Task assignment distribution
UNASSIGNED_TASK_RATE = 0.15        # 15% of tasks unassigned
EMPTY_DESCRIPTION_RATE = 0.20      # 20% of tasks have no description

# Due date distribution
DUE_DATE_DISTRIBUTION = {
    "within_week": 0.25,           # 25% due within 1 week
    "within_month": 0.40,          # 40% due within 1 month
    "within_quarter": 0.20,        # 20% due 1-3 months out
    "no_date": 0.10,               # 10% no due date
    "overdue": 0.05,               # 5% overdue
}

# Completion rates by project type
COMPLETION_RATES = {
    "sprint": (0.70, 0.85),        # Sprint projects: 70-85%
    "ongoing": (0.40, 0.50),       # Ongoing projects: 40-50%
    "campaign": (0.60, 0.75),      # Marketing campaigns: 60-75%
}

# Cycle time (days from creation to completion)
CYCLE_TIME_PARAMS = {
    "elite": (1, 2, 0.15),         # 1-2 days, 15% of tasks
    "good": (2, 4, 0.40),          # 2-4 days, 40%
    "median": (4, 7, 0.30),        # 4-7 days, 30%
    "slow": (7, 14, 0.12),         # 7-14 days, 12%
    "very_slow": (14, 30, 0.03),   # 14+ days, 3%
}

# Comment distribution per task
COMMENT_DISTRIBUTION = {
    0: 0.30,                       # 30% have 0 comments
    (1, 3): 0.40,                  # 40% have 1-3 comments
    (4, 10): 0.20,                 # 20% have 4-10 comments
    (10, 25): 0.10,                # 10% have 10+ comments (discussions)
}

# =============================================================================
# CUSTOM FIELDS
# =============================================================================

CUSTOM_FIELDS = [
    {"name": "Priority", "type": "enum", "options": ["P0 - Critical", "P1 - High", "P2 - Medium", "P3 - Low"]},
    {"name": "Effort", "type": "enum", "options": ["XS", "S", "M", "L", "XL"]},
    {"name": "Type", "type": "enum", "options": ["Feature", "Bug", "Chore", "Spike"]},
    {"name": "Sprint", "type": "text", "options": None},
    {"name": "Story Points", "type": "number", "options": None},
]

# Priority distribution
PRIORITY_DISTRIBUTION = {
    "P0 - Critical": 0.05,         # 5% critical
    "P1 - High": 0.20,             # 20% high
    "P2 - Medium": 0.50,           # 50% medium
    "P3 - Low": 0.25,              # 25% low
}

# =============================================================================
# TAGS
# =============================================================================

TAGS = [
    {"name": "bug", "color": "#E53935"},
    {"name": "feature", "color": "#43A047"},
    {"name": "blocked", "color": "#FB8C00"},
    {"name": "needs-review", "color": "#8E24AA"},
    {"name": "p0", "color": "#D32F2F"},
    {"name": "tech-debt", "color": "#757575"},
    {"name": "documentation", "color": "#1E88E5"},
    {"name": "security", "color": "#C62828"},
    {"name": "performance", "color": "#00ACC1"},
    {"name": "ux", "color": "#7B1FA2"},
]

# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
DATABASE_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(OUTPUT_DIR, "asana_simulation.sqlite")
)

# Random seed for reproducibility (optional)
RANDOM_SEED = int(os.environ.get("RANDOM_SEED", 42))
