"""
Statistical distribution utilities for realistic data generation.

Implements research-based distributions for:
- Task completion rates
- Assignment patterns
- Comment frequencies
- Priority distributions
"""

import random
from typing import List, Dict, Any, TypeVar, Optional

T = TypeVar('T')


def weighted_choice(options: Dict[T, float]) -> T:
    """
    Select from options based on weighted probabilities.
    
    Args:
        options: Dict mapping choices to their probability weights.
                 Weights should sum to 1.0 but will be normalized if not.
    
    Returns:
        Selected option
    """
    items = list(options.items())
    choices, weights = zip(*items)
    total = sum(weights)
    normalized_weights = [w / total for w in weights]
    return random.choices(choices, weights=normalized_weights, k=1)[0]


def weighted_sample(options: Dict[T, float], k: int) -> List[T]:
    """
    Sample k items from options based on weights (without replacement).
    """
    items = list(options.items())
    choices, weights = zip(*items)
    total = sum(weights)
    normalized_weights = [w / total for w in weights]
    
    # Adjust k if larger than available options
    k = min(k, len(choices))
    
    selected = []
    remaining_choices = list(choices)
    remaining_weights = list(normalized_weights)
    
    for _ in range(k):
        if not remaining_choices:
            break
        # Renormalize weights
        total = sum(remaining_weights)
        if total == 0:
            break
        probs = [w / total for w in remaining_weights]
        
        idx = random.choices(range(len(remaining_choices)), weights=probs, k=1)[0]
        selected.append(remaining_choices.pop(idx))
        remaining_weights.pop(idx)
    
    return selected


def log_normal_int(mean: float, sigma: float, min_val: int = 0, max_val: int = 100) -> int:
    """
    Generate an integer from a log-normal distribution.
    
    Useful for realistic counts (comments, subtasks) that are
    right-skewed (many low values, few high values).
    """
    value = random.lognormvariate(mean, sigma)
    return max(min_val, min(max_val, int(value)))


def normal_int(mean: float, std: float, min_val: int = 0, max_val: int = 100) -> int:
    """Generate an integer from a normal distribution, clamped to range."""
    value = random.gauss(mean, std)
    return max(min_val, min(max_val, int(value)))


def biased_boolean(true_probability: float) -> bool:
    """Return True with the given probability."""
    return random.random() < true_probability


def random_subset(items: List[T], min_count: int = 0, max_count: Optional[int] = None) -> List[T]:
    """
    Select a random subset of items.
    
    Args:
        items: List to select from
        min_count: Minimum items to select
        max_count: Maximum items to select (default: len(items))
    
    Returns:
        Random subset of items
    """
    if not items:
        return []
    
    if max_count is None:
        max_count = len(items)
    
    max_count = min(max_count, len(items))
    min_count = min(min_count, max_count)
    
    count = random.randint(min_count, max_count)
    return random.sample(items, count)


def distribute_among(total: int, buckets: int, min_per_bucket: int = 0) -> List[int]:
    """
    Distribute a total count across buckets somewhat evenly.
    
    Uses a variation of the "stars and bars" method with some noise.
    
    Args:
        total: Total count to distribute
        buckets: Number of buckets
        min_per_bucket: Minimum count per bucket
    
    Returns:
        List of counts per bucket
    """
    if buckets <= 0:
        return []
    
    # Ensure we have enough for minimums
    remaining = total - (min_per_bucket * buckets)
    if remaining < 0:
        # Not enough for minimums, distribute evenly
        base = total // buckets
        result = [base] * buckets
        # Distribute remainder
        for i in range(total % buckets):
            result[i] += 1
        return result
    
    # Start with minimums
    result = [min_per_bucket] * buckets
    
    # Distribute remaining with some randomness
    for _ in range(remaining):
        # Slightly favor buckets with fewer items
        weights = [1.0 / (count + 1) for count in result]
        idx = random.choices(range(buckets), weights=weights, k=1)[0]
        result[idx] += 1
    
    return result


def power_law_sample(n: int, alpha: float = 2.0) -> List[int]:
    """
    Generate n samples from a power law distribution.
    
    Useful for realistic distributions where a few items
    dominate (e.g., task counts per project).
    
    Args:
        n: Number of samples
        alpha: Power law exponent (higher = more skewed)
    
    Returns:
        List of sample values (sorted descending)
    """
    samples = []
    for _ in range(n):
        # Inverse transform sampling for power law
        u = random.random()
        value = (1 - u) ** (-1 / (alpha - 1))
        samples.append(int(value))
    
    return sorted(samples, reverse=True)


def completion_rate_for_project_type(project_type: str) -> float:
    """
    Get realistic completion rate based on project type.
    
    Based on agile benchmarks and Asana Anatomy of Work.
    """
    rates = {
        "sprint": (0.70, 0.85),      # Sprint projects: 70-85%
        "ongoing": (0.40, 0.50),     # Ongoing/maintenance: 40-50%
        "campaign": (0.60, 0.75),    # Marketing campaigns: 60-75%
        "planning": (0.30, 0.45),    # Planning/discovery: 30-45%
        "default": (0.50, 0.70),     # Default: 50-70%
    }
    
    low, high = rates.get(project_type, rates["default"])
    return random.uniform(low, high)


def comment_count_for_task() -> int:
    """
    Generate realistic comment count for a task.
    
    Distribution:
    - 30% have 0 comments
    - 40% have 1-3 comments
    - 20% have 4-10 comments
    - 10% have 10-25 comments (active discussions)
    """
    roll = random.random()
    
    if roll < 0.30:
        return 0
    elif roll < 0.70:
        return random.randint(1, 3)
    elif roll < 0.90:
        return random.randint(4, 10)
    else:
        return random.randint(10, 25)


def subtask_count_for_task() -> int:
    """
    Generate realistic subtask count for a task.
    
    Most tasks don't have subtasks. When they do:
    - 50% have 2-3 subtasks
    - 30% have 4-5 subtasks
    - 20% have 6-10 subtasks
    """
    roll = random.random()
    
    if roll < 0.50:
        return random.randint(2, 3)
    elif roll < 0.80:
        return random.randint(4, 5)
    else:
        return random.randint(6, 10)
