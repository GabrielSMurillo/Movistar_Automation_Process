"""
Excel Sanitizer - Prevent CSV/Formula Injection Attacks.

This module provides utilities to sanitize data before exporting to Excel,
preventing malicious formula injection.

Security Issue:
    When exporting to Excel, cells starting with =, +, -, @ can be interpreted
    as formulas, potentially executing malicious code or exfiltrating data.

Example:
    >>> df = pd.DataFrame({'phone': ['=cmd|"/c calc"', '3001234567']})
    >>> df_safe = sanitize_for_excel(df)
    >>> print(df_safe['phone'].iloc[0])
    "'=cmd|"/c calc""  # Prefixed with ' to prevent execution
"""

import pandas as pd
import logging
from typing import Union

logger = logging.getLogger(__name__)


def sanitize_for_excel(
    df: pd.DataFrame,
    inplace: bool = False
) -> pd.DataFrame:
    """
    Sanitize DataFrame to prevent formula injection in Excel.
    
    Prepends ' (single quote) to any cell starting with:
    - = (formula)
    - + (formula)
    - - (formula/negative)
    - @ (formula reference)
    - \t (tab - can bypass filters)
    - \r (carriage return)
    
    Args:
        df: DataFrame to sanitize
        inplace: If True, modify DataFrame in place
    
    Returns:
        Sanitized DataFrame
    
    Example:
        >>> df = pd.DataFrame({'name': ['John', '=SUM(1+1)'], 'phone': ['3001234567', '3009876543']})
        >>> df_safe = sanitize_for_excel(df)
        >>> df_safe['name'].iloc[1]
        "'=SUM(1+1)"
    """
    if not inplace:
        df = df.copy()
    
    sanitized_count = 0
    dangerous_prefixes = ('=', '+', '-', '@', '\t', '\r')
    
    # Process all object (string) columns
    for col in df.select_dtypes(include=['object']).columns:
        # Check each cell
        mask = df[col].astype(str).str.startswith(dangerous_prefixes)
        sanitized_count += mask.sum()
        
        if mask.any():
            # Prepend ' to dangerous cells
            df.loc[mask, col] = "'" + df.loc[mask, col].astype(str)
            
            logger.debug(
                f"Sanitized {mask.sum()} cells in column '{col}' "
                f"to prevent formula injection"
            )
    
    if sanitized_count > 0:
        logger.info(
            f"🔒 Excel Sanitization: Protected {sanitized_count} cells "
            f"from potential formula injection"
        )
    
    return df


def sanitize_value(value: any) -> any:
    """
    Sanitize a single value for Excel export.
    
    Args:
        value: Value to sanitize
    
    Returns:
        Sanitized value
    
    Example:
        >>> sanitize_value('=1+1')
        "'=1+1"
        >>> sanitize_value('normal text')
        'normal text'
    """
    if not isinstance(value, str):
        return value
    
    if value and value[0] in ('=', '+', '-', '@', '\t', '\r'):
        return f"'{value}"
    
    return value


def sanitize_list(data: list[list]) -> list[list]:
    """
    Sanitize a list of lists (used for Contact Log generation).
    
    Args:
        data: List of lists to sanitize
    
    Returns:
        Sanitized list of lists
    
    Example:
        >>> data = [['John', '=1+1'], ['Jane', 'normal']]
        >>> sanitized = sanitize_list(data)
        >>> sanitized[0][1]
        "'=1+1"
    """
    return [
        [sanitize_value(cell) for cell in row]
        for row in data
    ]


def is_potentially_dangerous(value: any) -> bool:
    """
    Check if a value could be dangerous in Excel.
    
    Args:
        value: Value to check
    
    Returns:
        True if potentially dangerous
    
    Example:
        >>> is_potentially_dangerous('=SUM(1+1)')
        True
        >>> is_potentially_dangerous('normal text')
        False
    """
    if not isinstance(value, str) or not value:
        return False
    
    return value[0] in ('=', '+', '-', '@', '\t', '\r')


# Export
__all__ = [
    'sanitize_for_excel',
    'sanitize_value',
    'sanitize_list',
    'is_potentially_dangerous',
]
