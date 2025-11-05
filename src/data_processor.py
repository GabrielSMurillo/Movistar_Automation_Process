"""
DEPRECATED: This module is deprecated.

Use src.domain.processors instead.

This file exists only for backward compatibility and will be removed
in a future version.
"""

import warnings
warnings.warn(
    "src.data_processor is deprecated. Import from src.domain.processors instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from new location for backward compatibility
from src.domain.processors import (
    BaseProcessor,
    TipificadorProcessor,
    DigitalProcessor,
    HistoricalSalesProcessor,
    consolidate_monthly_report,
    ProcessingResult,
)

__all__ = [
    "BaseProcessor",
    "TipificadorProcessor",
    "DigitalProcessor",
    "HistoricalSalesProcessor",
    "consolidate_monthly_report",
    "ProcessingResult",
]
