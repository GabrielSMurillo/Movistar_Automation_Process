"""
Utility modules for the Movistar Automation System.

Provides helper functions and utilities for:
- Excel sanitization and security
- Data validation helpers
- General utilities
"""

from .excel_sanitizer import (
    sanitize_for_excel,
    sanitize_value,
    sanitize_list,
    is_potentially_dangerous,
)

__all__ = [
    'sanitize_for_excel',
    'sanitize_value',
    'sanitize_list',
    'is_potentially_dangerous',
]
