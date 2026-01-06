"""
Tag generator.

Creates tags and task-tag associations.
Tags are cross-project labels for categorization.
"""

import uuid
import random
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.distributions import biased_boolean


# Predefined tags with colors (Asana color palette)
PREDEFINED_TAGS = [
    {"name": "bug", "color": "#E53935"},
    {"name": "feature", "color": "#43A047"},
    {"name": "enhancement", "color": "#1E88E5"},
    {"name": "blocked", "color": "#FB8C00"},
    {"name": "needs-review", "color": "#8E24AA"},
    {"name": "p0", "color": "#D32F2F"},
    {"name": "p1", "color": "#F57C00"},
    {"name": "tech-debt", "color": "#757575"},
    {"name": "documentation", "color": "#0288D1"},
    {"name": "security", "color": "#C62828"},
    {"name": "performance", "color": "#00ACC1"},
    {"name": "ux", "color": "#7B1FA2"},
    {"name": "mobile", "color": "#5E35B1"},
    {"name": "api", "color": "#00897B"},
    {"name": "infrastructure", "color": "#6D4C41"},
    {"name": "testing", "color": "#FDD835"},
    {"name": "breaking-change", "color": "#E91E63"},
    {"name": "wontfix", "color": "#9E9E9E"},
    {"name": "duplicate", "color": "#BDBDBD"},
    {"name": "good-first-issue", "color": "#4CAF50"},
]


def generate_tag(
    name: str,
    color: str,
    organization_id: str
) -> Dict[str, Any]:
    """Generate a tag record."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "color": color,
        "organization_id": organization_id,
    }


def generate_tags(organization_id: str) -> List[Dict[str, Any]]:
    """Generate all tags for the organization."""
    tags = []
    
    for tag_def in PREDEFINED_TAGS:
        tag = generate_tag(
            name=tag_def["name"],
            color=tag_def["color"],
            organization_id=organization_id
        )
        tags.append(tag)
    
    return tags


def generate_task_tag(task_id: str, tag_id: str) -> Dict[str, Any]:
    """Generate a task-tag association record."""
    return {
        "task_id": task_id,
        "tag_id": tag_id,
    }


def generate_task_tags(
    tasks: List[Dict[str, Any]],
    tags: List[Dict[str, Any]],
    tag_rate: float = 0.40
) -> List[Dict[str, Any]]:
    """
    Generate task-tag associations.
    
    Args:
        tasks: Task records
        tags: Tag records
        tag_rate: Percentage of tasks that have at least one tag
    
    Returns:
        List of task-tag association records
    """
    task_tags = []
    
    # Build tag lookup by name for smart assignment
    tag_by_name = {t["name"]: t for t in tags}
    
    # Only parent tasks get tags (not subtasks)
    parent_tasks = [t for t in tasks if t.get("parent_task_id") is None]
    
    for task in parent_tasks:
        if not biased_boolean(tag_rate):
            continue
        
        task_name_lower = task["name"].lower()
        assigned_tags = set()
        
        # Smart tag assignment based on task name
        if "fix" in task_name_lower or "bug" in task_name_lower:
            if "bug" in tag_by_name:
                assigned_tags.add(tag_by_name["bug"]["id"])
        
        if "feature" in task_name_lower or "implement" in task_name_lower:
            if "feature" in tag_by_name:
                assigned_tags.add(tag_by_name["feature"]["id"])
        
        if "refactor" in task_name_lower:
            if "tech-debt" in tag_by_name:
                assigned_tags.add(tag_by_name["tech-debt"]["id"])
        
        if "document" in task_name_lower:
            if "documentation" in tag_by_name:
                assigned_tags.add(tag_by_name["documentation"]["id"])
        
        if "test" in task_name_lower:
            if "testing" in tag_by_name:
                assigned_tags.add(tag_by_name["testing"]["id"])
        
        if "security" in task_name_lower:
            if "security" in tag_by_name:
                assigned_tags.add(tag_by_name["security"]["id"])
        
        if "performance" in task_name_lower or "optimize" in task_name_lower:
            if "performance" in tag_by_name:
                assigned_tags.add(tag_by_name["performance"]["id"])
        
        if "mobile" in task_name_lower:
            if "mobile" in tag_by_name:
                assigned_tags.add(tag_by_name["mobile"]["id"])
        
        if "api" in task_name_lower:
            if "api" in tag_by_name:
                assigned_tags.add(tag_by_name["api"]["id"])
        
        # Add 0-2 random additional tags
        if random.random() < 0.3:
            additional = random.sample(tags, k=min(len(tags), random.randint(1, 2)))
            for tag in additional:
                assigned_tags.add(tag["id"])
        
        # Create task-tag records
        for tag_id in assigned_tags:
            task_tag = generate_task_tag(task["id"], tag_id)
            task_tags.append(task_tag)
    
    return task_tags
