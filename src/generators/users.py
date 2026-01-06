"""
User generator.

Creates realistic user profiles with:
- Census-based name distributions
- Role distribution: junior (40%), mid (35%), senior (20%), lead (5%)
- Staggered hiring dates (growth curve)
- 5% inactive/deactivated accounts
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import format_timestamp, generate_staggered_dates
from utils.names import generate_unique_names, generate_unique_emails
from utils.distributions import weighted_choice, biased_boolean


def generate_user(
    name: str,
    email: str,
    role: str,
    department: str,
    created_at: datetime,
    is_active: bool = True
) -> Dict[str, Any]:
    """Generate a single user record."""
    return {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": name,
        "role": role,
        "department": department,
        "is_active": 1 if is_active else 0,
        "created_at": format_timestamp(created_at),
    }


def generate_users(
    num_users: int,
    domain: str,
    org_created_at: datetime,
    simulation_end: datetime,
    role_distribution: Dict[str, float],
    department_distribution: Dict[str, float],
    inactive_rate: float = 0.05
) -> List[Dict[str, Any]]:
    """
    Generate all users for the organization.
    
    Args:
        num_users: Total number of users
        domain: Email domain (e.g., "cloudvance.com")
        org_created_at: Organization founding date
        simulation_end: End of simulation period
        role_distribution: Dict mapping role to percentage
        department_distribution: Dict mapping department to percentage
        inactive_rate: Percentage of inactive users (turnover)
    
    Returns:
        List of user records
    """
    # Generate unique names
    names = generate_unique_names(num_users)
    emails = generate_unique_emails(names, domain)
    
    # Generate hire dates with growth curve (more recent hires)
    hire_dates = generate_staggered_dates(
        start=org_created_at + timedelta(days=1),
        end=simulation_end - timedelta(days=30),  # Leave room for recent activity
        count=num_users,
        distribution="growth"
    )
    
    # Prepare departments list weighted by distribution
    departments = list(department_distribution.keys())
    dept_weights = list(department_distribution.values())
    
    users = []
    
    for i, (name, email, hire_date) in enumerate(zip(names, emails, hire_dates)):
        # Assign role based on distribution
        role = weighted_choice(role_distribution)
        
        # Assign department based on distribution
        department = random.choices(departments, weights=dept_weights, k=1)[0]
        
        # Determine if active (newer users more likely active)
        # Older users have higher chance of being inactive (turnover)
        days_employed = (simulation_end - hire_date).days
        if days_employed > 365:
            is_active = not biased_boolean(inactive_rate * 1.5)  # Higher turnover for long-term
        else:
            is_active = not biased_boolean(inactive_rate * 0.5)  # Lower turnover for new hires
        
        user = generate_user(
            name=name,
            email=email,
            role=role,
            department=department,
            created_at=hire_date,
            is_active=is_active
        )
        users.append(user)
    
    return users


def get_users_by_department(users: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group users by department."""
    by_dept = {}
    for user in users:
        dept = user["department"]
        if dept not in by_dept:
            by_dept[dept] = []
        by_dept[dept].append(user)
    return by_dept


def get_active_users(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter to only active users."""
    return [u for u in users if u["is_active"]]


def get_senior_users(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get users with senior or lead roles."""
    return [u for u in users if u["role"] in ("senior", "lead")]
