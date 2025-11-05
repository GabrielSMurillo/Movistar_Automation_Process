"""
Data Profiler for automated data profiling and analysis.

Generates comprehensive profiles with statistics, distributions,
and quality indicators for DataFrames.

Example:
    >>> profiler = DataProfiler()
    >>> profile = profiler.profile_dataframe(df, 'Tipificador')
    >>> 
    >>> print(profile.summary())
    >>> profile.export_report(Path('profile.xlsx'))
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ColumnProfile:
    """
    Profile for a single column.
    
    Contains statistics, quality metrics, and insights
    for one DataFrame column.
    """
    
    # Basic info
    name: str
    dtype: str
    pandas_dtype: str
    
    # Counts
    total_count: int
    null_count: int
    unique_count: int
    
    # Rates
    null_rate: float
    unique_rate: float
    
    # Numeric statistics (if applicable)
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    q25: Optional[float] = None
    q75: Optional[float] = None
    
    # Categorical statistics (if applicable)
    top_values: Optional[Dict[str, int]] = None
    mode: Optional[Any] = None
    mode_frequency: Optional[int] = None
    
    # Quality flags
    has_high_null_rate: bool = False
    has_low_cardinality: bool = False
    has_outliers: bool = False
    outlier_count: int = 0
    
    # Distribution info
    is_numeric: bool = False
    is_categorical: bool = False
    is_datetime: bool = False
    is_boolean: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'columna': self.name,
            'tipo': self.dtype,
            'total_registros': self.total_count,
            'valores_nulos': self.null_count,
            'tasa_nulos': f"{self.null_rate:.2%}",
            'valores_unicos': self.unique_count,
            'tasa_unicidad': f"{self.unique_rate:.2%}",
            'media': self.mean,
            'mediana': self.median,
            'desv_std': self.std,
            'min': self.min_value,
            'max': self.max_value,
            'valores_mas_frecuentes': self.top_values,
            'tiene_alta_tasa_nulos': self.has_high_null_rate,
            'tiene_baja_cardinalidad': self.has_low_cardinality,
            'tiene_outliers': self.has_outliers,
            'cantidad_outliers': self.outlier_count,
        }


@dataclass
class DataProfile:
    """
    Complete profile for a DataFrame.
    
    Contains column profiles, overall statistics,
    and data quality assessment.
    """
    
    name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile] = field(default_factory=list)
    
    # Overall stats
    memory_usage_bytes: int = 0
    duplicate_row_count: int = 0
    duplicate_row_rate: float = 0.0
    
    # Quality metrics
    avg_null_rate: float = 0.0
    max_null_rate: float = 0.0
    
    # Timestamps
    profiled_at: datetime = field(default_factory=datetime.now)
    
    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            'nombre': self.name,
            'filas': f"{self.row_count:,}",
            'columnas': self.column_count,
            'memoria_mb': f"{self.memory_usage_bytes / 1024**2:.2f}",
            'duplicados': f"{self.duplicate_row_count:,} ({self.duplicate_row_rate:.1%})",
            'tasa_nulos_promedio': f"{self.avg_null_rate:.2%}",
            'tasa_nulos_maxima': f"{self.max_null_rate:.2%}",
            'perfilado_en': self.profiled_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    
    def quality_score(self) -> float:
        """
        Calculate overall quality score (0-100).
        
        Returns:
            Quality score percentage
        """
        # Start with perfect score
        score = 100.0
        
        # Penalize for nulls
        score -= self.avg_null_rate * 30  # Up to -30 points
        
        # Penalize for duplicates
        score -= self.duplicate_row_rate * 20  # Up to -20 points
        
        # Penalize for low cardinality columns
        low_card_cols = sum(1 for col in self.columns if col.has_low_cardinality)
        score -= (low_card_cols / self.column_count) * 10  # Up to -10 points
        
        # Penalize for outliers
        outlier_cols = sum(1 for col in self.columns if col.has_outliers)
        score -= (outlier_cols / self.column_count) * 10  # Up to -10 points
        
        return max(0.0, score)
    
    def export_report(self, output_path: Path) -> None:
        """
        Export profile as Excel report.
        
        Args:
            output_path: Path for output Excel file
        """
        # Create report sheets
        sheets = {}
        
        # Sheet 1: Summary
        summary_data = [self.summary()]
        sheets['Resumen'] = pd.DataFrame(summary_data)
        
        # Sheet 2: Column profiles
        column_data = [col.to_dict() for col in self.columns]
        sheets['Perfiles de Columnas'] = pd.DataFrame(column_data)
        
        # Sheet 3: Quality issues
        issues = []
        for col in self.columns:
            if col.has_high_null_rate:
                issues.append({
                    'columna': col.name,
                    'problema': 'Alta tasa de nulos',
                    'valor': f"{col.null_rate:.2%}",
                    'severidad': 'Alta'
                })
            if col.has_low_cardinality:
                issues.append({
                    'columna': col.name,
                    'problema': 'Baja cardinalidad',
                    'valor': col.unique_count,
                    'severidad': 'Media'
                })
            if col.has_outliers:
                issues.append({
                    'columna': col.name,
                    'problema': 'Outliers detectados',
                    'valor': col.outlier_count,
                    'severidad': 'Media'
                })
        
        sheets['Problemas de Calidad'] = pd.DataFrame(issues)
        
        # Save report
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                
                # Header format
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })
                
                for col_num, value in enumerate(df.columns):
                    worksheet.write(0, col_num, value, header_format)
                    
                    max_len = max(
                        df[value].astype(str).apply(len).max(),
                        len(str(value))
                    )
                    worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
        
        logger.info(f"✅ Profile report exported: {output_path}")


class DataProfiler:
    """
    Automated data profiler.
    
    Generates comprehensive profiles with statistics,
    distributions, and quality indicators.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize profiler.
        
        Args:
            config: Profiler configuration
        """
        self.config = config or {}
        self.high_null_threshold = self.config.get('high_null_threshold', 0.30)
        self.low_cardinality_threshold = self.config.get('low_cardinality_threshold', 10)
        self.outlier_method = self.config.get('outlier_method', 'iqr')  # iqr or zscore
        self.logger = logging.getLogger(f"{__name__}.DataProfiler")
    
    def profile_dataframe(
        self,
        df: pd.DataFrame,
        name: str = "DataFrame"
    ) -> DataProfile:
        """
        Generate comprehensive profile for DataFrame.
        
        Args:
            df: DataFrame to profile
            name: Descriptive name
        
        Returns:
            DataProfile with complete statistics
        
        Example:
            >>> profiler = DataProfiler()
            >>> profile = profiler.profile_dataframe(df, 'Tipificador')
            >>> print(f"Quality Score: {profile.quality_score():.1f}%")
        """
        self.logger.info("=" * 80)
        self.logger.info(f"📊 PROFILING: {name}")
        self.logger.info("=" * 80)
        
        # Profile each column
        column_profiles = []
        for col in df.columns:
            profile = self._profile_column(df, col)
            column_profiles.append(profile)
        
        # Overall statistics
        memory_usage = df.memory_usage(deep=True).sum()
        duplicate_count = df.duplicated().sum()
        duplicate_rate = duplicate_count / len(df) if len(df) > 0 else 0
        
        # Quality metrics
        null_rates = [col.null_rate for col in column_profiles]
        avg_null_rate = np.mean(null_rates) if null_rates else 0
        max_null_rate = max(null_rates) if null_rates else 0
        
        # Create profile
        profile = DataProfile(
            name=name,
            row_count=len(df),
            column_count=len(df.columns),
            columns=column_profiles,
            memory_usage_bytes=memory_usage,
            duplicate_row_count=duplicate_count,
            duplicate_row_rate=duplicate_rate,
            avg_null_rate=avg_null_rate,
            max_null_rate=max_null_rate,
        )
        
        # Log summary
        self._log_profile_summary(profile)
        
        return profile
    
    def _profile_column(self, df: pd.DataFrame, col: str) -> ColumnProfile:
        """
        Profile a single column.
        
        Args:
            df: DataFrame
            col: Column name
        
        Returns:
            ColumnProfile
        """
        series = df[col]
        
        # Basic stats
        total_count = len(series)
        null_count = series.isnull().sum()
        null_rate = null_count / total_count if total_count > 0 else 0
        unique_count = series.nunique()
        unique_rate = unique_count / total_count if total_count > 0 else 0
        
        # Determine type
        is_numeric = pd.api.types.is_numeric_dtype(series)
        is_datetime = pd.api.types.is_datetime64_any_dtype(series)
        is_boolean = pd.api.types.is_bool_dtype(series)
        is_categorical = not (is_numeric or is_datetime or is_boolean)
        
        # Create base profile
        profile = ColumnProfile(
            name=col,
            dtype=self._get_dtype_category(series),
            pandas_dtype=str(series.dtype),
            total_count=total_count,
            null_count=null_count,
            unique_count=unique_count,
            null_rate=null_rate,
            unique_rate=unique_rate,
            is_numeric=is_numeric,
            is_categorical=is_categorical,
            is_datetime=is_datetime,
            is_boolean=is_boolean,
        )
        
        # Numeric statistics
        if is_numeric and unique_count > 0:
            profile.mean = series.mean()
            profile.median = series.median()
            profile.std = series.std()
            profile.min_value = series.min()
            profile.max_value = series.max()
            profile.q25 = series.quantile(0.25)
            profile.q75 = series.quantile(0.75)
            
            # Detect outliers
            outlier_count = self._detect_outliers(series)
            profile.has_outliers = outlier_count > 0
            profile.outlier_count = outlier_count
        
        # Categorical statistics
        if is_categorical or is_boolean:
            value_counts = series.value_counts()
            profile.top_values = value_counts.head(10).to_dict()
            if len(value_counts) > 0:
                profile.mode = value_counts.index[0]
                profile.mode_frequency = value_counts.iloc[0]
        
        # Datetime statistics
        if is_datetime:
            profile.min_value = series.min()
            profile.max_value = series.max()
        
        # Quality flags
        profile.has_high_null_rate = null_rate > self.high_null_threshold
        profile.has_low_cardinality = unique_count < self.low_cardinality_threshold
        
        return profile
    
    def _get_dtype_category(self, series: pd.Series) -> str:
        """Categorize dtype."""
        if pd.api.types.is_numeric_dtype(series):
            return 'Numérico'
        elif pd.api.types.is_datetime64_any_dtype(series):
            return 'Fecha/Hora'
        elif pd.api.types.is_bool_dtype(series):
            return 'Booleano'
        else:
            return 'Texto'
    
    def _detect_outliers(self, series: pd.Series) -> int:
        """
        Detect outliers using IQR method.
        
        Args:
            series: Numeric series
        
        Returns:
            Count of outliers
        """
        if self.outlier_method == 'iqr':
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (series < lower_bound) | (series > upper_bound)
            return outliers.sum()
        
        elif self.outlier_method == 'zscore':
            # Z-score method
            mean = series.mean()
            std = series.std()
            
            if std == 0:
                return 0
            
            z_scores = np.abs((series - mean) / std)
            outliers = z_scores > 3
            return outliers.sum()
        
        else:
            return 0
    
    def _log_profile_summary(self, profile: DataProfile) -> None:
        """Log profile summary."""
        self.logger.info(f"\n📊 Dataset: {profile.name}")
        self.logger.info(f"   Filas: {profile.row_count:,}")
        self.logger.info(f"   Columnas: {profile.column_count}")
        self.logger.info(f"   Memoria: {profile.memory_usage_bytes / 1024**2:.2f} MB")
        self.logger.info(f"   Duplicados: {profile.duplicate_row_count:,} ({profile.duplicate_row_rate:.1%})")
        self.logger.info(f"   Tasa nulos promedio: {profile.avg_null_rate:.2%}")
        self.logger.info(f"   Quality Score: {profile.quality_score():.1f}/100")
        
        # Quality issues
        high_null_cols = [col.name for col in profile.columns if col.has_high_null_rate]
        if high_null_cols:
            self.logger.warning(f"   ⚠️  Columnas con alta tasa de nulos: {len(high_null_cols)}")
        
        outlier_cols = [col.name for col in profile.columns if col.has_outliers]
        if outlier_cols:
            self.logger.warning(f"   ⚠️  Columnas con outliers: {len(outlier_cols)}")
        
        self.logger.info("=" * 80)
    
    def compare_profiles(
        self,
        profile1: DataProfile,
        profile2: DataProfile
    ) -> Dict[str, Any]:
        """
        Compare two data profiles.
        
        Useful for comparing before/after transformations.
        
        Args:
            profile1: First profile
            profile2: Second profile
        
        Returns:
            Comparison dictionary
        """
        return {
            'row_count_change': profile2.row_count - profile1.row_count,
            'row_count_change_pct': (profile2.row_count - profile1.row_count) / profile1.row_count if profile1.row_count > 0 else 0,
            'column_count_change': profile2.column_count - profile1.column_count,
            'duplicate_change': profile2.duplicate_row_count - profile1.duplicate_row_count,
            'null_rate_change': profile2.avg_null_rate - profile1.avg_null_rate,
            'quality_score_change': profile2.quality_score() - profile1.quality_score(),
        }


# Export
__all__ = ['DataProfiler', 'ColumnProfile', 'DataProfile']
