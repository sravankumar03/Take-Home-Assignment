"""
Date and timestamp utilities for temporal data generation.

Ensures temporal consistency:
- org.created_at < team.created_at < user.created_at
- task.created_at < task.completed_at
- task.completed_at <= NOW()
"""

import random
from datetime import datetime, timedelta, date
from typing import Optional, Tuple


def random_date_between(start: datetime, end: datetime) -> datetime:
    """Generate a random datetime between start and end (inclusive)."""
    if start >= end:
        return start
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def random_business_date(start: datetime, end: datetime) -> datetime:
    """
    Generate a random datetime weighted toward business hours.
    
    Distribution:
    - 85% weekdays (Mon-Fri)
    - 15% weekends
    - 80% during 9am-6pm
    - 20% outside business hours
    """
    result = random_date_between(start, end)
    
    # Retry up to 10 times to get a weekday (85% target)
    attempts = 0
    while attempts < 10 and random.random() < 0.85:
        if result.weekday() < 5:  # Monday = 0, Friday = 4
            break
        result = random_date_between(start, end)
        attempts += 1
    
    # Adjust time to business hours (80% of the time)
    if random.random() < 0.80:
        hour = random.randint(9, 17)  # 9am to 5pm
        minute = random.randint(0, 59)
        result = result.replace(hour=hour, minute=minute)
    
    return result


def generate_due_date(
    created_at: datetime,
    distribution: str = "default",
    now: Optional[datetime] = None
) -> Optional[date]:
    """
    Generate a realistic due date based on creation date.
    
    Distribution (research-based):
    - 25% within 1 week
    - 40% within 1 month
    - 20% 1-3 months out
    - 10% no due date (returns None)
    - 5% overdue (past due date)
    """
    if now is None:
        now = datetime.now()
    
    roll = random.random()
    
    if roll < 0.10:  # 10% no due date
        return None
    elif roll < 0.15:  # 5% overdue (due date in the past relative to now)
        days_overdue = random.randint(1, 14)
        due = now - timedelta(days=days_overdue)
        # Ensure due date is after created_at
        if due.date() <= created_at.date():
            due = created_at + timedelta(days=1)
        return due.date()
    elif roll < 0.40:  # 25% within 1 week
        days = random.randint(1, 7)
        return (created_at + timedelta(days=days)).date()
    elif roll < 0.80:  # 40% within 1 month
        days = random.randint(8, 30)
        return (created_at + timedelta(days=days)).date()
    else:  # 20% within 1-3 months
        days = random.randint(31, 90)
        return (created_at + timedelta(days=days)).date()


def generate_completion_time(
    created_at: datetime,
    now: Optional[datetime] = None
) -> datetime:
    """
    Generate realistic task completion time using cycle time distribution.
    
    Distribution (from Typo Engineering Benchmarks):
    - 15% "elite": 1-2 days
    - 40% "good": 2-4 days
    - 30% "median": 4-7 days
    - 12% "slow": 7-14 days
    - 3% "very slow": 14-30 days
    """
    if now is None:
        now = datetime.now()
    
    roll = random.random()
    
    if roll < 0.15:
        days = random.uniform(1, 2)
    elif roll < 0.55:
        days = random.uniform(2, 4)
    elif roll < 0.85:
        days = random.uniform(4, 7)
    elif roll < 0.97:
        days = random.uniform(7, 14)
    else:
        days = random.uniform(14, 30)
    
    completed_at = created_at + timedelta(days=days)
    
    # Ensure completed_at doesn't exceed now
    if completed_at > now:
        completed_at = now - timedelta(hours=random.randint(1, 24))
    
    # Ensure completed_at is after created_at
    if completed_at <= created_at:
        completed_at = created_at + timedelta(hours=random.randint(1, 48))
    
    return completed_at


def generate_staggered_dates(
    start: datetime,
    end: datetime,
    count: int,
    distribution: str = "uniform"
) -> list:
    """
    Generate a list of dates distributed over a time range.
    
    Distributions:
    - "uniform": Evenly distributed
    - "growth": More dates toward the end (simulates hiring growth)
    - "bursts": Clustered around certain points (sprint starts)
    """
    dates = []
    
    if distribution == "uniform":
        for _ in range(count):
            dates.append(random_date_between(start, end))
    
    elif distribution == "growth":
        # Use exponential distribution - more recent dates are more likely
        for _ in range(count):
            # Bias toward end of range
            progress = random.random() ** 0.5  # Square root biases toward 1
            delta = (end - start) * progress
            dates.append(start + delta)
    
    elif distribution == "bursts":
        # Create burst points (e.g., sprint starts every 2 weeks)
        burst_interval = timedelta(days=14)
        current = start
        burst_points = []
        while current < end:
            burst_points.append(current)
            current += burst_interval
        
        # Distribute dates around burst points
        for _ in range(count):
            burst = random.choice(burst_points)
            # Add some noise (±3 days)
            noise = timedelta(days=random.gauss(0, 1.5))
            date = burst + noise
            # Clamp to range
            date = max(start, min(end, date))
            dates.append(date)
    
    return sorted(dates)


def days_since(dt: datetime, reference: Optional[datetime] = None) -> int:
    """Calculate days between a datetime and reference (default: now)."""
    if reference is None:
        reference = datetime.now()
    return (reference - dt).days


def is_business_day(dt: datetime) -> bool:
    """Check if datetime falls on a weekday."""
    return dt.weekday() < 5


def format_timestamp(dt: datetime) -> str:
    """Format datetime for SQLite storage."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(d: date) -> str:
    """Format date for SQLite storage."""
    return d.strftime("%Y-%m-%d")
