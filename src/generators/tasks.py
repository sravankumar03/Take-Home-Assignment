"""
Task generator.

Creates realistic tasks with:
- Department-specific naming patterns
- Due date distribution: 25% week, 40% month, 20% quarter, 10% none, 5% overdue
- Completion rates by project type
- 15% unassigned, 20% no description
- Cycle time based on industry benchmarks
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import (
    format_timestamp, format_date, random_business_date,
    generate_due_date, generate_completion_time
)
from utils.distributions import (
    weighted_choice, biased_boolean, completion_rate_for_project_type,
    distribute_among
)


# Task name templates by department
TASK_TEMPLATES = {
    "Engineering": [
        "Implement {component} {action}",
        "{action} {component} module",
        "Fix: {bug_description}",
        "Refactor {component} for {reason}",
        "Add {feature} to {component}",
        "Update {component} documentation",
        "Write tests for {component}",
        "Debug {component} {issue}",
        "Optimize {component} performance",
        "Review PR: {component} changes",
        "Set up {tool} integration",
        "Migrate {component} to {target}",
        "Add error handling to {component}",
        "Implement {component} caching",
        "Add logging to {component}",
    ],
    "Product": [
        "Draft PRD for {feature}",
        "User research: {topic}",
        "Competitive analysis: {competitor}",
        "Review design mockups for {feature}",
        "Write user stories for {feature}",
        "Define success metrics for {feature}",
        "Prioritize {quarter} backlog",
        "Stakeholder alignment meeting",
        "Update product roadmap",
        "Analyze {metric} data",
    ],
    "Marketing": [
        "Write blog post: {topic}",
        "Create social media content for {campaign}",
        "Design landing page for {campaign}",
        "Set up email automation for {campaign}",
        "Review campaign analytics",
        "Update website copy for {page}",
        "Coordinate with design on {asset}",
        "Schedule social posts for {period}",
        "Create presentation for {event}",
        "Research {topic} trends",
    ],
    "Sales": [
        "Follow up with {company}",
        "Prepare proposal for {company}",
        "Update CRM data for {region}",
        "Create sales deck for {vertical}",
        "Schedule demo with {company}",
        "Review contract for {company}",
        "Competitive positioning for {competitor}",
        "Update territory plan",
        "Prepare for QBR",
        "Train on new product features",
    ],
    "Operations": [
        "Review {process} workflow",
        "Update {document} documentation",
        "Coordinate with vendors on {topic}",
        "Prepare {report} report",
        "Audit {system} access",
        "Process {request} requests",
        "Update {policy} policy",
        "Review budget for {department}",
    ],
    "HR": [
        "Screen candidates for {role}",
        "Schedule interviews for {role}",
        "Update job description: {role}",
        "Prepare onboarding for {name}",
        "Review performance feedback",
        "Coordinate training session",
        "Update employee handbook",
        "Process benefits enrollment",
    ],
}

# Substitution values
COMPONENTS = [
    "auth", "billing", "notifications", "search", "analytics",
    "dashboard", "API", "mobile", "payments", "users", "reports",
    "integrations", "settings", "permissions", "cache", "queue"
]
ACTIONS = ["endpoint", "service", "handler", "controller", "middleware", "validation"]
FEATURES = ["filtering", "sorting", "pagination", "export", "import", "bulk actions"]
BUG_DESCRIPTIONS = [
    "users unable to login after password reset",
    "duplicate entries in export",
    "timezone handling in reports",
    "memory leak in background jobs",
    "race condition in concurrent updates",
    "incorrect calculation in billing",
    "missing validation for edge case",
    "UI not updating after action",
]
REASONS = ["scalability", "maintainability", "performance", "security", "readability"]
ISSUES = ["timeout", "memory usage", "error rate", "latency", "crash"]
TOOLS = ["Datadog", "Sentry", "Slack", "Jira", "GitHub Actions", "Redis"]
TARGETS = ["new architecture", "cloud service", "async processing", "microservice"]
TOPICS = ["AI features", "mobile users", "enterprise needs", "automation", "integrations"]
COMPETITORS = ["Competitor A", "Competitor B", "market leader"]
CAMPAIGNS = ["Q1 launch", "product update", "feature release", "webinar"]
PAGES = ["homepage", "pricing", "features", "about"]
ASSETS = ["banner", "video", "infographic", "case study"]
PERIODS = ["this week", "next sprint", "Q2"]
EVENTS = ["conference", "webinar", "partner meeting"]
COMPANIES = ["Acme Corp", "TechStart", "Enterprise Inc", "Growth Co"]
REGIONS = ["NA", "EMEA", "APAC"]
VERTICALS = ["fintech", "healthcare", "retail", "SaaS"]
PROCESSES = ["onboarding", "procurement", "approval", "reporting"]
DOCUMENTS = ["runbook", "SOP", "policy", "guidelines"]
SYSTEMS = ["AWS", "GCP", "Okta", "Salesforce"]
REQUESTS = ["access", "expense", "vacation", "equipment"]
POLICIES = ["security", "travel", "expense", "remote work"]
DEPARTMENTS = ["engineering", "sales", "marketing", "product"]
ROLES = ["Software Engineer", "Product Manager", "Designer", "Sales Rep"]
NAMES = ["new hire", "team member", "contractor"]
METRICS = ["conversion", "retention", "engagement", "churn"]


def _fill_task_template(template: str) -> str:
    """Fill placeholders in task template."""
    replacements = {
        "{component}": random.choice(COMPONENTS),
        "{action}": random.choice(ACTIONS),
        "{feature}": random.choice(FEATURES),
        "{bug_description}": random.choice(BUG_DESCRIPTIONS),
        "{reason}": random.choice(REASONS),
        "{issue}": random.choice(ISSUES),
        "{tool}": random.choice(TOOLS),
        "{target}": random.choice(TARGETS),
        "{topic}": random.choice(TOPICS),
        "{competitor}": random.choice(COMPETITORS),
        "{campaign}": random.choice(CAMPAIGNS),
        "{page}": random.choice(PAGES),
        "{asset}": random.choice(ASSETS),
        "{period}": random.choice(PERIODS),
        "{event}": random.choice(EVENTS),
        "{company}": random.choice(COMPANIES),
        "{region}": random.choice(REGIONS),
        "{vertical}": random.choice(VERTICALS),
        "{process}": random.choice(PROCESSES),
        "{document}": random.choice(DOCUMENTS),
        "{system}": random.choice(SYSTEMS),
        "{request}": random.choice(REQUESTS),
        "{policy}": random.choice(POLICIES),
        "{department}": random.choice(DEPARTMENTS),
        "{role}": random.choice(ROLES),
        "{name}": random.choice(NAMES),
        "{quarter}": f"Q{random.randint(1, 4)}",
        "{metric}": random.choice(METRICS),
        "{report}": random.choice(["weekly", "monthly", "quarterly"]),
    }
    
    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)
    return result


def _generate_description(name: str, dept: str) -> Optional[str]:
    """Generate task description (20% empty)."""
    if random.random() < 0.20:
        return None
    
    # 50% brief, 30% detailed
    if random.random() < 0.625:  # 50/80 = brief among non-empty
        templates = [
            f"Complete the task: {name}",
            f"Work on {name.lower()} as part of current sprint.",
            f"Priority item for the team.",
            f"Follow up from team discussion.",
            f"Blocked by dependencies - check status before starting.",
        ]
        return random.choice(templates)
    else:
        # Detailed with bullet points
        bullets = [
            "- Review existing implementation",
            "- Update relevant documentation",
            "- Add test coverage",
            "- Get code review approval",
            "- Deploy to staging first",
            "- Monitor for issues after deploy",
            "- Update stakeholders on completion",
        ]
        selected = random.sample(bullets, k=random.randint(2, 4))
        return f"Acceptance criteria:\n" + "\n".join(selected)


def generate_task(
    name: str,
    description: Optional[str],
    project_id: str,
    section_id: str,
    assignee_id: Optional[str],
    created_by_id: str,
    created_at: datetime,
    due_date: Optional[datetime],
    completed: bool,
    completed_at: Optional[datetime],
    position: int,
    parent_task_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a single task record."""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "project_id": project_id,
        "section_id": section_id,
        "assignee_id": assignee_id,
        "created_by_id": created_by_id,
        "parent_task_id": parent_task_id,
        "due_date": format_date(due_date) if due_date else None,
        "created_at": format_timestamp(created_at),
        "completed": 1 if completed else 0,
        "completed_at": format_timestamp(completed_at) if completed_at else None,
        "position": position,
    }


def generate_tasks(
    projects: List[Dict[str, Any]],
    sections: List[Dict[str, Any]],
    team_memberships: List[Dict[str, Any]],
    users: List[Dict[str, Any]],
    num_tasks: int,
    simulation_start: datetime,
    simulation_end: datetime,
    unassigned_rate: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Generate all tasks.
    
    Args:
        projects: Project records
        sections: Section records
        team_memberships: Membership records
        users: User records
        num_tasks: Total tasks to generate
        simulation_start: Start of simulation
        simulation_end: End of simulation (now)
        unassigned_rate: Percentage of unassigned tasks
    
    Returns:
        List of task records (parent tasks only, not subtasks)
    """
    tasks = []
    
    # Build lookups
    project_sections = {}
    for section in sections:
        pid = section["project_id"]
        if pid not in project_sections:
            project_sections[pid] = []
        project_sections[pid].append(section)
    
    # Sort sections by position
    for pid in project_sections:
        project_sections[pid].sort(key=lambda s: s["position"])
    
    # Team members by team
    team_members = {}
    for mem in team_memberships:
        tid = mem["team_id"]
        if tid not in team_members:
            team_members[tid] = []
        team_members[tid].append(mem["user_id"])
    
    # Active users lookup
    active_user_ids = {u["id"] for u in users if u["is_active"]}
    
    # Distribute tasks among projects (power law - some projects have many more)
    project_task_counts = distribute_among(
        total=num_tasks,
        buckets=len(projects),
        min_per_bucket=5
    )
    
    # Shuffle to randomize distribution
    random.shuffle(project_task_counts)
    
    for project, task_count in zip(projects, project_task_counts):
        dept = project.get("department", "Engineering")
        templates = TASK_TEMPLATES.get(dept, TASK_TEMPLATES["Engineering"])
        proj_sections = project_sections.get(project["id"], [])
        
        if not proj_sections:
            continue
        
        # Get team members for this project
        project_team_id = project["team_id"]
        available_assignees = [
            uid for uid in team_members.get(project_team_id, [])
            if uid in active_user_ids
        ]
        
        if not available_assignees:
            available_assignees = list(active_user_ids)[:10]  # Fallback
        
        # Project creation date
        project_created = datetime.strptime(project["created_at"], "%Y-%m-%d %H:%M:%S")
        
        # Determine completion rate based on project type/status
        if project["status"] == "completed" or project["archived"]:
            completion_rate = random.uniform(0.80, 0.95)
        else:
            completion_rate = completion_rate_for_project_type(
                "sprint" if "Sprint" in project["name"] else "ongoing"
            )
        
        # Section weights (more tasks in later stages means more completed)
        num_sections = len(proj_sections)
        
        for i in range(task_count):
            # Generate task name
            template = random.choice(templates)
            name = _fill_task_template(template)
            
            # Generate description
            description = _generate_description(name, dept)
            
            # Task creation date
            created_at = random_business_date(
                max(project_created, simulation_start),
                simulation_end - timedelta(hours=1)
            )
            
            # Determine if completed
            completed = biased_boolean(completion_rate)
            
            # Determine section based on completion status
            if completed:
                # Completed tasks go to last section
                section = proj_sections[-1]
            else:
                # Distribute among other sections (weighted toward earlier)
                non_done_sections = proj_sections[:-1] if len(proj_sections) > 1 else proj_sections
                weights = [1.0 / (idx + 1) for idx in range(len(non_done_sections))]
                section = random.choices(non_done_sections, weights=weights, k=1)[0]
            
            # Completion time
            completed_at = None
            if completed:
                completed_at = generate_completion_time(created_at, simulation_end)
            
            # Due date
            due_date = generate_due_date(created_at, now=simulation_end)
            
            # Assignee (15% unassigned)
            if biased_boolean(unassigned_rate):
                assignee_id = None
            else:
                assignee_id = random.choice(available_assignees)
            
            # Creator (usually assignee or team lead)
            if assignee_id and random.random() < 0.7:
                created_by_id = assignee_id
            else:
                created_by_id = random.choice(available_assignees)
            
            task = generate_task(
                name=name,
                description=description,
                project_id=project["id"],
                section_id=section["id"],
                assignee_id=assignee_id,
                created_by_id=created_by_id,
                created_at=created_at,
                due_date=due_date,
                completed=completed,
                completed_at=completed_at,
                position=i
            )
            tasks.append(task)
    
    return tasks
