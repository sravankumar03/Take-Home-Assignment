"""
Section generator.

Creates Kanban-style sections for projects:
- Engineering: Backlog, To Do, In Progress, In Review, Done
- Marketing: Planning, In Progress, Review, Published
- Default: To Do, In Progress, Done
"""

import uuid
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Section templates by project type/department
SECTION_TEMPLATES = {
    "Engineering": [
        "Backlog", "To Do", "In Progress", "In Review", "Done"
    ],
    "Product": [
        "Discovery", "Definition", "Design", "In Development", "Shipped"
    ],
    "Marketing": [
        "Ideas", "Planning", "In Progress", "Review", "Published"
    ],
    "Sales": [
        "Pipeline", "Qualified", "In Progress", "Closing", "Won/Lost"
    ],
    "Operations": [
        "Backlog", "This Week", "In Progress", "Done"
    ],
    "HR": [
        "To Do", "In Progress", "Pending Approval", "Complete"
    ],
    "default": [
        "To Do", "In Progress", "Done"
    ],
}


def generate_section(
    name: str,
    project_id: str,
    position: int
) -> Dict[str, Any]:
    """Generate a single section record."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "project_id": project_id,
        "position": position,
    }


def generate_sections(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate sections for all projects.
    
    Args:
        projects: List of project records (with 'department' field)
    
    Returns:
        List of section records
    """
    sections = []
    
    for project in projects:
        dept = project.get("department", "default")
        section_names = SECTION_TEMPLATES.get(dept, SECTION_TEMPLATES["default"])
        
        for position, name in enumerate(section_names):
            section = generate_section(
                name=name,
                project_id=project["id"],
                position=position
            )
            sections.append(section)
    
    return sections


def get_sections_for_project(project_id: str, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get all sections for a project, ordered by position."""
    project_sections = [s for s in sections if s["project_id"] == project_id]
    return sorted(project_sections, key=lambda s: s["position"])


def get_done_section(project_id: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get the 'done' section for a project (last section)."""
    project_sections = get_sections_for_project(project_id, sections)
    return project_sections[-1] if project_sections else None


def get_backlog_section(project_id: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get the first section (backlog/to-do) for a project."""
    project_sections = get_sections_for_project(project_id, sections)
    return project_sections[0] if project_sections else None
