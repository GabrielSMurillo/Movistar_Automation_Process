"""
Core data processors for the Movistar Automation System.

This module contains processors for different data sources, implementing
clean separation of concerns and business logic.
"""

import pandas as pd
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from datetime import date, datetime
from pathlib import Path

# Import core dependencies
from src.core.models import ProcessingMetrics, TipoLinea
from src.services.phone_validator import EnhancedPhoneValidator
from src.services.field_validators import FieldValidators
from src.services.service_code_mapper import ServiceCodeMapper
from src.services.novelty_detector import NoveltyDetector

logger = logging.getLogger(__name__)


class ProcessingResult:
    """Result of a processing operation."""
    
    def __init__(
        self,
        data: pd.DataFrame,
        metrics: Dict[str, Any],
        novedades: Optional[pd.DataFrame] = None
    ):
        self.data = data
        self.metrics = metrics
        self.novedades = novedades if novedades is not None else pd.DataFrame()


class BaseProcessor(ABC):
    """
    Abstract base processor with common functionality.
    
    All processors should inherit from this class and implement
    the process() method.
    """
    
    def __init__(self):
        self.phone_validator = EnhancedPhoneValidator()
        self.field_validators = FieldValidators()
        self.service_mapper = ServiceCodeMapper()
        self.novelty_detector = NoveltyDetector()
    
    @abstractmethod
    def process(
        self,
        df: pd.DataFrame,
        cols_map: Dict[str, str],
        start_date: date,
        end_date: date
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Dict[str, Any]]:
        """
        Process data.
        
        Args:
            df: Input DataFrame
            cols_map: Column name mapping
            start_date: Processing start date
            end_date: Processing end date
        
        Returns:
            Tuple of (processed_df, referidos_df, metrics)
        """
        pass
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Common cleaning operations."""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        
        return df
    
    def _extract_datetime_components(
        self,
        df: pd.DataFrame,
        timestamp_col: str = 'marca_temporal'
    ) -> pd.DataFrame:
        """Extract date and time components from timestamp."""
        if timestamp_col not in df.columns:
            logger.warning(f"Column '{timestamp_col}' not found")
            return df
        
        # Convert to datetime
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
        
        # Extract components
        df['fecha_venta'] = df[timestamp_col].dt.date
        df['hora_venta'] = df[timestamp_col].dt.time
        df['year'] = df[timestamp_col].dt.year
        df['month'] = df[timestamp_col].dt.month
        df['day'] = df[timestamp_col].dt.day
        df['hora'] = df[timestamp_col].dt.hour
        
        return df


class TipificadorProcessor(BaseProcessor):
    """
    Processor for Tipificador de Ventas data.
    
    Handles validation, cleaning, and transformation of sales data
    from the main tipificador source.
    """
    
    @staticmethod
    def process(
        df_raw: pd.DataFrame,
        cols_map: Dict[str, str],
        start_date: date,
        end_date: date
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Process tipificador data.
        
        Args:
            df_raw: Raw tipificador DataFrame
            cols_map: Column mapping dictionary
            start_date: Start date for filtering
            end_date: End date for filtering
        
        Returns:
            Tuple of (ventas_df, referidos_df, metrics)
        """
        logger.info("🔄 Processing Tipificador data...")
        start_time = datetime.now()
        
        processor = TipificadorProcessor()
        
        # 1. RENAME COLUMNS
        df = df_raw.copy()
        
        # Map columns (handle variations)
        for old_col, new_col in cols_map.items():
            matching_cols = [c for c in df.columns if old_col.lower() in c.lower()]
            if matching_cols:
                df = df.rename(columns={matching_cols[0]: new_col})
        
        # 2. CLEAN DATA
        df = processor._clean_dataframe(df)
        
        # 3. EXTRACT DATETIME
        df = processor._extract_datetime_components(df, 'marca_temporal')
        
        # 4. VALIDATE AND CLEAN PHONES
        logger.info("📞 Validating phone numbers...")
        phone_col = 'telefono_servicio'
        
        if phone_col in df.columns:
            # Clean phones and get type
            phone_results = df[phone_col].apply(
                lambda x: processor.phone_validator.validate(x)
            )
            
            # ✅ FIXED: Use correct attribute names from PhoneValidationResult
            df['telefono_limpio'] = phone_results.apply(
                lambda r: r.cleaned_phone if r.is_valid else None
            )
            df['tipo_linea'] = phone_results.apply(
                lambda r: r.tipo_linea if r.is_valid else 'INVALIDO'
            )
            df['telefono_valido'] = phone_results.apply(lambda r: r.is_valid)
        
        # 5. VALIDATE FIELDS
        logger.info("✅ Validating fields...")
        
        # Asesor validation
        if 'nombre_asesor' in df.columns:
            asesor_results = df['nombre_asesor'].apply(
                processor.field_validators.validate_asesor_name
            )
            # ✅ FIXED: Validator returns tuple (bool, str), not dict
            df['asesor_valido'] = asesor_results.apply(lambda r: r[0])
        
        # Login validation
        if 'login' in df.columns:
            login_results = df['login'].apply(
                processor.field_validators.validate_login
            )
            # ✅ FIXED: Validator returns tuple (bool, str), not dict
            df['login_valido'] = login_results.apply(lambda r: r[0])
        
        # 6. ASSIGN SERVICE CODES
        logger.info("🏷️  Assigning service codes...")
        
        if 'tipo_venta' in df.columns and 'tipo_linea' in df.columns:
            service_results = df.apply(
                lambda row: processor.service_mapper.get_code(
                    str(row.get('tipo_venta', 'TU MASCOTA')),
                    str(row.get('tipo_linea', 'MOVIL'))
                ),
                axis=1
            )
            
            df['cod_servicio'] = service_results.apply(lambda x: x[0])
            df['programa'] = service_results.apply(lambda x: x[1])
        
        # 7. DETECT REFERRALS
        df_referidos = pd.DataFrame()
        
        if 'es_referido' in df.columns:
            # Check for referrals
            referido_values = {'sí', 'si', 'yes', 's', 'y', '1', 'true'}
            df['is_referido'] = df['es_referido'].astype(str).str.lower().str.strip().isin(referido_values)
            
            # Extract referrals
            df_referidos = df[df['is_referido'] == True].copy()
            logger.info(f"  📋 Referidos encontrados: {len(df_referidos)}")
        
        # 8. SEPARATE VALID AND NOVEDADES
        logger.info("🔍 Separating valid records from novedades...")
        
        df_valid, df_novedades = processor.novelty_detector.separate_valid_and_novelties(df)
        
        logger.info(f"  ✅ Valid records: {len(df_valid)}")
        logger.info(f"  ⚠️  Novedades (invalid): {len(df_novedades)}")
        
        # 9. FILTER BY DATE RANGE
        if 'fecha_venta' in df_valid.columns:
            df_valid = df_valid[
                (df_valid['fecha_venta'] >= start_date) &
                (df_valid['fecha_venta'] <= end_date)
            ].copy()
        
        # 10. CALCULATE METRICS
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metrics = {
            'total_raw': len(df_raw),
            'total_cleaned': len(df),
            'total_valid': len(df_valid),
            'total_novedades': len(df_novedades),
            'referidos': len(df_referidos),
            'movil_count': len(df_valid[df_valid['tipo_linea'] == 'MOVIL']),
            'fija_count': len(df_valid[df_valid['tipo_linea'] == 'FIJA']),
            'processing_time_seconds': processing_time,
            'df_novedades': df_novedades,  # Include for novelty report
        }
        
        logger.info(f"✅ Tipificador processing completed in {processing_time:.2f}s")
        
        return df_valid, df_referidos, metrics


class DigitalProcessor(BaseProcessor):
    """
    Processor for Digital Sales data.
    
    Handles validation and transformation of digital channel sales.
    """
    
    @staticmethod
    def process(
        df_raw: pd.DataFrame,
        cols_map: Dict[str, str],
        start_date: date,
        end_date: date
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process digital sales data.
        
        Args:
            df_raw: Raw digital sales DataFrame
            cols_map: Column mapping dictionary
            start_date: Start date for filtering
            end_date: End date for filtering
        
        Returns:
            Tuple of (processed_df, metrics)
        """
        logger.info("🔄 Processing Digital sales data...")
        start_time = datetime.now()
        
        processor = DigitalProcessor()
        
        # 1. RENAME COLUMNS
        df = df_raw.copy()
        
        for old_col, new_col in cols_map.items():
            matching_cols = [c for c in df.columns if old_col.lower() in c.lower()]
            if matching_cols:
                df = df.rename(columns={matching_cols[0]: new_col})
        
        # 2. CLEAN DATA
        df = processor._clean_dataframe(df)
        
        # 3. PARSE DATES
        if 'fecha_venta' in df.columns:
            df['fecha_venta'] = pd.to_datetime(df['fecha_venta'], errors='coerce')
            df['fecha_venta'] = df['fecha_venta'].dt.date
        
        # 4. VALIDATE PHONES
        logger.info("📞 Validating phone numbers...")
        
        if 'telefono_servicio' in df.columns:
            phone_results = df['telefono_servicio'].apply(
                lambda x: processor.phone_validator.validate(x)
            )
            
            # ✅ FIXED: Use correct attribute names
            df['telefono_limpio'] = phone_results.apply(
                lambda r: r.cleaned_phone if r.is_valid else None
            )
            df['tipo_linea'] = phone_results.apply(
                lambda r: r.tipo_linea if r.is_valid else 'DIGITAL'
            )
            df['telefono_valido'] = phone_results.apply(lambda r: r.is_valid)
        
        # 5. ASSIGN SERVICE CODES (Digital codes)
        logger.info("🏷️  Assigning digital service codes...")
        
        if 'plan_desc' in df.columns or 'tipo_venta' in df.columns:
            plan_col = 'plan_desc' if 'plan_desc' in df.columns else 'tipo_venta'
            
            service_results = df[plan_col].apply(
                lambda x: processor.service_mapper.get_code(
                    str(x) if pd.notna(x) else 'MASCOTAS',
                    'DIGITAL'
                )
            )
            
            df['cod_servicio'] = service_results.apply(lambda x: x[0])
            df['programa'] = service_results.apply(lambda x: x[1])
        
        # 6. MARK AS DIGITAL CHANNEL
        df['base_asignada'] = 'DIGITAL'
        df['nombre_asesor'] = 'Digital'
        
        # 7. SEPARATE VALID AND NOVEDADES
        logger.info("🔍 Separating valid records from novedades...")
        
        df_valid, df_novedades = processor.novelty_detector.separate_valid_and_novelties(df)
        
        logger.info(f"  ✅ Valid records: {len(df_valid)}")
        logger.info(f"  ⚠️  Novedades (invalid): {len(df_novedades)}")
        
        # 8. FILTER BY DATE RANGE
        if 'fecha_venta' in df_valid.columns:
            df_valid = df_valid[
                (df_valid['fecha_venta'] >= start_date) &
                (df_valid['fecha_venta'] <= end_date)
            ].copy()
        
        # 9. CALCULATE METRICS
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metrics = {
            'total_raw': len(df_raw),
            'total_cleaned': len(df),
            'total_valid': len(df_valid),
            'total_novedades': len(df_novedades),
            'processing_time_seconds': processing_time,
            'df_novedades': df_novedades,
        }
        
        logger.info(f"✅ Digital processing completed in {processing_time:.2f}s")
        
        return df_valid, metrics


class HistoricalSalesProcessor(BaseProcessor):
    """
    Processor for Historical Sales data.
    
    Handles consolidation and deduplication of historical data.
    """
    
    @staticmethod
    def process(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process historical sales data.
        
        Args:
            df_raw: Raw historical data DataFrame
        
        Returns:
            Tuple of (processed_df, metrics)
        """
        logger.info("🔄 Processing Historical sales data...")
        start_time = datetime.now()
        
        processor = HistoricalSalesProcessor()
        
        if df_raw.empty:
            logger.warning("⚠️  No historical data to process")
            return df_raw, {'total_raw': 0, 'total_processed': 0}
        
        # 1. CLEAN DATA
        df = processor._clean_dataframe(df_raw)
        
        # 2. DEDUPLICATE
        logger.info("🔍 Deduplicating historical records...")
        
        # Identify key columns for deduplication
        key_columns = []
        
        if 'telefono_servicio' in df.columns or 'telefono_limpio' in df.columns:
            key_columns.append('telefono_limpio' if 'telefono_limpio' in df.columns else 'telefono_servicio')
        
        if 'fecha_venta' in df.columns:
            key_columns.append('fecha_venta')
        
        if key_columns:
            df_dedup = df.drop_duplicates(subset=key_columns, keep='first')
            duplicates_removed = len(df) - len(df_dedup)
            logger.info(f"  🗑️  Removed {duplicates_removed} duplicate records")
        else:
            df_dedup = df
            duplicates_removed = 0
        
        # 3. VALIDATE DATES
        if 'fecha_venta' in df_dedup.columns:
            df_dedup['fecha_venta'] = pd.to_datetime(df_dedup['fecha_venta'], errors='coerce')
            
            # Remove invalid dates
            valid_dates = df_dedup['fecha_venta'].notna()
            df_dedup = df_dedup[valid_dates].copy()
        
        # 4. CALCULATE METRICS
        processing_time = (datetime.now() - start_time).total_seconds()
        
        metrics = {
            'total_raw': len(df_raw),
            'total_processed': len(df_dedup),
            'duplicates_removed': duplicates_removed,
            'processing_time_seconds': processing_time,
        }
        
        logger.info(f"✅ Historical processing completed in {processing_time:.2f}s")
        
        return df_dedup, metrics


def consolidate_monthly_report(
    df_ventas_mes: pd.DataFrame,
    df_digital_mes: pd.DataFrame,
    df_historical: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Consolidate monthly report from all sources.
    
    Priority order:
    1. Historical data (already validated and sent)
    2. Current month ventas
    3. Current month digital
    
    Args:
        df_ventas_mes: Monthly sales from tipificador
        df_digital_mes: Monthly digital sales
        df_historical: Historical sales data
    
    Returns:
        Tuple of (consolidated_df, metrics)
    """
    logger.info("📊 Consolidating monthly report...")
    start_time = datetime.now()
    
    # Identify common columns
    common_cols = set(df_ventas_mes.columns) & set(df_digital_mes.columns)
    
    if df_historical is not None and not df_historical.empty:
        common_cols = common_cols & set(df_historical.columns)
    
    common_cols = list(common_cols)
    
    # Select only common columns
    df_list = []
    
    # 1. Add historical (highest priority)
    if df_historical is not None and not df_historical.empty:
        df_hist_subset = df_historical[common_cols].copy()
        df_hist_subset['source'] = 'HISTORICAL'
        df_list.append(df_hist_subset)
        logger.info(f"  📂 Historical: {len(df_hist_subset)} records")
    
    # 2. Add current month ventas
    if not df_ventas_mes.empty:
        df_ventas_subset = df_ventas_mes[common_cols].copy()
        df_ventas_subset['source'] = 'TIPIFICADOR'
        df_list.append(df_ventas_subset)
        logger.info(f"  📋 Tipificador: {len(df_ventas_subset)} records")
    
    # 3. Add digital
    if not df_digital_mes.empty:
        df_digital_subset = df_digital_mes[common_cols].copy()
        df_digital_subset['source'] = 'DIGITAL'
        df_list.append(df_digital_subset)
        logger.info(f"  💻 Digital: {len(df_digital_subset)} records")
    
    # Concatenate all
    if df_list:
        df_consolidated = pd.concat(df_list, ignore_index=True)
        
        # Deduplicate (historical takes precedence)
        if 'telefono_limpio' in df_consolidated.columns and 'fecha_venta' in df_consolidated.columns:
            df_consolidated = df_consolidated.drop_duplicates(
                subset=['telefono_limpio', 'fecha_venta'],
                keep='first'  # Keep first (historical)
            )
    else:
        df_consolidated = pd.DataFrame()
    
    # Calculate metrics
    processing_time = (datetime.now() - start_time).total_seconds()
    
    metrics = {
        'total_historical': len(df_historical) if df_historical is not None else 0,
        'total_ventas': len(df_ventas_mes),
        'total_digital': len(df_digital_mes),
        'total_consolidated': len(df_consolidated),
        'processing_time_seconds': processing_time,
    }
    
    logger.info(f"✅ Monthly consolidation completed: {len(df_consolidated)} unique records")
    logger.info(f"   Processing time: {processing_time:.2f}s")
    
    return df_consolidated, metrics


# Export for backward compatibility
__all__ = [
    "BaseProcessor",
    "TipificadorProcessor",
    "DigitalProcessor",
    "HistoricalSalesProcessor",
    "consolidate_monthly_report",
    "ProcessingResult",
]
