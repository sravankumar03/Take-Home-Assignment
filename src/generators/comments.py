"""
Comment generator.

Creates realistic comments/stories on tasks:
- 30% tasks: 0 comments
- 40% tasks: 1-3 comments
- 20% tasks: 4-10 comments
- 10% tasks: 10+ comments (active discussions)
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import format_timestamp, random_date_between
from utils.distributions import comment_count_for_task


# Comment templates by type
COMMENT_TEMPLATES = {
    "status_update": [
        "Started working on this.",
        "Making progress, should be done by end of day.",
        "Completed the first part, moving to the next step.",
        "Running into some issues, will update soon.",
        "Done with my part, passing to review.",
        "Pushed the changes, ready for review.",
        "This is taking longer than expected.",
        "Almost done, just finishing up tests.",
        "Deployed to staging for testing.",
        "All done! Moving to complete.",
    ],
    "question": [
        "Can someone clarify the requirements here?",
        "Should this follow the new or old pattern?",
        "Do we have designs for this?",
        "What's the priority on this?",
        "Is this blocked by anything?",
        "Who should review this?",
        "When do we need this by?",
        "Are there any edge cases to consider?",
        "Should I coordinate with another team?",
        "What's the expected behavior here?",
    ],
    "blocker": [
        "Blocked: waiting on API changes from backend team.",
        "Blocked: need access to production logs.",
        "Blocked: dependency not released yet.",
        "Blocked: waiting on design review.",
        "Blocked: need clarification from product.",
        "Blocked: CI is failing on main branch.",
        "Can't proceed until the migration is complete.",
        "Need someone to unblock the PR.",
    ],
    "feedback": [
        "Looks good to me!",
        "LGTM, approved.",
        "Left some comments on the PR.",
        "Nice work on this!",
        "A few minor suggestions, otherwise good.",
        "Thanks for picking this up.",
        "Great progress!",
        "This is exactly what we needed.",
    ],
    "technical": [
        "Make sure to handle the null case.",
        "Consider using the new caching layer.",
        "Don't forget to update the documentation.",
        "We should add metrics for this.",
        "Remember to add error handling.",
        "This might affect performance, let's monitor.",
        "Check the edge cases around timezone handling.",
        "The tests should cover the error scenarios.",
    ],
    "reference": [
        "Related to the discussion in #channel.",
        "See the design doc for more context.",
        "This is part of the larger initiative.",
        "Follow up from our sync meeting.",
        "Context: this was requested by customer X.",
        "Reference: linked Jira ticket has more details.",
    ],
}


def generate_comment(
    task_id: str,
    author_id: str,
    text: str,
    created_at: datetime
) -> Dict[str, Any]:
    """Generate a single comment record."""
    return {
        "id": str(uuid.uuid4()),
        "task_id": task_id,
        "author_id": author_id,
        "text": text,
        "created_at": format_timestamp(created_at),
    }


def generate_comments(
    tasks: List[Dict[str, Any]],
    team_memberships: List[Dict[str, Any]],
    users: List[Dict[str, Any]],
    simulation_end: datetime = None
) -> List[Dict[str, Any]]:
    """
    Generate comments for all tasks.
    
    Args:
        tasks: Task records
        team_memberships: Membership records for finding commenters
        users: User records
        simulation_end: End of simulation
    
    Returns:
        List of comment records
    """
    if simulation_end is None:
        simulation_end = datetime.now()
    
    comments = []
    
    # Build team member lookup
    team_members = {}
    for mem in team_memberships:
        tid = mem["team_id"]
        if tid not in team_members:
            team_members[tid] = []
        team_members[tid].append(mem["user_id"])
    
    # Project to team lookup (we need this from projects data)
    # For simplicity, we'll use task assignee/creator as potential commenters
    
    active_user_ids = [u["id"] for u in users if u["is_active"]]
    
    for task in tasks:
        # Determine number of comments
        num_comments = comment_count_for_task()
        
        if num_comments == 0:
            continue
        
        # Parse task dates
        task_created = datetime.strptime(task["created_at"], "%Y-%m-%d %H:%M:%S")
        
        if task["completed_at"]:
            task_end = datetime.strptime(task["completed_at"], "%Y-%m-%d %H:%M:%S")
        else:
            task_end = simulation_end
        
        # Potential commenters (prioritize assignee and creator)
        potential_authors = []
        if task["assignee_id"]:
            potential_authors.append(task["assignee_id"])
        if task["created_by_id"]:
            potential_authors.append(task["created_by_id"])
        
        # Add some random team members
        potential_authors.extend(random.sample(
            active_user_ids,
            k=min(5, len(active_user_ids))
        ))
        
        # Generate comments
        for i in range(num_comments):
            # Pick comment type (status updates more common)
            comment_type = random.choices(
                list(COMMENT_TEMPLATES.keys()),
                weights=[0.35, 0.20, 0.10, 0.15, 0.15, 0.05],
                k=1
            )[0]
            
            text = random.choice(COMMENT_TEMPLATES[comment_type])
            
            # Pick author (weight toward assignee)
            if potential_authors:
                if task["assignee_id"] and random.random() < 0.5:
                    author_id = task["assignee_id"]
                else:
                    author_id = random.choice(potential_authors)
            else:
                author_id = random.choice(active_user_ids)
            
            # Comment time (distributed between task creation and end)
            # Earlier comments more likely
            progress = (i + 1) / (num_comments + 1)
            comment_window_start = task_created
            comment_window_end = task_created + (task_end - task_created) * min(1.0, progress + 0.2)
            
            created_at = random_date_between(comment_window_start, comment_window_end)
            
            comment = generate_comment(
                task_id=task["id"],
                author_id=author_id,
                text=text,
                created_at=created_at
            )
            comments.append(comment)
    
    return comments
