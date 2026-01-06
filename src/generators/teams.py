"""
Team generator.

Creates teams/departments with realistic distribution:
- Engineering: 40%
- Product: 15%
- Marketing: 15%
- Sales: 15%
- Operations: 10%
- HR: 5%
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import format_timestamp, random_date_between


# Team name templates by department
TEAM_TEMPLATES = {
    "Engineering": [
        "Platform Engineering", "Backend Services", "Frontend Team",
        "Mobile Development", "DevOps", "Infrastructure", "API Team",
        "Data Engineering", "Security Engineering", "QA Engineering",
        "Site Reliability", "Core Services", "Developer Experience",
        "Cloud Platform", "ML Engineering", "Integrations Team",
    ],
    "Product": [
        "Product Core", "Growth Product", "Enterprise Product",
        "Mobile Product", "Platform Product", "Analytics Product",
        "UX Research", "Product Operations",
    ],
    "Marketing": [
        "Brand Marketing", "Content Marketing", "Growth Marketing",
        "Product Marketing", "Demand Generation", "Marketing Operations",
        "Events Team", "Social Media",
    ],
    "Sales": [
        "Enterprise Sales", "Mid-Market Sales", "SMB Sales",
        "Sales Development", "Solutions Engineering", "Sales Operations",
        "Customer Success", "Account Management",
    ],
    "Operations": [
        "Business Operations", "Finance", "Legal", "IT Operations",
        "Procurement", "Facilities",
    ],
    "HR": [
        "People Operations", "Talent Acquisition", "Learning & Development",
        "HR Business Partners",
    ],
}

# Team descriptions by department
TEAM_DESCRIPTIONS = {
    "Engineering": "Responsible for building and maintaining {focus} systems and infrastructure.",
    "Product": "Drives product strategy, roadmap, and feature development for {focus}.",
    "Marketing": "Leads {focus} initiatives to drive brand awareness and customer acquisition.",
    "Sales": "Manages {focus} customer relationships and revenue generation.",
    "Operations": "Oversees {focus} processes and organizational efficiency.",
    "HR": "Supports {focus} initiatives for employee experience and organizational development.",
}


def generate_team(
    name: str,
    department: str,
    organization_id: str,
    created_at: datetime
) -> Dict[str, Any]:
    """Generate a single team record."""
    # Generate description
    focus = name.replace(department, "").strip()
    if not focus:
        focus = "core"
    description = TEAM_DESCRIPTIONS.get(department, "Team focused on {focus}.").format(focus=focus.lower())
    
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "organization_id": organization_id,
        "created_at": format_timestamp(created_at),
    }


def generate_teams(
    organization_id: str,
    num_teams: int,
    org_created_at: datetime,
    department_distribution: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Generate all teams for the organization.
    
    Args:
        organization_id: Parent organization ID
        num_teams: Total number of teams to generate
        org_created_at: Organization founding date
        department_distribution: Dict mapping department to percentage
    
    Returns:
        List of team records
    """
    teams = []
    used_names = set()
    
    # Calculate teams per department
    departments = list(department_distribution.keys())
    weights = list(department_distribution.values())
    
    # Normalize weights
    total_weight = sum(weights)
    team_counts = {
        dept: max(1, int(num_teams * (weight / total_weight)))
        for dept, weight in zip(departments, weights)
    }
    
    # Adjust to match exact count
    current_total = sum(team_counts.values())
    while current_total < num_teams:
        # Add to random department
        dept = random.choice(departments)
        team_counts[dept] += 1
        current_total += 1
    while current_total > num_teams:
        # Remove from largest department
        max_dept = max(team_counts, key=team_counts.get)
        if team_counts[max_dept] > 1:
            team_counts[max_dept] -= 1
            current_total -= 1
        else:
            break
    
    # Generate teams for each department
    # Teams are created within the first 6 months of org founding
    team_creation_window = org_created_at + timedelta(days=180)
    
    for department, count in team_counts.items():
        available_names = [n for n in TEAM_TEMPLATES.get(department, []) if n not in used_names]
        
        for i in range(count):
            # Pick a name
            if available_names:
                name = available_names.pop(random.randint(0, len(available_names) - 1))
            else:
                # Generate a unique name
                name = f"{department} Team {i + 1}"
                while name in used_names:
                    name = f"{department} Team {random.randint(1, 100)}"
            
            used_names.add(name)
            
            # Random creation date within window
            created_at = random_date_between(
                org_created_at + timedelta(days=1),
                team_creation_window
            )
            
            team = generate_team(
                name=name,
                department=department,
                organization_id=organization_id,
                created_at=created_at
            )
            team["department"] = department  # Store for later use
            teams.append(team)
    
    return teams
