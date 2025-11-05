"""
Core module for Movistar Automation System.

This package contains the foundational components:
- Configuration management with Pydantic
- Custom exception hierarchy
- Domain models with validation
- Utility decorators

Example:
 >>> from src.core import get_settings
 >>> from src.core.exceptions import PhoneValidationError
 >>> from src.core.models import SaleRecord
 >>> from src.core.decorators import retry, timing
"""

from src.core.config import get_settings, reset_settings, Settings, Environment
from src.core.exceptions import (
 MovistarAutomationError,
 ConfigurationError,
 DataValidationError,
 PhoneValidationError,
 FileOperationError,
 ProcessingError,
)
from src.core.models import (
 SaleRecord,
 ProcessingMetrics,
 ValidationResult,
 TipoLinea,
 TipoVenta,
 DuplicateStatus,
)
from src.core.decorators import (
 retry,
 timing,
 log_execution,
 cache_result,
)

__version__ = "2.0.0"
__author__ = "Movistar Automation Team"

__all__ = [
 # Config
 "get_settings",
 "reset_settings",
 "Settings",
 "Environment",
 # Exceptions
 "MovistarAutomationError",
 "ConfigurationError",
 "DataValidationError",
 "PhoneValidationError",
 "FileOperationError",
 "ProcessingError",
 # Models
 "SaleRecord",
 "ProcessingMetrics",
 "ValidationResult",
 "TipoLinea",
 "TipoVenta",
 "DuplicateStatus",
 # Decorators
 "retry",
 "timing",
 "log_execution",
 "cache_result",
]
