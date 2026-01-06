"""
Custom fields generator.

Creates custom field definitions and values:
- Priority (P0-P3)
- Effort (T-shirt sizing)
- Type (Feature, Bug, Chore, Spike)
- Sprint
- Story Points
"""

import uuid
import random
import json
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.distributions import weighted_choice


# Standard custom field definitions
FIELD_DEFINITIONS = [
    {
        "name": "Priority",
        "field_type": "enum",
        "options": ["P0 - Critical", "P1 - High", "P2 - Medium", "P3 - Low"],
        "distribution": {
            "P0 - Critical": 0.05,
            "P1 - High": 0.20,
            "P2 - Medium": 0.50,
            "P3 - Low": 0.25,
        }
    },
    {
        "name": "Effort",
        "field_type": "enum",
        "options": ["XS", "S", "M", "L", "XL"],
        "distribution": {
            "XS": 0.15,
            "S": 0.30,
            "M": 0.35,
            "L": 0.15,
            "XL": 0.05,
        }
    },
    {
        "name": "Type",
        "field_type": "enum",
        "options": ["Feature", "Bug", "Chore", "Spike"],
        "distribution": {
            "Feature": 0.45,
            "Bug": 0.30,
            "Chore": 0.20,
            "Spike": 0.05,
        }
    },
    {
        "name": "Sprint",
        "field_type": "text",
        "options": None,
        "distribution": None
    },
    {
        "name": "Story Points",
        "field_type": "number",
        "options": None,
        "distribution": {
            1: 0.10,
            2: 0.25,
            3: 0.30,
            5: 0.25,
            8: 0.08,
            13: 0.02,
        }
    },
]


def generate_custom_field_definition(
    name: str,
    field_type: str,
    options: List[str],
    organization_id: str
) -> Dict[str, Any]:
    """Generate a custom field definition record."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "field_type": field_type,
        "options": json.dumps(options) if options else None,
        "organization_id": organization_id,
    }


def generate_custom_field_definitions(organization_id: str) -> List[Dict[str, Any]]:
    """Generate all custom field definitions."""
    definitions = []
    
    for field_def in FIELD_DEFINITIONS:
        definition = generate_custom_field_definition(
            name=field_def["name"],
            field_type=field_def["field_type"],
            options=field_def.get("options"),
            organization_id=organization_id
        )
        # Store distribution for value generation
        definition["_distribution"] = field_def.get("distribution")
        definitions.append(definition)
    
    return definitions


def generate_custom_field_value(
    field_id: str,
    task_id: str,
    value: str
) -> Dict[str, Any]:
    """Generate a custom field value record."""
    return {
        "id": str(uuid.uuid4()),
        "field_id": field_id,
        "task_id": task_id,
        "value": value,
    }


def generate_custom_field_values(
    field_definitions: List[Dict[str, Any]],
    tasks: List[Dict[str, Any]],
    coverage_rate: float = 0.80
) -> List[Dict[str, Any]]:
    """
    Generate custom field values for tasks.
    
    Args:
        field_definitions: Field definition records
        tasks: Task records
        coverage_rate: Percentage of tasks that have each field
    
    Returns:
        List of custom field value records
    """
    values = []
    
    # Only parent tasks get custom fields (not subtasks)
    parent_tasks = [t for t in tasks if t.get("parent_task_id") is None]
    
    for field_def in field_definitions:
        distribution = field_def.get("_distribution")
        field_type = field_def["field_type"]
        
        for task in parent_tasks:
            # Skip some tasks randomly
            if random.random() > coverage_rate:
                continue
            
            # Generate value based on field type
            if field_type == "enum" and distribution:
                value = weighted_choice(distribution)
            elif field_type == "number" and distribution:
                value = str(weighted_choice(distribution))
            elif field_type == "text":
                # Sprint field - generate sprint name
                # Parse task creation date for sprint calculation
                # Simple approach: Sprint N based on week number
                if field_def["name"] == "Sprint":
                    sprint_num = random.randint(1, 26)  # ~6 months of sprints
                    value = f"Sprint {sprint_num}"
                else:
                    value = None
            else:
                value = None
            
            if value:
                field_value = generate_custom_field_value(
                    field_id=field_def["id"],
                    task_id=task["id"],
                    value=value
                )
                values.append(field_value)
    
    return values
