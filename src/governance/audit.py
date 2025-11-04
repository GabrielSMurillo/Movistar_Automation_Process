"""
Audit Logger for governance and compliance.

Maintains audit trail of all system operations, user actions,
and data changes.

Example:
    >>> logger = AuditLogger()
    >>> 
    >>> # Log user action
    >>> logger.log_event(
    ...     'user_action',
    ...     'file_uploaded',
    ...     {'filename': 'tipificador.xlsx', 'size_mb': 2.5},
    ...     user='jperez'
    ... )
    >>> 
    >>> # Log system event
    >>> logger.log_event(
    ...     'system',
    ...     'validation_completed',
    ...     {'records_processed': 1000, 'errors': 50}
    ... )
    >>> 
    >>> # Export audit log
    >>> logger.export_log(Path('audit.xlsx'))
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """
    Single audit entry.
    
    Records a system or user event.
    """
    
    # Identity
    entry_id: str
    timestamp: datetime
    
    # Event
    category: str  # user_action, system, data_change, security, error
    event_type: str
    description: str = ''
    
    # Context
    user: str = 'system'
    source: str = 'movistar_automation'
    
    # Details
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Impact
    severity: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AuditLogger:
    """
    Audit logger for governance.
    
    Maintains complete audit trail of system operations
    and user actions for compliance and debugging.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            output_dir: Directory for audit logs
        """
        self.entries: List[AuditEntry] = []
        self.output_dir = output_dir or Path('audit_logs')
        self.logger = logging.getLogger(f"{__name__}.AuditLogger")
        self._entry_counter = 0
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def log_event(
        self,
        category: str,
        event_type: str,
        metadata: Dict[str, Any] = None,
        description: str = '',
        user: str = 'system',
        severity: str = 'INFO'
    ) -> AuditEntry:
        """
        Log an event.
        
        Args:
            category: Event category
            event_type: Type of event
            metadata: Additional event metadata
            description: Human-readable description
            user: User who triggered event
            severity: Event severity level
        
        Returns:
            Created AuditEntry
        """
        entry = AuditEntry(
            entry_id=self._generate_id(),
            timestamp=datetime.now(),
            category=category,
            event_type=event_type,
            description=description,
            user=user,
            metadata=metadata or {},
            severity=severity
        )
        
        self.entries.append(entry)
        
        # Log to standard logger
        log_msg = f"[AUDIT] {category}.{event_type}"
        if description:
            log_msg += f": {description}"
        
        if severity == 'CRITICAL':
            self.logger.critical(log_msg)
        elif severity == 'ERROR':
            self.logger.error(log_msg)
        elif severity == 'WARNING':
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)
        
        return entry
    
    def log_user_action(
        self,
        action: str,
        user: str,
        metadata: Dict[str, Any] = None
    ) -> AuditEntry:
        """
        Log user action.
        
        Args:
            action: Action performed
            user: User who performed action
            metadata: Additional metadata
        
        Returns:
            Created AuditEntry
        """
        return self.log_event(
            category='user_action',
            event_type=action,
            user=user,
            metadata=metadata
        )
    
    def log_data_change(
        self,
        change_type: str,
        details: Dict[str, Any],
        user: str = 'system'
    ) -> AuditEntry:
        """
        Log data change.
        
        Args:
            change_type: Type of change (insert, update, delete, transform)
            details: Change details
            user: User who made change
        
        Returns:
            Created AuditEntry
        """
        return self.log_event(
            category='data_change',
            event_type=change_type,
            metadata=details,
            user=user
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        metadata: Dict[str, Any] = None
    ) -> AuditEntry:
        """
        Log error event.
        
        Args:
            error_type: Type of error
            error_message: Error message
            metadata: Additional error context
        
        Returns:
            Created AuditEntry
        """
        return self.log_event(
            category='error',
            event_type=error_type,
            description=error_message,
            metadata=metadata or {},
            severity='ERROR'
        )
    
    def get_events_by_category(self, category: str) -> List[AuditEntry]:
        """Get events by category."""
        return [entry for entry in self.entries if entry.category == category]
    
    def get_events_by_user(self, user: str) -> List[AuditEntry]:
        """Get events by user."""
        return [entry for entry in self.entries if entry.user == user]
    
    def get_recent_events(self, count: int = 20) -> List[AuditEntry]:
        """Get most recent events."""
        return sorted(self.entries, key=lambda e: e.timestamp, reverse=True)[:count]
    
    def export_log(self, output_path: Path = None) -> None:
        """
        Export audit log as Excel.
        
        Args:
            output_path: Output file path (default: timestamped file)
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"audit_log_{timestamp}.xlsx"
        
        # Convert entries to DataFrame
        data = []
        for entry in self.entries:
            row = {
                'ID': entry.entry_id,
                'Timestamp': entry.timestamp,
                'Categoría': entry.category,
                'Evento': entry.event_type,
                'Usuario': entry.user,
                'Severidad': entry.severity,
                'Descripción': entry.description,
                'Metadata': json.dumps(entry.metadata, ensure_ascii=False)
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Save
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Audit Log', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Audit Log']
            
            # Header format
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num, value, header_format)
                max_len = max(df[value].astype(str).apply(len).max(), len(str(value)))
                worksheet.set_column(col_num, col_num, min(max_len + 2, 60))
        
        self.logger.info(f"✅ Audit log exported: {output_path} ({len(self.entries)} entries)")
    
    def export_json(self, output_path: Path = None) -> None:
        """
        Export audit log as JSON.
        
        Args:
            output_path: Output file path (default: timestamped file)
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.output_dir / f"audit_log_{timestamp}.json"
        
        data = {
            'exported_at': datetime.now().isoformat(),
            'entry_count': len(self.entries),
            'entries': [entry.to_dict() for entry in self.entries]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"✅ Audit log (JSON) exported: {output_path}")
    
    def _generate_id(self) -> str:
        """Generate unique entry ID."""
        self._entry_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"AUDIT_{timestamp}_{self._entry_counter:06d}"
    
    def summary(self) -> Dict[str, Any]:
        """Get audit summary."""
        by_category = {}
        by_severity = {}
        
        for entry in self.entries:
            by_category[entry.category] = by_category.get(entry.category, 0) + 1
            by_severity[entry.severity] = by_severity.get(entry.severity, 0) + 1
        
        return {
            'total_entries': len(self.entries),
            'by_category': by_category,
            'by_severity': by_severity,
            'first_entry': self.entries[0].timestamp if self.entries else None,
            'last_entry': self.entries[-1].timestamp if self.entries else None,
        }


# Export
__all__ = ['AuditLogger', 'AuditEntry']
