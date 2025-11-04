"""
Data Lineage Tracker.

Tracks data transformations and dependencies throughout
the processing pipeline.

Example:
    >>> tracker = LineageTracker()
    >>> 
    >>> # Track data load
    >>> tracker.track_load('tipificador.xlsx', records=1000)
    >>> 
    >>> # Track transformation
    >>> tracker.track_transformation(
    ...     source='tipificador_raw',
    ...     target='tipificador_valid',
    ...     operation='validation',
    ...     records_in=1000,
    ...     records_out=950
    ... )
    >>> 
    >>> # Export lineage
    >>> tracker.export_lineage(Path('lineage.json'))
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class LineageEntry:
    """
    Single lineage entry.
    
    Records a data transformation or operation.
    """
    
    # Identity
    entry_id: str
    timestamp: datetime
    
    # Operation
    operation_type: str  # load, transform, validate, aggregate, export
    operation_name: str
    
    # Data flow
    source: Optional[str] = None
    target: Optional[str] = None
    
    # Metadata
    records_in: Optional[int] = None
    records_out: Optional[int] = None
    columns_in: Optional[List[str]] = None
    columns_out: Optional[List[str]] = None
    
    # Details
    transformation_logic: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # User/system
    user: str = 'system'
    pipeline: Optional[str] = None
    stage: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class LineageTracker:
    """
    Data lineage tracker.
    
    Maintains complete history of data transformations
    and dependencies.
    """
    
    def __init__(self):
        """Initialize lineage tracker."""
        self.entries: List[LineageEntry] = []
        self.logger = logging.getLogger(f"{__name__}.LineageTracker")
        self._entry_counter = 0
    
    def track_load(
        self,
        source: str,
        target: str = None,
        records: int = None,
        columns: List[str] = None,
        **kwargs
    ) -> LineageEntry:
        """
        Track data load operation.
        
        Args:
            source: Source file/database
            target: Target DataFrame/table name
            records: Number of records loaded
            columns: List of columns
            **kwargs: Additional metadata
        
        Returns:
            Created LineageEntry
        """
        entry = LineageEntry(
            entry_id=self._generate_id('load'),
            timestamp=datetime.now(),
            operation_type='load',
            operation_name='Data Load',
            source=source,
            target=target or source,
            records_in=0,
            records_out=records,
            columns_out=columns,
            parameters=kwargs
        )
        
        self.entries.append(entry)
        self.logger.debug(f"📥 Tracked load: {source} → {target} ({records:,} records)")
        
        return entry
    
    def track_transformation(
        self,
        source: str,
        target: str,
        operation: str,
        records_in: int = None,
        records_out: int = None,
        transformation_logic: str = None,
        **kwargs
    ) -> LineageEntry:
        """
        Track data transformation.
        
        Args:
            source: Source DataFrame/table
            target: Target DataFrame/table
            operation: Operation name
            records_in: Input record count
            records_out: Output record count
            transformation_logic: Description of transformation
            **kwargs: Additional metadata
        
        Returns:
            Created LineageEntry
        """
        entry = LineageEntry(
            entry_id=self._generate_id('transform'),
            timestamp=datetime.now(),
            operation_type='transform',
            operation_name=operation,
            source=source,
            target=target,
            records_in=records_in,
            records_out=records_out,
            transformation_logic=transformation_logic,
            parameters=kwargs
        )
        
        self.entries.append(entry)
        
        # Log with data change info
        if records_in and records_out:
            change = records_out - records_in
            pct = (change / records_in * 100) if records_in > 0 else 0
            self.logger.debug(
                f"🔄 Tracked transformation: {source} → {target} "
                f"({records_in:,} → {records_out:,}, {pct:+.1f}%)"
            )
        else:
            self.logger.debug(f"🔄 Tracked transformation: {source} → {target}")
        
        return entry
    
    def track_validation(
        self,
        source: str,
        valid_target: str,
        invalid_target: str,
        records_in: int,
        valid_count: int,
        invalid_count: int,
        **kwargs
    ) -> LineageEntry:
        """
        Track validation operation.
        
        Args:
            source: Source DataFrame
            valid_target: Valid records target
            invalid_target: Invalid records target
            records_in: Input record count
            valid_count: Valid record count
            invalid_count: Invalid record count
            **kwargs: Additional metadata
        
        Returns:
            Created LineageEntry
        """
        entry = LineageEntry(
            entry_id=self._generate_id('validate'),
            timestamp=datetime.now(),
            operation_type='validate',
            operation_name='Data Validation',
            source=source,
            target=f"{valid_target} + {invalid_target}",
            records_in=records_in,
            records_out=records_in,  # Total preserved
            transformation_logic=f"Split: {valid_count} valid, {invalid_count} invalid",
            parameters={
                'valid_target': valid_target,
                'invalid_target': invalid_target,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'valid_rate': valid_count / records_in if records_in > 0 else 0,
                **kwargs
            }
        )
        
        self.entries.append(entry)
        self.logger.debug(
            f"✓ Tracked validation: {source} → "
            f"{valid_count:,} valid + {invalid_count:,} invalid"
        )
        
        return entry
    
    def track_export(
        self,
        source: str,
        target: str,
        records: int,
        format: str = 'xlsx',
        **kwargs
    ) -> LineageEntry:
        """
        Track data export.
        
        Args:
            source: Source DataFrame
            target: Target file path
            records: Number of records exported
            format: Export format
            **kwargs: Additional metadata
        
        Returns:
            Created LineageEntry
        """
        entry = LineageEntry(
            entry_id=self._generate_id('export'),
            timestamp=datetime.now(),
            operation_type='export',
            operation_name=f'Export to {format.upper()}',
            source=source,
            target=target,
            records_in=records,
            records_out=records,
            parameters={'format': format, **kwargs}
        )
        
        self.entries.append(entry)
        self.logger.debug(f"📤 Tracked export: {source} → {target} ({records:,} records)")
        
        return entry
    
    def get_lineage_for(self, target: str) -> List[LineageEntry]:
        """
        Get complete lineage for a dataset.
        
        Args:
            target: Target dataset name
        
        Returns:
            List of lineage entries leading to target
        """
        # Simple implementation: get all entries where target matches
        # In production, would implement graph traversal
        return [entry for entry in self.entries if entry.target == target]
    
    def get_recent_entries(self, count: int = 10) -> List[LineageEntry]:
        """Get most recent lineage entries."""
        return sorted(self.entries, key=lambda e: e.timestamp, reverse=True)[:count]
    
    def export_lineage(self, output_path: Path) -> None:
        """
        Export lineage as JSON.
        
        Args:
            output_path: Output file path
        """
        data = {
            'exported_at': datetime.now().isoformat(),
            'entry_count': len(self.entries),
            'entries': [entry.to_dict() for entry in self.entries]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ Lineage exported: {output_path} ({len(self.entries)} entries)")
    
    def _generate_id(self, operation_type: str) -> str:
        """Generate unique entry ID."""
        self._entry_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{operation_type}_{timestamp}_{self._entry_counter:04d}"
    
    def summary(self) -> Dict[str, Any]:
        """Get lineage summary."""
        by_type = {}
        for entry in self.entries:
            by_type[entry.operation_type] = by_type.get(entry.operation_type, 0) + 1
        
        return {
            'total_entries': len(self.entries),
            'by_type': by_type,
            'first_entry': self.entries[0].timestamp if self.entries else None,
            'last_entry': self.entries[-1].timestamp if self.entries else None,
        }


# Export
__all__ = ['LineageTracker', 'LineageEntry']
