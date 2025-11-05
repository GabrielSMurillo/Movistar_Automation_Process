"""
Advanced Analytics Module.

Provides comprehensive data analytics capabilities:
- Data profiling and quality metrics
- Anomaly detection
- Trend analysis
- Automated insight generation

Example:
    >>> from src.analytics import DataProfiler, QualityMonitor
    >>> 
    >>> profiler = DataProfiler()
    >>> profile = profiler.profile_dataframe(df, 'Tipificador')
    >>> 
    >>> monitor = QualityMonitor()
    >>> quality_report = monitor.assess_quality(df)
"""

from src.analytics.profiler import DataProfiler, ColumnProfile, DataProfile
from src.analytics.quality_monitor import QualityMonitor, QualityReport, QualityIssue

__all__ = [
    'DataProfiler',
    'ColumnProfile',
    'DataProfile',
    'QualityMonitor',
    'QualityReport',
    'QualityIssue',
]
