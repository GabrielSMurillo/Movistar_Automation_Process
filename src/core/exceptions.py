"""
Custom exceptions for the Movistar Automation System.

This module defines a hierarchy of exceptions to provide clear,
specific error handling throughout the application.

Exception Hierarchy:
 MovistarAutomationError (base)
 [EMOJI] ConfigurationError
 [EMOJI] DataValidationError
 [EMOJI] [EMOJI] PhoneValidationError
 [EMOJI] [EMOJI] DateValidationError
 [EMOJI] [EMOJI] SchemaValidationError
 [EMOJI] FileOperationError
 [EMOJI] [EMOJI] FileNotFoundError
 [EMOJI] [EMOJI] FileFormatError
 [EMOJI] [EMOJI] FileWriteError
 [EMOJI] ProcessingError
 [EMOJI] [EMOJI] DuplicateRecordError
 [EMOJI] [EMOJI] TransformationError
 [EMOJI] OutputGenerationError

Example:
 >>> from src.core.exceptions import PhoneValidationError
 >>> if not is_valid_phone(phone):
 ... raise PhoneValidationError(f"Invalid phone: {phone}")
"""

from typing import Optional, Any

class MovistarAutomationError(Exception):
 """
 Base exception for all Movistar Automation errors.
 
 All custom exceptions should inherit from this class.
 """
 
 def __init__(
 self,
 message: str,
 details: Optional[dict[str, Any]] = None,
 original_exception: Optional[Exception] = None
 ):
 """
 Initialize exception.
 
 Args:
 message: Human-readable error message
 details: Additional context (dict)
 original_exception: Original exception if wrapping
 """
 super().__init__(message)
 self.message = message
 self.details = details or {}
 self.original_exception = original_exception
 
 def __str__(self) -> str:
 """String representation with details."""
 base = self.message
 if self.details:
 details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
 base = f"{base} [{details_str}]"
 return base

# ============================================================================
# CONFIGURATION ERRORS
# ============================================================================

class ConfigurationError(MovistarAutomationError):
 """Raised when there's an error in configuration."""
 pass

class InvalidEnvironmentError(ConfigurationError):
 """Raised when environment variable is invalid."""
 pass

# ============================================================================
# DATA VALIDATION ERRORS
# ============================================================================

class DataValidationError(MovistarAutomationError):
 """Base class for data validation errors."""
 pass

class PhoneValidationError(DataValidationError):
 """Raised when phone number validation fails."""
 
 def __init__(self, phone: str, reason: str, **kwargs):
 super().__init__(
 f"Invalid phone number: {phone}. Reason: {reason}",
 details={"phone": phone, "reason": reason, **kwargs}
 )

class DateValidationError(DataValidationError):
 """Raised when date validation fails."""
 
 def __init__(self, date_value: Any, reason: str, **kwargs):
 super().__init__(
 f"Invalid date: {date_value}. Reason: {reason}",
 details={"date": date_value, "reason": reason, **kwargs}
 )

class SchemaValidationError(DataValidationError):
 """Raised when DataFrame schema validation fails."""
 
 def __init__(self, missing_columns: set, available_columns: set, **kwargs):
 super().__init__(
 f"Schema validation failed. Missing columns: {missing_columns}",
 details={
 "missing_columns": list(missing_columns),
 "available_columns": list(available_columns),
 **kwargs
 }
 )

class DataQualityError(DataValidationError):
 """Raised when data quality checks fail."""
 
 def __init__(self, metric: str, value: float, threshold: float, **kwargs):
 super().__init__(
 f"Data quality check failed: {metric}={value:.2%} exceeds threshold {threshold:.2%}",
 details={
 "metric": metric,
 "value": value,
 "threshold": threshold,
 **kwargs
 }
 )

# ============================================================================
# FILE OPERATION ERRORS
# ============================================================================

class FileOperationError(MovistarAutomationError):
 """Base class for file operation errors."""
 pass

class FileNotFoundError(FileOperationError):
 """Raised when required file is not found."""
 
 def __init__(self, file_path: str, **kwargs):
 super().__init__(
 f"File not found: {file_path}",
 details={"file_path": file_path, **kwargs}
 )

class FileFormatError(FileOperationError):
 """Raised when file format is invalid."""
 
 def __init__(self, file_path: str, expected_format: str, **kwargs):
 super().__init__(
 f"Invalid file format: {file_path}. Expected: {expected_format}",
 details={
 "file_path": file_path,
 "expected_format": expected_format,
 **kwargs
 }
 )

class FileWriteError(FileOperationError):
 """Raised when writing file fails."""
 
 def __init__(self, file_path: str, reason: str, **kwargs):
 super().__init__(
 f"Failed to write file: {file_path}. Reason: {reason}",
 details={
 "file_path": file_path,
 "reason": reason,
 **kwargs
 }
 )

# ============================================================================
# PROCESSING ERRORS
# ============================================================================

class ProcessingError(MovistarAutomationError):
 """Base class for processing errors."""
 pass

class DuplicateRecordError(ProcessingError):
 """Raised when duplicate record is detected."""
 
 def __init__(self, record_id: str, duplicate_of: str, **kwargs):
 super().__init__(
 f"Duplicate record detected: {record_id} is duplicate of {duplicate_of}",
 details={
 "record_id": record_id,
 "duplicate_of": duplicate_of,
 **kwargs
 }
 )

class TransformationError(ProcessingError):
 """Raised when data transformation fails."""
 
 def __init__(self, transformation: str, reason: str, **kwargs):
 super().__init__(
 f"Transformation '{transformation}' failed: {reason}",
 details={
 "transformation": transformation,
 "reason": reason,
 **kwargs
 }
 )

# ============================================================================
# OUTPUT GENERATION ERRORS
# ============================================================================

class OutputGenerationError(MovistarAutomationError):
 """Raised when output generation fails."""
 
 def __init__(self, output_type: str, reason: str, **kwargs):
 super().__init__(
 f"Failed to generate {output_type}: {reason}",
 details={
 "output_type": output_type,
 "reason": reason,
 **kwargs
 }
 )

# ============================================================================
# RETRY ERRORS
# ============================================================================

class RetryExhaustedError(MovistarAutomationError):
 """Raised when retry attempts are exhausted."""
 
 def __init__(self, operation: str, attempts: int, last_error: Exception, **kwargs):
 super().__init__(
 f"Retry exhausted for '{operation}' after {attempts} attempts",
 details={
 "operation": operation,
 "attempts": attempts,
 "last_error": str(last_error),
 **kwargs
 },
 original_exception=last_error
 )

# Export all exceptions
__all__ = [
 "MovistarAutomationError",
 "ConfigurationError",
 "InvalidEnvironmentError",
 "DataValidationError",
 "PhoneValidationError",
 "DateValidationError",
 "SchemaValidationError",
 "DataQualityError",
 "FileOperationError",
 "FileNotFoundError",
 "FileFormatError",
 "FileWriteError",
 "ProcessingError",
 "DuplicateRecordError",
 "TransformationError",
 "OutputGenerationError",
 "RetryExhaustedError",
]
