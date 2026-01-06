"""
Team membership generator.

Creates user-team associations with:
- Each user belongs to 1-3 teams (primary + cross-functional)
- Team leads are senior/lead role users
- Membership dates after both user and team creation
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import format_timestamp, random_date_between
from utils.distributions import distribute_among


def generate_team_membership(
    team_id: str,
    user_id: str,
    role: str,
    joined_at: datetime
) -> Dict[str, Any]:
    """Generate a single team membership record."""
    return {
        "id": str(uuid.uuid4()),
        "team_id": team_id,
        "user_id": user_id,
        "role": role,  # 'member' or 'lead'
        "joined_at": format_timestamp(joined_at),
    }


def generate_team_memberships(
    teams: List[Dict[str, Any]],
    users: List[Dict[str, Any]],
    min_team_size: int = 8,
    max_team_size: int = 20
) -> List[Dict[str, Any]]:
    """
    Generate team memberships.
    
    Strategy:
    1. Assign each user to a primary team based on department
    2. Some users (20%) join 1-2 additional cross-functional teams
    3. Each team gets 1-2 leads from senior/lead users
    
    Args:
        teams: List of team records
        users: List of user records
        min_team_size: Minimum members per team
        max_team_size: Maximum members per team
    
    Returns:
        List of team membership records
    """
    memberships = []
    user_team_count = {u["id"]: 0 for u in users}
    team_members = {t["id"]: [] for t in teams}
    
    # Group teams by department
    teams_by_dept = {}
    for team in teams:
        dept = team.get("department", "Engineering")
        if dept not in teams_by_dept:
            teams_by_dept[dept] = []
        teams_by_dept[dept].append(team)
    
    # Group users by department
    users_by_dept = {}
    for user in users:
        dept = user["department"]
        if dept not in users_by_dept:
            users_by_dept[dept] = []
        users_by_dept[dept].append(user)
    
    # Get senior users for lead assignments
    senior_users = {u["id"]: u for u in users if u["role"] in ("senior", "lead")}
    
    # Step 1: Primary team assignment - ensure each user has at least one team
    for dept, dept_users in users_by_dept.items():
        dept_teams = teams_by_dept.get(dept, [])
        
        if not dept_teams:
            # Fall back to any team if no department match
            dept_teams = teams
        
        # Distribute users among department teams
        team_sizes = distribute_among(
            total=len(dept_users),
            buckets=len(dept_teams),
            min_per_bucket=min(min_team_size, len(dept_users) // len(dept_teams)) if dept_teams else 0
        )
        
        user_idx = 0
        for team, size in zip(dept_teams, team_sizes):
            for _ in range(size):
                if user_idx >= len(dept_users):
                    break
                
                user = dept_users[user_idx]
                user_idx += 1
                
                # Calculate join date (after both team and user creation)
                team_created = datetime.strptime(team["created_at"], "%Y-%m-%d %H:%M:%S")
                user_created = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
                join_start = max(team_created, user_created)
                join_end = join_start + timedelta(days=30)  # Join within 30 days
                joined_at = random_date_between(join_start, join_end)
                
                # Determine membership role
                is_lead = (
                    user["id"] in senior_users and
                    len([m for m in team_members[team["id"]] if m["role"] == "lead"]) < 2 and
                    random.random() < 0.3
                )
                
                membership = generate_team_membership(
                    team_id=team["id"],
                    user_id=user["id"],
                    role="lead" if is_lead else "member",
                    joined_at=joined_at
                )
                
                memberships.append(membership)
                team_members[team["id"]].append(membership)
                user_team_count[user["id"]] += 1
    
    # Step 2: Cross-functional assignments (20% of users join additional teams)
    active_users = [u for u in users if u["is_active"]]
    cross_functional_users = random.sample(
        active_users,
        k=min(len(active_users), int(len(active_users) * 0.2))
    )
    
    for user in cross_functional_users:
        if user_team_count[user["id"]] >= 3:
            continue
        
        # Pick 1-2 additional teams from other departments
        other_teams = [
            t for t in teams
            if t["id"] not in [m["team_id"] for m in memberships if m["user_id"] == user["id"]]
        ]
        
        if not other_teams:
            continue
        
        extra_teams = random.sample(other_teams, k=min(len(other_teams), random.randint(1, 2)))
        
        for team in extra_teams:
            team_created = datetime.strptime(team["created_at"], "%Y-%m-%d %H:%M:%S")
            user_created = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
            join_start = max(team_created, user_created)
            join_end = join_start + timedelta(days=90)  # More flexibility for cross-functional
            joined_at = random_date_between(join_start, join_end)
            
            membership = generate_team_membership(
                team_id=team["id"],
                user_id=user["id"],
                role="member",
                joined_at=joined_at
            )
            
            memberships.append(membership)
            user_team_count[user["id"]] += 1
    
    # Step 3: Ensure each team has at least one lead
    for team in teams:
        team_mems = [m for m in memberships if m["team_id"] == team["id"]]
        has_lead = any(m["role"] == "lead" for m in team_mems)
        
        if not has_lead and team_mems:
            # Find a senior member or promote someone
            for mem in team_mems:
                user = next((u for u in users if u["id"] == mem["user_id"]), None)
                if user and user["role"] in ("senior", "lead"):
                    mem["role"] = "lead"
                    break
            else:
                # Just promote the first member
                team_mems[0]["role"] = "lead"
    
    return memberships


def get_team_member_ids(team_id: str, memberships: List[Dict[str, Any]]) -> List[str]:
    """Get all user IDs for a team."""
    return [m["user_id"] for m in memberships if m["team_id"] == team_id]


def get_team_leads(team_id: str, memberships: List[Dict[str, Any]]) -> List[str]:
    """Get lead user IDs for a team."""
    return [m["user_id"] for m in memberships if m["team_id"] == team_id and m["role"] == "lead"]
