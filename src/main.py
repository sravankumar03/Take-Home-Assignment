"""
Main orchestration script for Asana simulation.

Generates a complete SQLite database with realistic data.

Usage:
    python src/main.py
"""

import os
import sys
import random
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Import database
from database import Database

# Import generators
from generators import (
    generate_organizations,
    generate_teams,
    generate_users,
    generate_team_memberships,
    generate_projects,
    generate_sections,
    generate_tasks,
    generate_subtasks,
    generate_comments,
    generate_custom_field_definitions,
    generate_custom_field_values,
    generate_tags,
    generate_task_tags,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main generation pipeline."""
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("Asana Workspace Simulation - Data Generation")
    logger.info("=" * 60)
    
    # Set random seed for reproducibility
    random.seed(config.RANDOM_SEED)
    logger.info(f"Random seed: {config.RANDOM_SEED}")
    
    # Ensure output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Initialize database
    logger.info(f"Database path: {config.DATABASE_PATH}")
    db = Database(config.DATABASE_PATH, config.SCHEMA_PATH)
    
    # Clear existing database
    db.clear_database()
    
    # Initialize schema
    db.initialize_schema()
    
    # =========================================================================
    # PHASE 1: Core Entities
    # =========================================================================
    logger.info("\n--- Phase 1: Core Entities ---")
    
    # Generate organization
    logger.info("Generating organization...")
    organizations = generate_organizations(config)
    db.insert_many("organizations", organizations)
    org_id = organizations[0]["id"]
    
    # Generate teams
    logger.info(f"Generating {config.NUM_TEAMS} teams...")
    teams = generate_teams(
        organization_id=org_id,
        num_teams=config.NUM_TEAMS,
        org_created_at=config.ORG_CREATED_AT,
        department_distribution=config.DEPARTMENT_DISTRIBUTION
    )
    # Remove department field before insert (not in schema)
    teams_for_db = [{k: v for k, v in t.items() if k != "department"} for t in teams]
    db.insert_many("teams", teams_for_db)
    
    # Generate users
    logger.info(f"Generating {config.NUM_USERS} users...")
    users = generate_users(
        num_users=config.NUM_USERS,
        domain=config.ORGANIZATION_DOMAIN,
        org_created_at=config.ORG_CREATED_AT,
        simulation_end=config.SIMULATION_END,
        role_distribution=config.ROLE_DISTRIBUTION,
        department_distribution=config.DEPARTMENT_DISTRIBUTION,
        inactive_rate=config.INACTIVE_USER_RATE
    )
    db.insert_many("users", users)
    
    # Generate team memberships
    logger.info("Generating team memberships...")
    memberships = generate_team_memberships(
        teams=teams,
        users=users,
        min_team_size=config.MIN_TEAM_SIZE,
        max_team_size=config.MAX_TEAM_SIZE
    )
    db.insert_many("team_memberships", memberships)
    
    # =========================================================================
    # PHASE 2: Projects & Sections
    # =========================================================================
    logger.info("\n--- Phase 2: Projects & Sections ---")
    
    # Generate projects
    logger.info(f"Generating {config.NUM_PROJECTS} projects...")
    projects = generate_projects(
        teams=teams,
        team_memberships=memberships,
        users=users,
        num_projects=config.NUM_PROJECTS,
        simulation_start=config.SIMULATION_START,
        simulation_end=config.SIMULATION_END
    )
    # Remove department field before insert
    projects_for_db = [{k: v for k, v in p.items() if k != "department"} for p in projects]
    db.insert_many("projects", projects_for_db)
    
    # Generate sections
    logger.info("Generating sections...")
    sections = generate_sections(projects)
    db.insert_many("sections", sections)
    
    # =========================================================================
    # PHASE 3: Tasks & Subtasks
    # =========================================================================
    logger.info("\n--- Phase 3: Tasks & Subtasks ---")
    
    # Generate tasks
    logger.info(f"Generating {config.NUM_TASKS} tasks...")
    tasks = generate_tasks(
        projects=projects,
        sections=sections,
        team_memberships=memberships,
        users=users,
        num_tasks=config.NUM_TASKS,
        simulation_start=config.SIMULATION_START,
        simulation_end=config.SIMULATION_END,
        unassigned_rate=config.UNASSIGNED_TASK_RATE
    )
    db.insert_many("tasks", tasks)
    
    # Generate subtasks
    logger.info("Generating subtasks...")
    subtasks = generate_subtasks(
        tasks=tasks,
        subtask_rate=config.SUBTASK_RATE,
        simulation_end=config.SIMULATION_END
    )
    db.insert_many("tasks", subtasks)  # Same table as tasks
    
    # Combine for comments/tags
    all_tasks = tasks + subtasks
    
    # =========================================================================
    # PHASE 4: Collaboration
    # =========================================================================
    logger.info("\n--- Phase 4: Collaboration ---")
    
    # Generate comments
    logger.info("Generating comments...")
    comments = generate_comments(
        tasks=all_tasks,
        team_memberships=memberships,
        users=users,
        simulation_end=config.SIMULATION_END
    )
    db.insert_many("comments", comments)
    
    # =========================================================================
    # PHASE 5: Metadata
    # =========================================================================
    logger.info("\n--- Phase 5: Metadata ---")
    
    # Generate custom field definitions
    logger.info("Generating custom fields...")
    field_definitions = generate_custom_field_definitions(org_id)
    # Remove _distribution field before insert
    field_defs_for_db = [{k: v for k, v in f.items() if not k.startswith("_")} for f in field_definitions]
    db.insert_many("custom_field_definitions", field_defs_for_db)
    
    # Generate custom field values
    field_values = generate_custom_field_values(
        field_definitions=field_definitions,
        tasks=tasks  # Only parent tasks
    )
    db.insert_many("custom_field_values", field_values)
    
    # Generate tags
    logger.info("Generating tags...")
    tags = generate_tags(org_id)
    db.insert_many("tags", tags)
    
    # Generate task-tag associations
    task_tags = generate_task_tags(tasks=tasks, tags=tags)
    db.insert_many("task_tags", task_tags)
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    logger.info("\n--- Validation ---")
    
    # Get stats
    stats = db.get_stats()
    logger.info("Table row counts:")
    for table, count in stats.items():
        logger.info(f"  {table}: {count:,}")
    
    # Validate integrity
    issues = db.validate_integrity()
    if issues:
        logger.warning("Integrity issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("No integrity issues found!")
    
    # Close database
    db.close()
    
    # Summary
    elapsed = datetime.now() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("Generation Complete!")
    logger.info(f"Time elapsed: {elapsed}")
    logger.info(f"Database: {config.DATABASE_PATH}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
