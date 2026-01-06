"""
Data loader for pre-curated JSON files.

Loads realistic data from JSON files for:
- Names (census-based)
- Task templates
- Project templates
- Comment templates

Falls back to built-in defaults if files don't exist.
"""

import os
import json
from typing import List, Dict, Any, Optional

# Base directory for data files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")


def _load_json_file(filename: str) -> Optional[Any]:
    """Load JSON file from data directory."""
    filepath = os.path.join(DATA_DIR, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_first_names() -> List[Dict[str, Any]]:
    """
    Load first names with weights from census data.
    
    Returns list of {"name": str, "weight": float}
    """
    data = _load_json_file("first_names.json")
    if data:
        return data
    
    # Built-in fallback (subset of census data)
    return [
        {"name": "James", "weight": 3.318}, {"name": "Michael", "weight": 4.350},
        {"name": "Robert", "weight": 3.143}, {"name": "David", "weight": 3.611},
        {"name": "John", "weight": 3.271}, {"name": "William", "weight": 3.614},
        {"name": "Mary", "weight": 2.629}, {"name": "Jennifer", "weight": 1.468},
        {"name": "Elizabeth", "weight": 1.629}, {"name": "Sarah", "weight": 0.998},
        {"name": "Emily", "weight": 0.844}, {"name": "Jessica", "weight": 1.045},
        {"name": "Priya", "weight": 0.400}, {"name": "Wei", "weight": 0.380},
        {"name": "Mohammed", "weight": 0.480}, {"name": "Carlos", "weight": 0.450},
    ]


def load_last_names() -> List[Dict[str, Any]]:
    """
    Load last names with weights from census data.
    
    Returns list of {"name": str, "weight": float}
    """
    data = _load_json_file("last_names.json")
    if data:
        return data
    
    # Built-in fallback
    return [
        {"name": "Smith", "weight": 2.376}, {"name": "Johnson", "weight": 1.935},
        {"name": "Williams", "weight": 1.635}, {"name": "Brown", "weight": 1.437},
        {"name": "Garcia", "weight": 1.166}, {"name": "Miller", "weight": 1.161},
        {"name": "Davis", "weight": 1.116}, {"name": "Rodriguez", "weight": 1.094},
        {"name": "Patel", "weight": 0.520}, {"name": "Kim", "weight": 0.480},
        {"name": "Chen", "weight": 0.450}, {"name": "Singh", "weight": 0.380},
        {"name": "Nguyen", "weight": 0.476}, {"name": "Lee", "weight": 0.693},
    ]


def load_task_templates() -> Dict[str, List[str]]:
    """
    Load task name templates by department.
    
    Returns dict mapping department to list of template strings.
    """
    data = _load_json_file("task_templates.json")
    if data:
        return data
    
    # Built-in fallback
    return {
        "Engineering": [
            "Implement {component} service",
            "Fix: {bug_description}",
            "Refactor {component} module",
        ],
        "Marketing": [
            "Write blog post about {topic}",
            "Create social content for {campaign}",
        ],
        "Product": [
            "User research: {feature}",
            "Write PRD for {feature}",
        ],
    }


def load_project_templates() -> Dict[str, List[str]]:
    """
    Load project name templates by department.
    """
    data = _load_json_file("project_templates.json")
    if data:
        return data
    
    return {
        "Engineering": [
            "Q{quarter} Platform Sprint",
            "API v{version} Development",
        ],
        "Marketing": [
            "Q{quarter} Campaign",
            "Product Launch: {feature}",
        ],
    }


def load_comment_templates() -> Dict[str, List[str]]:
    """
    Load comment templates by type.
    """
    data = _load_json_file("comment_templates.json")
    if data:
        return data
    
    return {
        "status": [
            "Making progress on this.",
            "Almost done!",
        ],
        "question": [
            "Can someone clarify this?",
            "What's the priority here?",
        ],
    }
