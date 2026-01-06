"""Scrapers package for loading pre-curated data."""

from .data_loader import (
    load_first_names,
    load_last_names,
    load_task_templates,
    load_project_templates,
    load_comment_templates,
)

__all__ = [
    'load_first_names',
    'load_last_names',
    'load_task_templates',
    'load_project_templates',
    'load_comment_templates',
]
