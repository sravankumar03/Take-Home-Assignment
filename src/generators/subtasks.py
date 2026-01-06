"""
Subtask generator.

Generates subtasks for a portion of parent tasks.
Subtasks are stored in the same `tasks` table with `parent_task_id` set.

Distribution:
- 25% of tasks have subtasks
- When present: 50% have 2-3, 30% have 4-5, 20% have 6-10 subtasks
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import format_timestamp, format_date, random_date_between
from utils.distributions import subtask_count_for_task, biased_boolean


# Subtask name patterns (action-oriented, shorter than parent tasks)
SUBTASK_PATTERNS = [
    "Research {topic}",
    "Draft initial version",
    "Review with team",
    "Implement changes",
    "Write tests",
    "Update documentation",
    "Get approval",
    "Deploy to staging",
    "QA verification",
    "Final review",
    "Merge PR",
    "Update status",
    "Notify stakeholders",
    "Create follow-up tasks",
    "Schedule meeting",
    "Gather requirements",
    "Design solution",
    "Code review",
    "Performance testing",
    "Security review",
]


def generate_subtask(
    parent_task: Dict[str, Any],
    name: str,
    position: int,
    created_at: datetime,
    completed: bool,
    completed_at: datetime = None
) -> Dict[str, Any]:
    """Generate a subtask record."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": None,  # Subtasks typically don't have descriptions
        "project_id": parent_task["project_id"],
        "section_id": parent_task["section_id"],
        "assignee_id": parent_task["assignee_id"],  # Inherit from parent
        "created_by_id": parent_task["created_by_id"],
        "parent_task_id": parent_task["id"],
        "due_date": parent_task["due_date"],  # Inherit from parent
        "created_at": format_timestamp(created_at),
        "completed": 1 if completed else 0,
        "completed_at": format_timestamp(completed_at) if completed_at else None,
        "position": position,
    }


def generate_subtasks(
    tasks: List[Dict[str, Any]],
    subtask_rate: float = 0.25,
    simulation_end: datetime = None
) -> List[Dict[str, Any]]:
    """
    Generate subtasks for a portion of tasks.
    
    Args:
        tasks: Parent task records
        subtask_rate: Percentage of tasks that have subtasks
        simulation_end: End of simulation period
    
    Returns:
        List of subtask records (same schema as tasks)
    """
    if simulation_end is None:
        simulation_end = datetime.now()
    
    subtasks = []
    
    # Only consider parent tasks (not already subtasks)
    parent_tasks = [t for t in tasks if t.get("parent_task_id") is None]
    
    # Select tasks that will have subtasks
    tasks_with_subtasks = [
        t for t in parent_tasks
        if biased_boolean(subtask_rate)
    ]
    
    for parent in tasks_with_subtasks:
        # Determine number of subtasks
        num_subtasks = subtask_count_for_task()
        
        # Parse parent creation time
        parent_created = datetime.strptime(parent["created_at"], "%Y-%m-%d %H:%M:%S")
        parent_completed = parent["completed"]
        parent_completed_at = None
        if parent["completed_at"]:
            parent_completed_at = datetime.strptime(parent["completed_at"], "%Y-%m-%d %H:%M:%S")
        
        # Generate subtasks
        used_names = set()
        
        for i in range(num_subtasks):
            # Pick a unique name
            name = random.choice(SUBTASK_PATTERNS)
            attempt = 0
            while name in used_names and attempt < 10:
                name = random.choice(SUBTASK_PATTERNS)
                # Add variety
                if "{topic}" in name:
                    name = name.replace("{topic}", random.choice([
                        "options", "requirements", "alternatives", "dependencies"
                    ]))
                attempt += 1
            used_names.add(name)
            
            # Subtask creation is after parent, staggered
            subtask_created = random_date_between(
                parent_created,
                parent_created + timedelta(days=2)
            )
            
            # Subtask completion follows parent
            if parent_completed:
                # If parent is completed, most subtasks should be completed
                # Earlier subtasks more likely completed
                subtask_completed = biased_boolean(0.90 - (i * 0.05))
                
                if subtask_completed and parent_completed_at:
                    # Complete before parent
                    subtask_completed_at = random_date_between(
                        subtask_created,
                        parent_completed_at
                    )
                else:
                    subtask_completed_at = None
                    subtask_completed = False
            else:
                # Parent not completed - some subtasks may be done
                subtask_completed = biased_boolean(0.3 + (i * 0.1))  # Earlier more likely done
                if subtask_completed:
                    subtask_completed_at = random_date_between(
                        subtask_created,
                        simulation_end
                    )
                else:
                    subtask_completed_at = None
            
            subtask = generate_subtask(
                parent_task=parent,
                name=name,
                position=i,
                created_at=subtask_created,
                completed=subtask_completed,
                completed_at=subtask_completed_at
            )
            subtasks.append(subtask)
    
    return subtasks
