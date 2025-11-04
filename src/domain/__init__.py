"""
Domain layer for the Movistar Automation System.

This package contains the core business logic, domain models,
and domain services that are independent of external concerns.
"""

from .processors import (
    BaseProcessor,
    TipificadorProcessor,
    DigitalProcessor,
    HistoricalSalesProcessor,
    consolidate_monthly_report,
)

__all__ = [
    "BaseProcessor",
    "TipificadorProcessor",
    "DigitalProcessor",
    "HistoricalSalesProcessor",
    "consolidate_monthly_report",
]
