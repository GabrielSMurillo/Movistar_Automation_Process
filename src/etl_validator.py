"""
ETL Validator - Comprehensive validation for data pipeline.

Validates:
1. File loading (format, schema, data types)
2. Data transformations (integrity, correctness)
3. Data quality (completeness, accuracy)
4. Performance metrics
5. End-to-end reconciliation

Example:
 >>> validator = ETLValidator()
 >>> 
 >>> # Validate file loading
 >>> result = validator.validate_load(df, 'tipificador', expected_columns)
 >>> 
 >>> # Validate transformation
 >>> result = validator.validate_transform(df_before, df_after, 'phone_cleaning')
 >>> 
 >>> # End-to-end validation
 >>> report = validator.generate_etl_report()
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
 """Result of a validation check."""
 stage: str
 check_name: str
 passed: bool
 message: str
 details: Dict[str, Any] = field(default_factory=dict)
 timestamp: datetime = field(default_factory=datetime.now)
 severity: str = "INFO" # INFO, WARNING, ERROR, CRITICAL

@dataclass
class ETLMetrics:
 """Metrics for ETL stage."""
 stage_name: str
 records_in: int
 records_out: int
 records_added: int = 0
 records_removed: int = 0
 duration_seconds: float = 0.0
 memory_mb: float = 0.0
 passed_validation: bool = True
 
 @property
 def records_delta(self) -> int:
 return self.records_out - self.records_in
 
 @property
 def retention_rate(self) -> float:
 if self.records_in == 0:
 return 0.0
 return (self.records_out / self.records_in) * 100

class ETLValidator:
 """
 Comprehensive ETL validator.
 
 Tracks and validates every stage of the ETL process.
 """
 
 def __init__(self):
 """Initialize ETL validator."""
 self.validation_results: List[ValidationResult] = []
 self.stage_metrics: List[ETLMetrics] = []
 self.logger = logging.getLogger(f"{__name__}.ETLValidator")
 
 # ==========================================
 # FILE LOADING VALIDATION
 # ==========================================
 
 def validate_load(
 self,
 df: pd.DataFrame,
 file_name: str,
 expected_columns: List[str] = None,
 expected_types: Dict[str, str] = None,
 min_records: int = 1
 ) -> ValidationResult:
 """
 Validate file loading.
 
 Checks:
 - File loaded successfully (not empty)
 - Expected columns present
 - Data types correct
 - Minimum record count
 - No completely null columns
 
 Args:
 df: Loaded DataFrame
 file_name: Name of file
 expected_columns: List of required columns
 expected_types: Expected data types {col: type}
 min_records: Minimum expected records
 
 Returns:
 ValidationResult
 """
 checks_passed = []
 checks_failed = []
 details = {}
 
 # Check 1: Not empty
 if df.empty:
 checks_failed.append("DataFrame is empty")
 return ValidationResult(
 stage="LOAD",
 check_name=f"load_{file_name}",
 passed=False,
 message=f"File '{file_name}' loaded but DataFrame is empty",
 severity="CRITICAL"
 )
 else:
 checks_passed.append(f"Loaded {len(df):,} records")
 details['records_loaded'] = len(df)
 details['columns_loaded'] = len(df.columns)
 
 # Check 2: Minimum records
 if len(df) < min_records:
 checks_failed.append(f"Only {len(df)} records (expected >= {min_records})")
 else:
 checks_passed.append(f"Record count OK ({len(df):,} >= {min_records})")
 
 # Check 3: Expected columns
 if expected_columns:
 missing_cols = set(expected_columns) - set(df.columns)
 extra_cols = set(df.columns) - set(expected_columns)
 
 if missing_cols:
 checks_failed.append(f"Missing columns: {missing_cols}")
 else:
 checks_passed.append("All expected columns present")
 
 if extra_cols:
 checks_passed.append(f"Extra columns found: {extra_cols}")
 
 details['missing_columns'] = list(missing_cols)
 details['extra_columns'] = list(extra_cols)
 
 # Check 4: Data types
 if expected_types:
 type_mismatches = []
 for col, expected_type in expected_types.items():
 if col in df.columns:
 actual_type = str(df[col].dtype)
 if expected_type not in actual_type:
 type_mismatches.append(f"{col}: {actual_type} (expected {expected_type})")
 
 if type_mismatches:
 checks_failed.append(f"Type mismatches: {type_mismatches}")
 else:
 checks_passed.append("Data types OK")
 
 details['type_mismatches'] = type_mismatches
 
 # Check 5: Completely null columns
 null_cols = df.columns[df.isnull().all()].tolist()
 if null_cols:
 checks_failed.append(f"Completely null columns: {null_cols}")
 else:
 checks_passed.append("No completely null columns")
 
 details['null_columns'] = null_cols
 
 # Check 6: Memory usage
 memory_mb = df.memory_usage(deep=True).sum() / 1024**2
 details['memory_mb'] = f"{memory_mb:.2f}"
 checks_passed.append(f"Memory: {memory_mb:.2f} MB")
 
 # Summary
 passed = len(checks_failed) == 0
 severity = "ERROR" if not passed else "INFO"
 
 message = f"File '{file_name}': {len(checks_passed)} checks passed"
 if checks_failed:
 message += f", {len(checks_failed)} FAILED"
 
 result = ValidationResult(
 stage="LOAD",
 check_name=f"load_{file_name}",
 passed=passed,
 message=message,
 details=details,
 severity=severity
 )
 
 self.validation_results.append(result)
 self._log_result(result, checks_passed, checks_failed)
 
 return result
 
 # ==========================================
 # SCHEMA VALIDATION
 # ==========================================
 
 def validate_schema(
 self,
 df: pd.DataFrame,
 schema: Dict[str, Any],
 stage_name: str = "schema_check"
 ) -> ValidationResult:
 """
 Validate DataFrame against expected schema.
 
 Args:
 df: DataFrame to validate
 schema: Expected schema {col: {'type': str, 'nullable': bool, 'unique': bool}}
 stage_name: Name of validation stage
 
 Returns:
 ValidationResult
 """
 checks_passed = []
 checks_failed = []
 details = {}
 
 for col, constraints in schema.items():
 # Check existence
 if col not in df.columns:
 checks_failed.append(f"Column '{col}' missing")
 continue
 
 # Check type
 if 'type' in constraints:
 expected_type = constraints['type']
 actual_type = str(df[col].dtype)
 if expected_type not in actual_type:
 checks_failed.append(f"'{col}': type {actual_type} (expected {expected_type})")
 
 # Check nullable
 if 'nullable' in constraints and not constraints['nullable']:
 null_count = df[col].isnull().sum()
 if null_count > 0:
 checks_failed.append(f"'{col}': {null_count:,} nulls (not allowed)")
 
 # Check unique
 if 'unique' in constraints and constraints['unique']:
 dup_count = df[col].duplicated().sum()
 if dup_count > 0:
 checks_failed.append(f"'{col}': {dup_count:,} duplicates (should be unique)")
 
 passed = len(checks_failed) == 0
 
 result = ValidationResult(
 stage="SCHEMA",
 check_name=stage_name,
 passed=passed,
 message=f"Schema validation: {len(checks_passed)} OK, {len(checks_failed)} FAILED",
 details=details,
 severity="ERROR" if not passed else "INFO"
 )
 
 self.validation_results.append(result)
 self._log_result(result, checks_passed, checks_failed)
 
 return result
 
 # ==========================================
 # TRANSFORMATION VALIDATION
 # ==========================================
 
 def validate_transform(
 self,
 df_before: pd.DataFrame,
 df_after: pd.DataFrame,
 transform_name: str,
 expected_delta: int = None,
 min_retention: float = 0.0,
 max_retention: float = 100.0
 ) -> ValidationResult:
 """
 Validate data transformation.
 
 Checks:
 - Record count changes are expected
 - No unexpected data loss
 - Retention rate within bounds
 
 Args:
 df_before: DataFrame before transformation
 df_after: DataFrame after transformation
 transform_name: Name of transformation
 expected_delta: Expected change in record count (None = any)
 min_retention: Minimum acceptable retention rate (%)
 max_retention: Maximum acceptable retention rate (%)
 
 Returns:
 ValidationResult
 """
 checks_passed = []
 checks_failed = []
 details = {}
 
 records_before = len(df_before)
 records_after = len(df_after)
 delta = records_after - records_before
 retention_rate = (records_after / records_before * 100) if records_before > 0 else 0
 
 details['records_before'] = records_before
 details['records_after'] = records_after
 details['delta'] = delta
 details['retention_rate'] = f"{retention_rate:.1f}%"
 
 # Check 1: Record count delta
 if expected_delta is not None:
 if delta == expected_delta:
 checks_passed.append(f"Delta OK: {delta} (expected {expected_delta})")
 else:
 checks_failed.append(f"Delta mismatch: {delta} (expected {expected_delta})")
 else:
 checks_passed.append(f"Record delta: {delta:+,}")
 
 # Check 2: Retention rate
 if retention_rate < min_retention:
 checks_failed.append(f"Retention {retention_rate:.1f}% < min {min_retention}%")
 elif retention_rate > max_retention:
 checks_failed.append(f"Retention {retention_rate:.1f}% > max {max_retention}%")
 else:
 checks_passed.append(f"Retention rate OK: {retention_rate:.1f}%")
 
 # Check 3: Column consistency
 cols_added = set(df_after.columns) - set(df_before.columns)
 cols_removed = set(df_before.columns) - set(df_after.columns)
 
 if cols_added:
 checks_passed.append(f"Columns added: {cols_added}")
 details['columns_added'] = list(cols_added)
 
 if cols_removed:
 checks_passed.append(f"Columns removed: {cols_removed}")
 details['columns_removed'] = list(cols_removed)
 
 # Summary
 passed = len(checks_failed) == 0
 
 result = ValidationResult(
 stage="TRANSFORM",
 check_name=transform_name,
 passed=passed,
 message=f"Transform '{transform_name}': {records_before:,} -> {records_after:,} ({delta:+,})",
 details=details,
 severity="WARNING" if not passed else "INFO"
 )
 
 self.validation_results.append(result)
 self._log_result(result, checks_passed, checks_failed)
 
 return result
 
 # ==========================================
 # DATA QUALITY VALIDATION
 # ==========================================
 
 def validate_data_quality(
 self,
 df: pd.DataFrame,
 stage_name: str,
 max_null_rate: float = 0.30,
 max_duplicate_rate: float = 0.10
 ) -> ValidationResult:
 """
 Validate data quality metrics.
 
 Args:
 df: DataFrame to validate
 stage_name: Name of stage
 max_null_rate: Maximum acceptable null rate
 max_duplicate_rate: Maximum acceptable duplicate rate
 
 Returns:
 ValidationResult
 """
 checks_passed = []
 checks_failed = []
 details = {}
 
 # Check 1: Null rates
 null_rates = df.isnull().mean()
 high_null_cols = null_rates[null_rates > max_null_rate]
 
 if not high_null_cols.empty:
 checks_failed.append(
 f"High null rates: {dict(high_null_cols.apply(lambda x: f'{x:.1%}'))}"
 )
 details['high_null_columns'] = high_null_cols.to_dict()
 else:
 checks_passed.append(f"Null rates OK (max: {null_rates.max():.1%})")
 
 # Check 2: Duplicate rate
 dup_count = df.duplicated().sum()
 dup_rate = dup_count / len(df) if len(df) > 0 else 0
 
 if dup_rate > max_duplicate_rate:
 checks_failed.append(f"Duplicate rate {dup_rate:.1%} > max {max_duplicate_rate:.0%}")
 else:
 checks_passed.append(f"Duplicate rate OK: {dup_rate:.1%}")
 
 details['duplicate_count'] = dup_count
 details['duplicate_rate'] = f"{dup_rate:.2%}"
 
 # Check 3: Data types consistency
 object_cols = df.select_dtypes(include=['object']).columns
 numeric_in_object = []
 
 for col in object_cols:
 try:
 pd.to_numeric(df[col], errors='raise')
 numeric_in_object.append(col)
 except:
 pass
 
 if numeric_in_object:
 checks_passed.append(f"Numeric columns stored as object: {numeric_in_object}")
 details['numeric_as_object'] = numeric_in_object
 
 # Summary
 passed = len(checks_failed) == 0
 
 result = ValidationResult(
 stage="QUALITY",
 check_name=stage_name,
 passed=passed,
 message=f"Quality check '{stage_name}': {len(checks_passed)} OK, {len(checks_failed)} issues",
 details=details,
 severity="WARNING" if not passed else "INFO"
 )
 
 self.validation_results.append(result)
 self._log_result(result, checks_passed, checks_failed)
 
 return result
 
 # ==========================================
 # BUSINESS RULE VALIDATION
 # ==========================================
 
 def validate_business_rules(
 self,
 df: pd.DataFrame,
 rules: List[Dict[str, Any]],
 stage_name: str = "business_rules"
 ) -> ValidationResult:
 """
 Validate business rules.
 
 Args:
 df: DataFrame to validate
 rules: List of rules [{'name': str, 'condition': callable, 'severity': str}]
 stage_name: Name of stage
 
 Returns:
 ValidationResult
 
 Example:
 >>> rules = [
 ... {
 ... 'name': 'phone_length',
 ... 'condition': lambda df: (df['telefono'].str.len() == 10).all(),
 ... 'severity': 'ERROR'
 ... },
 ... {
 ... 'name': 'no_future_dates',
 ... 'condition': lambda df: (df['fecha_venta'] <= pd.Timestamp.now()).all(),
 ... 'severity': 'WARNING'
 ... }
 ... ]
 >>> result = validator.validate_business_rules(df, rules)
 """
 checks_passed = []
 checks_failed = []
 details = {}
 max_severity = "INFO"
 
 for rule in rules:
 rule_name = rule['name']
 condition = rule['condition']
 severity = rule.get('severity', 'WARNING')
 
 try:
 result = condition(df)
 
 if result:
 checks_passed.append(f"[OK] {rule_name}")
 else:
 checks_failed.append(f"[FAIL] {rule_name}")
 if severity == "CRITICAL":
 max_severity = "CRITICAL"
 elif severity == "ERROR" and max_severity != "CRITICAL":
 max_severity = "ERROR"
 elif severity == "WARNING" and max_severity not in ["CRITICAL", "ERROR"]:
 max_severity = "WARNING"
 
 details[rule_name] = "passed" if result else "failed"
 
 except Exception as e:
 checks_failed.append(f"[FAIL] {rule_name}: {str(e)}")
 details[rule_name] = f"error: {str(e)}"
 
 passed = len(checks_failed) == 0
 
 result = ValidationResult(
 stage="BUSINESS_RULES",
 check_name=stage_name,
 passed=passed,
 message=f"Business rules: {len(checks_passed)}/{len(rules)} passed",
 details=details,
 severity=max_severity if not passed else "INFO"
 )
 
 self.validation_results.append(result)
 self._log_result(result, checks_passed, checks_failed)
 
 return result
 
 # ==========================================
 # RECONCILIATION
 # ==========================================
 
 def reconcile(
 self,
 df_input: pd.DataFrame,
 df_output: pd.DataFrame,
 expected_retention: float = None
 ) -> ValidationResult:
 """
 Reconcile input vs output records.
 
 Args:
 df_input: Input DataFrame
 df_output: Output DataFrame
 expected_retention: Expected retention rate (%)
 
 Returns:
 ValidationResult
 """
 checks_passed = []
 checks_failed = []
 details = {}
 
 records_in = len(df_input)
 records_out = len(df_output)
 retention = (records_out / records_in * 100) if records_in > 0 else 0
 
 details['records_in'] = records_in
 details['records_out'] = records_out
 details['retention_rate'] = f"{retention:.1f}%"
 details['records_lost'] = records_in - records_out
 
 checks_passed.append(f"Input: {records_in:,} records")
 checks_passed.append(f"Output: {records_out:,} records")
 checks_passed.append(f"Retention: {retention:.1f}%")
 
 if expected_retention is not None:
 diff = abs(retention - expected_retention)
 if diff > 5: # 5% tolerance
 checks_failed.append(
 f"Retention {retention:.1f}% differs from expected {expected_retention:.1f}% by {diff:.1f}%"
 )
 
 passed = len(checks_failed) == 0
 
 result = ValidationResult(
 stage="RECONCILIATION",
 check_name="end_to_end",
 passed=passed,
 message=f"Reconciliation: {records_in:,} {} {records_out:,} ({retention:.1f}%)",
 details=details,
 severity="WARNING" if not passed else "INFO"
 )
 
 self.validation_results.append(result)
 self._log_result(result, checks_passed, checks_failed)
 
 return result
 
 # ==========================================
 # REPORTING
 # ==========================================
 
 def generate_etl_report(self) -> pd.DataFrame:
 """
 Generate comprehensive ETL validation report.
 
 Returns:
 DataFrame with all validation results
 """
 if not self.validation_results:
 return pd.DataFrame()
 
 data = []
 for result in self.validation_results:
 data.append({
 'timestamp': result.timestamp,
 'stage': result.stage,
 'check': result.check_name,
 'passed': result.passed,
 'severity': result.severity,
 'message': result.message,
 'details': str(result.details)
 })
 
 df = pd.DataFrame(data)
 return df
 
 def export_report(self, output_path: Path) -> None:
 """
 Export validation report to Excel.
 
 Args:
 output_path: Output file path
 """
 df_report = self.generate_etl_report()
 
 with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
 df_report.to_excel(writer, sheet_name='Validation Results', index=False)
 
 # Summary sheet
 summary = {
 'total_checks': len(self.validation_results),
 'passed': sum(1 for r in self.validation_results if r.passed),
 'failed': sum(1 for r in self.validation_results if not r.passed),
 'critical': sum(1 for r in self.validation_results if r.severity == 'CRITICAL'),
 'errors': sum(1 for r in self.validation_results if r.severity == 'ERROR'),
 'warnings': sum(1 for r in self.validation_results if r.severity == 'WARNING'),
 }
 
 pd.DataFrame([summary]).to_excel(writer, sheet_name='Summary', index=False)
 
 self.logger.info(f"[INFO] Validation report exported: {output_path}")
 
 def get_failed_checks(self) -> List[ValidationResult]:
 """Get all failed validation checks."""
 return [r for r in self.validation_results if not r.passed]
 
 def has_critical_issues(self) -> bool:
 """Check if there are any critical issues."""
 return any(r.severity == 'CRITICAL' for r in self.validation_results)
 
 def _log_result(
 self,
 result: ValidationResult,
 checks_passed: List[str],
 checks_failed: List[str]
 ) -> None:
 """Log validation result."""
 status = f"[INFO] PASSED" if result.passed else f"[INFO] FAILED"
 self.logger.info(f"{status} - {result.message}")
 
 if checks_passed and self.logger.isEnabledFor(logging.DEBUG):
 for check in checks_passed:
 self.logger.debug(f" [OK] {check}")
 
 if checks_failed:
 for check in checks_failed:
 self.logger.warning(f" [FAIL] {check}")

# Export
__all__ = ['ETLValidator', 'ValidationResult', 'ETLMetrics']
