"""
Name generation utilities using census-based data.

Generates realistic names reflecting US demographic distributions.
Names are loaded from pre-curated JSON files based on Census data.
"""

import os
import json
import random
from typing import List, Tuple, Optional

# Cache for loaded name data
_first_names_cache: Optional[List[Tuple[str, float]]] = None
_last_names_cache: Optional[List[Tuple[str, float]]] = None


def _get_data_path(filename: str) -> str:
    """Get path to data file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "data", filename)


def _load_first_names() -> List[Tuple[str, float]]:
    """Load first names from data file."""
    global _first_names_cache
    
    if _first_names_cache is not None:
        return _first_names_cache
    
    filepath = _get_data_path("first_names.json")
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _first_names_cache = [(item["name"], item.get("weight", 1.0)) for item in data]
    else:
        # Fallback to built-in list if file not found
        _first_names_cache = _get_fallback_first_names()
    
    return _first_names_cache


def _load_last_names() -> List[Tuple[str, float]]:
    """Load last names from data file."""
    global _last_names_cache
    
    if _last_names_cache is not None:
        return _last_names_cache
    
    filepath = _get_data_path("last_names.json")
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _last_names_cache = [(item["name"], item.get("weight", 1.0)) for item in data]
    else:
        # Fallback to built-in list if file not found
        _last_names_cache = _get_fallback_last_names()
    
    return _last_names_cache


def _get_fallback_first_names() -> List[Tuple[str, float]]:
    """Built-in first names based on US Census popularity."""
    # Top 100 first names with rough census-based weights
    names = [
        ("James", 3.318), ("Robert", 3.143), ("John", 3.271), ("Michael", 4.350), ("David", 3.611),
        ("William", 3.614), ("Richard", 2.563), ("Joseph", 2.603), ("Thomas", 2.304), ("Christopher", 2.032),
        ("Charles", 2.106), ("Daniel", 2.007), ("Matthew", 1.600), ("Anthony", 1.404), ("Mark", 1.346),
        ("Donald", 1.348), ("Steven", 1.286), ("Paul", 1.286), ("Andrew", 1.272), ("Joshua", 1.266),
        ("Kenneth", 1.226), ("Kevin", 1.173), ("Brian", 1.166), ("George", 1.164), ("Timothy", 1.069),
        ("Ronald", 1.073), ("Edward", 1.095), ("Jason", 0.997), ("Jeffrey", 0.973), ("Ryan", 0.966),
        ("Mary", 2.629), ("Patricia", 1.571), ("Jennifer", 1.468), ("Linda", 1.452), ("Elizabeth", 1.629),
        ("Barbara", 1.435), ("Susan", 1.120), ("Jessica", 1.045), ("Sarah", 0.998), ("Karen", 0.985),
        ("Lisa", 0.969), ("Nancy", 0.978), ("Betty", 0.932), ("Margaret", 0.944), ("Sandra", 0.873),
        ("Ashley", 0.853), ("Kimberly", 0.868), ("Emily", 0.844), ("Donna", 0.860), ("Michelle", 0.811),
        ("Dorothy", 0.727), ("Carol", 0.736), ("Amanda", 0.772), ("Melissa", 0.753), ("Deborah", 0.739),
        ("Stephanie", 0.744), ("Rebecca", 0.739), ("Sharon", 0.740), ("Laura", 0.697), ("Cynthia", 0.705),
        ("Priya", 0.400), ("Aisha", 0.350), ("Wei", 0.380), ("Hiroshi", 0.320), ("Carlos", 0.450),
        ("Mohammed", 0.480), ("Fatima", 0.400), ("Yuki", 0.300), ("Raj", 0.350), ("Ana", 0.420),
        ("Chen", 0.380), ("Olga", 0.280), ("Ivan", 0.320), ("Sanjay", 0.350), ("Maria", 0.520),
        ("Ahmed", 0.380), ("Nadia", 0.300), ("Viktor", 0.280), ("Kenji", 0.300), ("Ananya", 0.320),
    ]
    return names


def _get_fallback_last_names() -> List[Tuple[str, float]]:
    """Built-in last names based on US Census popularity."""
    names = [
        ("Smith", 2.376), ("Johnson", 1.935), ("Williams", 1.635), ("Brown", 1.437), ("Jones", 1.362),
        ("Garcia", 1.166), ("Miller", 1.161), ("Davis", 1.116), ("Rodriguez", 1.094), ("Martinez", 1.060),
        ("Hernandez", 1.043), ("Lopez", 0.973), ("Gonzalez", 0.966), ("Wilson", 0.843), ("Anderson", 0.784),
        ("Thomas", 0.761), ("Taylor", 0.751), ("Moore", 0.724), ("Jackson", 0.708), ("Martin", 0.678),
        ("Lee", 0.693), ("Perez", 0.681), ("Thompson", 0.669), ("White", 0.660), ("Harris", 0.624),
        ("Sanchez", 0.612), ("Clark", 0.575), ("Ramirez", 0.568), ("Lewis", 0.562), ("Robinson", 0.548),
        ("Walker", 0.541), ("Young", 0.529), ("Allen", 0.496), ("King", 0.491), ("Wright", 0.483),
        ("Scott", 0.481), ("Torres", 0.478), ("Nguyen", 0.476), ("Hill", 0.474), ("Flores", 0.467),
        ("Green", 0.459), ("Adams", 0.442), ("Nelson", 0.439), ("Baker", 0.425), ("Hall", 0.423),
        ("Rivera", 0.419), ("Campbell", 0.415), ("Mitchell", 0.409), ("Carter", 0.407), ("Roberts", 0.398),
        ("Patel", 0.520), ("Kim", 0.480), ("Shah", 0.350), ("Chen", 0.450), ("Wang", 0.420),
        ("Singh", 0.380), ("Kumar", 0.400), ("Sharma", 0.350), ("Gupta", 0.320), ("Wong", 0.300),
        ("Liu", 0.340), ("Zhang", 0.380), ("Huang", 0.300), ("Yang", 0.280), ("Tanaka", 0.250),
        ("Sato", 0.240), ("Suzuki", 0.230), ("Yamamoto", 0.220), ("Nakamura", 0.210), ("Kobayashi", 0.200),
    ]
    return names


def generate_full_name() -> str:
    """Generate a realistic full name."""
    first_names = _load_first_names()
    last_names = _load_last_names()
    
    # Weighted random selection
    first_choices, first_weights = zip(*first_names)
    last_choices, last_weights = zip(*last_names)
    
    first = random.choices(first_choices, weights=first_weights, k=1)[0]
    last = random.choices(last_choices, weights=last_weights, k=1)[0]
    
    return f"{first} {last}"


def generate_email(name: str, domain: str) -> str:
    """
    Generate email from name and domain.
    
    Format: firstname.lastname@domain
    Handles duplicates by adding numbers if needed.
    """
    parts = name.lower().split()
    if len(parts) >= 2:
        email_name = f"{parts[0]}.{parts[-1]}"
    else:
        email_name = parts[0] if parts else "user"
    
    # Remove special characters
    email_name = ''.join(c for c in email_name if c.isalnum() or c == '.')
    
    return f"{email_name}@{domain}"


def generate_unique_names(count: int) -> List[str]:
    """Generate a list of unique full names."""
    names = set()
    attempts = 0
    max_attempts = count * 3  # Avoid infinite loop
    
    while len(names) < count and attempts < max_attempts:
        names.add(generate_full_name())
        attempts += 1
    
    # If we couldn't get enough unique names, add numbered variants
    while len(names) < count:
        base_name = generate_full_name()
        suffix = random.randint(1, 99)
        names.add(f"{base_name} {suffix}")
    
    return list(names)


def generate_unique_emails(names: List[str], domain: str) -> List[str]:
    """Generate unique emails for a list of names."""
    emails = []
    seen = set()
    
    for name in names:
        base_email = generate_email(name, domain)
        email = base_email
        counter = 1
        
        while email in seen:
            # Add number to make unique
            local, dom = base_email.split('@')
            email = f"{local}{counter}@{dom}"
            counter += 1
        
        emails.append(email)
        seen.add(email)
    
    return emails
