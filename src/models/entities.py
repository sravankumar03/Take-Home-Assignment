"""
Data model entities for Asana simulation.

These dataclasses represent the core entities in the Asana workspace.
They provide type safety and documentation for the data structures.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime, date


@dataclass
class Organization:
    """Top-level workspace container."""
    id: str
    name: str
    created_at: datetime


@dataclass
class Team:
    """Department or squad within the organization."""
    id: str
    name: str
    organization_id: str
    created_at: datetime
    description: Optional[str] = None


@dataclass
class User:
    """Employee in the workspace."""
    id: str
    email: str
    name: str
    role: str  # junior | mid | senior | lead
    department: str
    created_at: datetime
    is_active: bool = True


@dataclass
class TeamMembership:
    """User-team association."""
    id: str
    team_id: str
    user_id: str
    joined_at: datetime
    role: str = "member"  # member | lead


@dataclass
class Project:
    """Collection of tasks organized around a goal."""
    id: str
    name: str
    team_id: str
    owner_id: str
    created_at: datetime
    description: Optional[str] = None
    status: str = "active"  # active | paused | completed
    due_date: Optional[date] = None
    archived: bool = False


@dataclass
class Section:
    """Kanban column or sprint subdivision within a project."""
    id: str
    name: str
    project_id: str
    position: int


@dataclass
class Task:
    """The fundamental unit of work."""
    id: str
    name: str
    project_id: str
    section_id: str
    created_by_id: str
    created_at: datetime
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    parent_task_id: Optional[str] = None  # NULL = task, set = subtask
    due_date: Optional[date] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    position: int = 0


@dataclass
class Comment:
    """Discussion or activity on a task."""
    id: str
    task_id: str
    author_id: str
    text: str
    created_at: datetime


@dataclass
class CustomFieldDefinition:
    """Schema for a custom field."""
    id: str
    name: str
    field_type: str  # enum | number | text | date
    organization_id: str
    options: Optional[str] = None  # JSON for enum options


@dataclass
class CustomFieldValue:
    """Value of a custom field on a task."""
    id: str
    field_id: str
    task_id: str
    value: Optional[str] = None


@dataclass
class Tag:
    """Cross-project label."""
    id: str
    name: str
    color: str
    organization_id: str


@dataclass
class TaskTag:
    """Task-tag association."""
    task_id: str
    tag_id: str
