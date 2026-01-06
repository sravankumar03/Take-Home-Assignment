"""
Organization generator.

Creates the top-level organization/workspace entity.
In this simulation, we model a single B2B SaaS company.
"""

import uuid
from datetime import datetime
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dates import format_timestamp


def generate_organization(
    name: str,
    created_at: datetime
) -> Dict[str, Any]:
    """
    Generate the organization record.
    
    Args:
        name: Organization name (from config)
        created_at: Organization founding date
    
    Returns:
        Dict with organization data
    """
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "created_at": format_timestamp(created_at),
    }


def generate_organizations(config) -> list:
    """
    Generate organization(s) based on config.
    
    For this simulation, we create a single organization.
    """
    org = generate_organization(
        name=config.ORGANIZATION_NAME,
        created_at=config.ORG_CREATED_AT,
    )
    return [org]
