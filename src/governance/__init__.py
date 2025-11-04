"""
Data Governance Module.

Provides governance capabilities for data tracking, auditing,
and compliance:
- Data lineage tracking
- Audit logging
- Metrics collection
- Alert management

Example:
    >>> from src.governance import LineageTracker, AuditLogger
    >>> 
    >>> tracker = LineageTracker()
    >>> tracker.track_transformation(source='tipificador.xlsx', target='valid_records.csv', operation='validation')
    >>> 
    >>> logger = AuditLogger()
    >>> logger.log_event('data_processing', 'validation_completed', {'records': 1000})
"""

from src.governance.lineage import LineageTracker, LineageEntry
from src.governance.audit import AuditLogger, AuditEntry

__all__ = [
    'LineageTracker',
    'LineageEntry',
    'AuditLogger',
    'AuditEntry',
]
