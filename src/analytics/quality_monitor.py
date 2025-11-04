"""
Data Quality Monitor.

Automated quality assessment with configurable rules and thresholds.
Generates quality reports and alerts for data issues.

Example:
    >>> monitor = QualityMonitor()
    >>> report = monitor.assess_quality(df)
    >>> 
    >>> if report.has_critical_issues():
    ...     print(f"Critical issues found: {report.critical_count}")
    >>> 
    >>> report.export_report(Path('quality_report.xlsx'))
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityIssue:
    """
    Single quality issue.
    
    Attributes:
        severity: CRITICAL, HIGH, MEDIUM, LOW
        category: Type of issue (null_rate, duplicates, outliers, etc.)
        column: Affected column (if applicable)
        description: Human-readable description
        value: Measured value
        threshold: Threshold that was exceeded
        recommendation: How to fix
    """
    
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    column: Optional[str]
    description: str
    value: Any
    threshold: Any
    recommendation: str
    detected_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'severidad': self.severity,
            'categoria': self.category,
            'columna': self.column or 'N/A',
            'descripcion': self.description,
            'valor_medido': str(self.value),
            'umbral': str(self.threshold),
            'recomendacion': self.recommendation,
            'detectado': self.detected_at.strftime('%Y-%m-%d %H:%M:%S'),
        }


@dataclass
class QualityReport:
    """
    Complete quality assessment report.
    
    Contains all detected issues organized by severity.
    """
    
    dataset_name: str
    issues: List[QualityIssue] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.now)
    
    # Metrics
    total_rows: int = 0
    total_columns: int = 0
    
    @property
    def critical_issues(self) -> List[QualityIssue]:
        """Get critical issues."""
        return [issue for issue in self.issues if issue.severity == 'CRITICAL']
    
    @property
    def high_issues(self) -> List[QualityIssue]:
        """Get high severity issues."""
        return [issue for issue in self.issues if issue.severity == 'HIGH']
    
    @property
    def medium_issues(self) -> List[QualityIssue]:
        """Get medium severity issues."""
        return [issue for issue in self.issues if issue.severity == 'MEDIUM']
    
    @property
    def low_issues(self) -> List[QualityIssue]:
        """Get low severity issues."""
        return [issue for issue in self.issues if issue.severity == 'LOW']
    
    @property
    def critical_count(self) -> int:
        """Count critical issues."""
        return len(self.critical_issues)
    
    @property
    def high_count(self) -> int:
        """Count high issues."""
        return len(self.high_issues)
    
    @property
    def total_issues(self) -> int:
        """Total issue count."""
        return len(self.issues)
    
    def has_critical_issues(self) -> bool:
        """Check if has critical issues."""
        return self.critical_count > 0
    
    def has_issues(self) -> bool:
        """Check if has any issues."""
        return self.total_issues > 0
    
    def add_issue(self, issue: QualityIssue) -> None:
        """Add an issue."""
        self.issues.append(issue)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'dataset': self.dataset_name,
            'filas': f"{self.total_rows:,}",
            'columnas': self.total_columns,
            'total_problemas': self.total_issues,
            'criticos': self.critical_count,
            'altos': self.high_count,
            'medios': len(self.medium_issues),
            'bajos': len(self.low_issues),
            'verificado': self.checked_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    
    def export_report(self, output_path: Path) -> None:
        """
        Export quality report as Excel.
        
        Args:
            output_path: Output file path
        """
        sheets = {}
        
        # Sheet 1: Summary
        sheets['Resumen'] = pd.DataFrame([self.summary()])
        
        # Sheet 2: All issues
        if self.issues:
            issue_data = [issue.to_dict() for issue in self.issues]
            sheets['Problemas'] = pd.DataFrame(issue_data)
        
        # Sheet 3: Critical issues only
        if self.critical_issues:
            critical_data = [issue.to_dict() for issue in self.critical_issues]
            sheets['Críticos'] = pd.DataFrame(critical_data)
        
        # Save
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                
                # Header format
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#FF6B6B' if sheet_name == 'Críticos' else '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })
                
                for col_num, value in enumerate(df.columns):
                    worksheet.write(0, col_num, value, header_format)
                    max_len = max(df[value].astype(str).apply(len).max(), len(str(value)))
                    worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
        
        logger.info(f"✅ Quality report exported: {output_path}")


class QualityMonitor:
    """
    Automated data quality monitor.
    
    Checks data against configurable quality rules and
    generates comprehensive quality reports.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize quality monitor.
        
        Args:
            config: Monitor configuration
        """
        self.config = config or {}
        
        # Thresholds
        self.max_null_rate = self.config.get('max_null_rate', 0.30)
        self.max_duplicate_rate = self.config.get('max_duplicate_rate', 0.15)
        self.min_unique_rate = self.config.get('min_unique_rate', 0.05)
        self.max_outlier_rate = self.config.get('max_outlier_rate', 0.10)
        
        self.logger = logging.getLogger(f"{__name__}.QualityMonitor")
    
    def assess_quality(
        self,
        df: pd.DataFrame,
        name: str = "DataFrame"
    ) -> QualityReport:
        """
        Assess data quality.
        
        Args:
            df: DataFrame to assess
            name: Dataset name
        
        Returns:
            QualityReport with all detected issues
        """
        self.logger.info("=" * 80)
        self.logger.info(f"🔍 QUALITY ASSESSMENT: {name}")
        self.logger.info("=" * 80)
        
        report = QualityReport(
            dataset_name=name,
            total_rows=len(df),
            total_columns=len(df.columns)
        )
        
        # Check null rates
        self._check_null_rates(df, report)
        
        # Check duplicates
        self._check_duplicates(df, report)
        
        # Check cardinality
        self._check_cardinality(df, report)
        
        # Check outliers (numeric columns)
        self._check_outliers(df, report)
        
        # Check data types
        self._check_data_types(df, report)
        
        # Log summary
        self._log_quality_summary(report)
        
        return report
    
    def _check_null_rates(self, df: pd.DataFrame, report: QualityReport) -> None:
        """Check for high null rates."""
        null_rates = df.isnull().mean()
        
        for col, null_rate in null_rates.items():
            if null_rate > self.max_null_rate:
                report.add_issue(QualityIssue(
                    severity='HIGH',
                    category='null_rate',
                    column=col,
                    description=f'Alta tasa de valores nulos en columna {col}',
                    value=f"{null_rate:.2%}",
                    threshold=f"{self.max_null_rate:.2%}",
                    recommendation=f'Revisar origen de datos o considerar imputación'
                ))
            elif null_rate > self.max_null_rate / 2:
                report.add_issue(QualityIssue(
                    severity='MEDIUM',
                    category='null_rate',
                    column=col,
                    description=f'Tasa moderada de nulos en {col}',
                    value=f"{null_rate:.2%}",
                    threshold=f"{self.max_null_rate:.2%}",
                    recommendation='Monitorear tendencia'
                ))
    
    def _check_duplicates(self, df: pd.DataFrame, report: QualityReport) -> None:
        """Check for duplicate rows."""
        dup_count = df.duplicated().sum()
        dup_rate = dup_count / len(df) if len(df) > 0 else 0
        
        if dup_rate > self.max_duplicate_rate:
            report.add_issue(QualityIssue(
                severity='CRITICAL',
                category='duplicates',
                column=None,
                description='Tasa de duplicados excede el umbral',
                value=f"{dup_count:,} ({dup_rate:.2%})",
                threshold=f"{self.max_duplicate_rate:.2%}",
                recommendation='Ejecutar proceso de deduplicación antes de procesar'
            ))
    
    def _check_cardinality(self, df: pd.DataFrame, report: QualityReport) -> None:
        """Check for low cardinality issues."""
        for col in df.columns:
            unique_count = df[col].nunique()
            unique_rate = unique_count / len(df) if len(df) > 0 else 0
            
            # Low cardinality (but not intentional categories)
            if unique_rate < self.min_unique_rate and unique_count > 1:
                report.add_issue(QualityIssue(
                    severity='LOW',
                    category='cardinality',
                    column=col,
                    description=f'Baja cardinalidad en {col}',
                    value=f"{unique_count} valores únicos ({unique_rate:.2%})",
                    threshold=f"{self.min_unique_rate:.2%}",
                    recommendation='Verificar si es correcto o hay error de captura'
                ))
    
    def _check_outliers(self, df: pd.DataFrame, report: QualityReport) -> None:
        """Check for outliers in numeric columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = df[col].dropna()
            
            if len(series) < 4:  # Need at least 4 values for quartiles
                continue
            
            # IQR method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            
            outliers = ((series < lower) | (series > upper)).sum()
            outlier_rate = outliers / len(series)
            
            if outlier_rate > self.max_outlier_rate:
                report.add_issue(QualityIssue(
                    severity='MEDIUM',
                    category='outliers',
                    column=col,
                    description=f'Outliers detectados en {col}',
                    value=f"{outliers:,} ({outlier_rate:.2%})",
                    threshold=f"{self.max_outlier_rate:.2%}",
                    recommendation='Revisar valores extremos y validar con negocio'
                ))
    
    def _check_data_types(self, df: pd.DataFrame, report: QualityReport) -> None:
        """Check for potential data type issues."""
        # Check for numeric stored as object
        for col in df.select_dtypes(include=['object']).columns:
            # Try to convert to numeric
            try:
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if numeric_series.notna().sum() > len(df) * 0.8:  # 80% are numeric
                    report.add_issue(QualityIssue(
                        severity='LOW',
                        category='data_type',
                        column=col,
                        description=f'Columna {col} parece numérica pero está como texto',
                        value='object',
                        threshold='numeric',
                        recommendation='Convertir a tipo numérico para optimizar memoria'
                    ))
            except:
                pass
    
    def _log_quality_summary(self, report: QualityReport) -> None:
        """Log quality summary."""
        self.logger.info(f"\n📊 Dataset: {report.dataset_name}")
        self.logger.info(f"   Total problemas: {report.total_issues}")
        
        if report.critical_count > 0:
            self.logger.error(f"   🔴 Críticos: {report.critical_count}")
        if report.high_count > 0:
            self.logger.warning(f"   🟠 Altos: {report.high_count}")
        if len(report.medium_issues) > 0:
            self.logger.info(f"   🟡 Medios: {len(report.medium_issues)}")
        if len(report.low_issues) > 0:
            self.logger.info(f"   🟢 Bajos: {len(report.low_issues)}")
        
        if not report.has_issues():
            self.logger.info("   ✅ No se detectaron problemas de calidad")
        
        self.logger.info("=" * 80)


# Export
__all__ = ['QualityMonitor', 'QualityReport', 'QualityIssue']
