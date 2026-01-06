"""
Project generator.

Creates realistic projects with:
- Department-appropriate project types
- 60% have due dates (clustered on quarter ends)
- 30% of old projects archived
- Status distribution: active (60%), paused (10%), completed (30%)
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import format_timestamp, random_date_between, format_date
from utils.distributions import weighted_choice, biased_boolean


# Project name templates by department
PROJECT_TEMPLATES = {
    "Engineering": [
        "Q{quarter} Platform Improvements", "API v{version} Development",
        "Performance Optimization Sprint", "Security Audit Remediation",
        "Mobile App {feature} Feature", "Infrastructure Migration",
        "Tech Debt Reduction", "Developer Experience Improvements",
        "Monitoring & Observability", "CI/CD Pipeline Enhancement",
        "Database Optimization", "Microservices Refactoring",
        "{component} Service Rewrite", "Load Testing Initiative",
        "Error Handling Improvements", "Logging Infrastructure",
    ],
    "Product": [
        "Q{quarter} Roadmap Execution", "User Research: {feature}",
        "Feature Discovery: {area}", "Product Analytics Dashboard",
        "Competitive Analysis", "Beta Program: {feature}",
        "Customer Feedback Integration", "Product Requirements: {area}",
        "UX Improvement Initiative", "Onboarding Flow Redesign",
    ],
    "Marketing": [
        "Q{quarter} Campaign Planning", "{event} Event Launch",
        "Content Calendar Q{quarter}", "Brand Refresh Initiative",
        "Lead Generation Campaign", "Product Launch: {feature}",
        "SEO Optimization", "Social Media Strategy",
        "Email Marketing Automation", "Partner Marketing Program",
        "Customer Case Studies", "Webinar Series",
    ],
    "Sales": [
        "Q{quarter} Sales Targets", "Enterprise Deal Pipeline",
        "Sales Enablement Materials", "CRM Data Cleanup",
        "Territory Planning Q{quarter}", "Competitive Battlecards",
        "Customer Success Playbook", "Upsell Campaign",
        "Partner Channel Development", "Sales Training Program",
    ],
    "Operations": [
        "Q{quarter} OKR Planning", "Process Automation Initiative",
        "Vendor Review & Consolidation", "Budget Planning FY{year}",
        "Compliance Audit Prep", "Office Expansion Planning",
        "IT Security Review", "Business Continuity Planning",
    ],
    "HR": [
        "Q{quarter} Hiring Plan", "Employee Engagement Survey",
        "Performance Review Cycle", "Training & Development Program",
        "Culture Initiative", "Benefits Review",
        "Onboarding Program Redesign", "Diversity & Inclusion Goals",
    ],
}

# Components for template substitution
FEATURES = ["Analytics", "Reporting", "Notifications", "Integrations", "Dashboard", "API", "Mobile"]
AREAS = ["Enterprise", "SMB", "Growth", "Retention", "Activation", "Monetization"]
COMPONENTS = ["Auth", "Billing", "Notifications", "Search", "Analytics", "Core"]
EVENTS = ["Summit", "Conference", "Webinar", "Launch", "Workshop"]


def _fill_template(template: str, quarter: int, year: int) -> str:
    """Fill in template placeholders."""
    result = template
    result = result.replace("{quarter}", str(quarter))
    result = result.replace("{year}", str(year))
    result = result.replace("{version}", str(random.randint(2, 5)))
    result = result.replace("{feature}", random.choice(FEATURES))
    result = result.replace("{area}", random.choice(AREAS))
    result = result.replace("{component}", random.choice(COMPONENTS))
    result = result.replace("{event}", random.choice(EVENTS))
    return result


def generate_project(
    name: str,
    team_id: str,
    owner_id: str,
    created_at: datetime,
    due_date: datetime = None,
    status: str = "active",
    archived: bool = False
) -> Dict[str, Any]:
    """Generate a single project record."""
    # Generate description based on name
    description = f"Project focused on {name.lower()}. "
    description += random.choice([
        "Key initiative for this quarter.",
        "Cross-functional collaboration required.",
        "High priority for leadership.",
        "Part of our strategic roadmap.",
        "Customer-facing improvements.",
    ])
    
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "team_id": team_id,
        "owner_id": owner_id,
        "status": status,
        "created_at": format_timestamp(created_at),
        "due_date": format_date(due_date) if due_date else None,
        "archived": 1 if archived else 0,
    }


def generate_projects(
    teams: List[Dict[str, Any]],
    team_memberships: List[Dict[str, Any]],
    users: List[Dict[str, Any]],
    num_projects: int,
    simulation_start: datetime,
    simulation_end: datetime
) -> List[Dict[str, Any]]:
    """
    Generate all projects.
    
    Args:
        teams: List of team records
        team_memberships: List of membership records
        users: List of user records
        num_projects: Total projects to generate
        simulation_start: Start of simulation period
        simulation_end: End of simulation period
    
    Returns:
        List of project records
    """
    projects = []
    used_names = set()
    
    # Build lookup for team leads
    team_leads = {}
    for team in teams:
        leads = [
            m["user_id"] for m in team_memberships
            if m["team_id"] == team["id"] and m["role"] == "lead"
        ]
        if not leads:
            # Fall back to any team member
            leads = [m["user_id"] for m in team_memberships if m["team_id"] == team["id"]]
        team_leads[team["id"]] = leads
    
    # Senior users for project ownership
    senior_user_ids = {u["id"] for u in users if u["role"] in ("senior", "lead") and u["is_active"]}
    
    # Distribute projects among teams (weighted by team size)
    team_sizes = {
        t["id"]: len([m for m in team_memberships if m["team_id"] == t["id"]])
        for t in teams
    }
    total_size = sum(team_sizes.values()) or 1
    
    for team in teams:
        dept = team.get("department", "Engineering")
        templates = PROJECT_TEMPLATES.get(dept, PROJECT_TEMPLATES["Engineering"])
        
        # Calculate projects for this team
        team_weight = team_sizes[team["id"]] / total_size
        team_project_count = max(1, int(num_projects * team_weight))
        
        team_created = datetime.strptime(team["created_at"], "%Y-%m-%d %H:%M:%S")
        
        for _ in range(team_project_count):
            if len(projects) >= num_projects:
                break
            
            # Pick a template and generate name
            template = random.choice(templates)
            
            # Determine quarter based on random date
            created_at = random_date_between(
                max(team_created, simulation_start),
                simulation_end - timedelta(days=7)
            )
            quarter = (created_at.month - 1) // 3 + 1
            year = created_at.year
            
            name = _fill_template(template, quarter, year)
            
            # Ensure unique name
            base_name = name
            counter = 1
            while name in used_names:
                name = f"{base_name} ({counter})"
                counter += 1
            used_names.add(name)
            
            # Select owner (prefer team leads, fall back to senior users)
            possible_owners = [
                uid for uid in team_leads.get(team["id"], [])
                if uid in senior_user_ids
            ]
            if not possible_owners:
                possible_owners = team_leads.get(team["id"], [])
            if not possible_owners:
                possible_owners = list(senior_user_ids)
            
            owner_id = random.choice(possible_owners) if possible_owners else users[0]["id"]
            
            # Determine due date (60% have dates, clustered on quarter ends)
            due_date = None
            if random.random() < 0.60:
                # Quarter end dates
                quarter_ends = [
                    datetime(year, 3, 31),
                    datetime(year, 6, 30),
                    datetime(year, 9, 30),
                    datetime(year, 12, 31),
                ]
                # Pick a future quarter end
                future_ends = [d for d in quarter_ends if d > created_at]
                if future_ends:
                    due_date = random.choice(future_ends[:2])  # Within 2 quarters
                else:
                    due_date = created_at + timedelta(days=random.randint(30, 90))
            
            # Determine status and archived
            age_days = (simulation_end - created_at).days
            
            if age_days > 180:  # Older than 6 months
                archived = biased_boolean(0.30)  # 30% archived
                status = random.choices(
                    ["active", "paused", "completed"],
                    weights=[0.20, 0.10, 0.70]  # Older projects more likely completed
                )[0]
            else:
                archived = False
                status = random.choices(
                    ["active", "paused", "completed"],
                    weights=[0.70, 0.10, 0.20]
                )[0]
            
            project = generate_project(
                name=name,
                team_id=team["id"],
                owner_id=owner_id,
                created_at=created_at,
                due_date=due_date,
                status=status,
                archived=archived
            )
            project["department"] = dept  # Store for generating tasks
            projects.append(project)
    
    return projects[:num_projects]
