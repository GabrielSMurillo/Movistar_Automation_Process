"""
Validation Pipeline Stage.

Performs comprehensive validation of sales records:
1. Phone number validation (with 957 prefix handling)
2. Asesor name validation
3. Login validation
4. Cliente name validation
5. Required fields validation

Splits records into:
- Valid records → continue to processing
- Invalid records → novedades file

Example:
    >>> from src.pipeline import Pipeline
    >>> from src.pipeline.validation_stage import ValidationStage
    >>> 
    >>> pipeline = Pipeline([
    ...     IngestionStage(),
    ...     ValidationStage(),  # Validates and splits records
    ...     TransformationStage()
    ... ])
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import logging
from datetime import datetime

from src.pipeline.base import PipelineStage, PipelineContext
from src.services.phone_validator import EnhancedPhoneValidator
from src.services.field_validators import FieldValidators

logger = logging.getLogger(__name__)


class ValidationStage(PipelineStage):
    """
    Comprehensive validation stage.
    
    Validates all business rules and splits records into:
    - Valid: Continue processing
    - Invalid: Go to novedades file
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize validation stage.
        
        Args:
            config: Stage configuration
        """
        super().__init__(name='Validation', config=config)
        
        self.phone_validator = EnhancedPhoneValidator()
        self.field_validators = FieldValidators()
        
        # Statistics
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.rejection_stats: Dict[str, int] = {}
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute validation.
        
        Args:
            context: Pipeline context with data
        
        Returns:
            Updated context with valid/invalid DataFrames
        """
        self.logger.info("=" * 80)
        self.logger.info("🔍 VALIDACIÓN COMPLETA DE REGISTROS")
        self.logger.info("=" * 80)
        
        # Get data to validate
        df_tipificador = context.get_dataframe('tipificador_raw')
        
        if df_tipificador is None or df_tipificador.empty:
            self.logger.warning("No tipificador data to validate")
            return context
        
        self.total_records = len(df_tipificador)
        self.logger.info(f"Total registros a validar: {self.total_records:,}")
        
        # Validate all records
        df_valid, df_invalid = self._validate_dataframe(df_tipificador)
        
        # Store results
        context.add_dataframe('tipificador_valid', df_valid)
        context.add_dataframe('tipificador_novedades', df_invalid)
        
        # Update counters
        self.valid_records = len(df_valid)
        self.invalid_records = len(df_invalid)
        self.records_processed = self.total_records
        
        # Add metrics
        context.set_metric('validation_total', self.total_records)
        context.set_metric('validation_valid', self.valid_records)
        context.set_metric('validation_invalid', self.invalid_records)
        context.set_metric('validation_rejection_stats', self.rejection_stats)
        
        # Log summary
        self._log_summary()
        
        return context
    
    def _validate_dataframe(
        self,
        df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Validate entire DataFrame.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Tuple of (valid_df, invalid_df)
        """
        # Create copy with validation columns
        df_validated = df.copy()
        
        # Initialize validation columns
        df_validated['es_valido'] = True
        df_validated['motivo_rechazo'] = ''
        df_validated['validacion_telefono'] = True
        df_validated['validacion_asesor'] = True
        df_validated['validacion_login'] = True
        df_validated['validacion_cliente'] = True
        
        # Validate each record
        for idx, row in df_validated.iterrows():
            is_valid, rejection_reasons = self._validate_record(row, df_validated, idx)
            
            if not is_valid:
                df_validated.at[idx, 'es_valido'] = False
                df_validated.at[idx, 'motivo_rechazo'] = '; '.join(rejection_reasons)
        
        # Split into valid/invalid
        df_valid = df_validated[df_validated['es_valido']].copy()
        df_invalid = df_validated[~df_validated['es_valido']].copy()
        
        # Add processing timestamp to invalid records
        df_invalid['fecha_procesamiento'] = datetime.now()
        df_invalid['estado'] = 'RECHAZADO'
        
        return df_valid, df_invalid
    
    def _validate_record(
        self,
        row: pd.Series,
        df: pd.DataFrame,
        idx: Any
    ) -> tuple[bool, List[str]]:
        """
        Validate a single record.
        
        Args:
            row: Record to validate
            df: Full DataFrame (for updating)
            idx: Record index
        
        Returns:
            Tuple of (is_valid, rejection_reasons)
        """
        rejection_reasons = []
        
        # 1. Validate phone number
        if 'telefono_servicio' in row:
            result = self.phone_validator.validate(row['telefono_servicio'])
            
            if not result.is_valid:
                df.at[idx, 'validacion_telefono'] = False
                rejection_reasons.append(f"Teléfono: {result.reason}")
                self._increment_rejection_stat(f"Teléfono - {result.reason}")
            else:
                # Store validated data
                df.at[idx, 'telefono_limpio'] = result.cleaned_phone
                df.at[idx, 'tipo_linea'] = result.tipo_linea
                df.at[idx, 'tiene_indicativo'] = result.has_city_code
                if result.city_name:
                    df.at[idx, 'ciudad'] = result.city_name
        else:
            df.at[idx, 'validacion_telefono'] = False
            rejection_reasons.append("Teléfono: Campo faltante")
            self._increment_rejection_stat("Teléfono - Campo faltante")
        
        # 2. Validate asesor name
        if 'nombre_asesor' in row:
            is_valid, reason = self.field_validators.validate_asesor_name(
                row['nombre_asesor']
            )
            
            if not is_valid:
                df.at[idx, 'validacion_asesor'] = False
                rejection_reasons.append(reason)
                self._increment_rejection_stat(f"Asesor - {reason.split(':')[0]}")
        
        # 3. Validate login
        if 'login_asesor' in row or 'LOGIN' in row:
            login_field = 'login_asesor' if 'login_asesor' in row else 'LOGIN'
            is_valid, reason = self.field_validators.validate_login(
                row[login_field]
            )
            
            if not is_valid:
                df.at[idx, 'validacion_login'] = False
                rejection_reasons.append(reason)
                self._increment_rejection_stat(f"Login - {reason.split(':')[0]}")
        
        # 4. Validate cliente name
        if 'nombre_cliente' in row:
            is_valid, reason = self.field_validators.validate_cliente_name(
                row['nombre_cliente']
            )
            
            if not is_valid:
                df.at[idx, 'validacion_cliente'] = False
                rejection_reasons.append(reason)
                self._increment_rejection_stat(f"Cliente - {reason.split(':')[0]}")
        
        # 5. Validate required fields
        required_fields = ['tipo_venta', 'fecha_venta']
        for field in required_fields:
            if field not in row or pd.isna(row[field]) or str(row[field]).strip() == '':
                rejection_reasons.append(f"Campo requerido faltante: {field}")
                self._increment_rejection_stat(f"Campo faltante - {field}")
        
        is_valid = len(rejection_reasons) == 0
        
        return is_valid, rejection_reasons
    
    def _increment_rejection_stat(self, reason: str) -> None:
        """Increment rejection statistic counter."""
        if reason not in self.rejection_stats:
            self.rejection_stats[reason] = 0
        self.rejection_stats[reason] += 1
    
    def _log_summary(self) -> None:
        """Log validation summary."""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("📊 RESUMEN DE VALIDACIÓN")
        self.logger.info("=" * 80)
        self.logger.info(f"Total procesados: {self.total_records:,}")
        self.logger.info(f"✅ Válidos: {self.valid_records:,} ({self.valid_records/self.total_records*100:.1f}%)")
        self.logger.info(f"❌ Inválidos: {self.invalid_records:,} ({self.invalid_records/self.total_records*100:.1f}%)")
        
        if self.rejection_stats:
            self.logger.info("\nMotivos de rechazo:")
            sorted_reasons = sorted(
                self.rejection_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for reason, count in sorted_reasons[:10]:  # Top 10
                self.logger.info(f"  • {reason}: {count:,}")
        
        self.logger.info("=" * 80)


# Export
__all__ = ['ValidationStage']
