"""
Novedades (Rejected Records) Generator.

Generates file with rejected records for operations team to fix.

File Structure:
- Same as Tipificador de Ventas
- Plus additional columns:
  * MOTIVO_RECHAZO: Why rejected
  * FECHA_PROCESAMIENTO: When processed
  * ESTADO: "RECHAZADO"
  * VALIDACION_TELEFONO: bool
  * VALIDACION_ASESOR: bool
  * VALIDACION_LOGIN: bool
  * VALIDACION_CLIENTE: bool

This file is for INTERNAL use only - NOT sent to client.

Example:
    >>> generator = NovedadesGenerator()
    >>> success = generator.generate(
    ...     df_invalid,
    ...     Path('OCTUBRE_NO_Exitosas_Movistar.xlsx')
    ... )
"""

from pathlib import Path
from typing import List
import pandas as pd
import logging
from datetime import datetime

from src.generators.base_generator import BaseGenerator, GeneratorRegistry

logger = logging.getLogger(__name__)


@GeneratorRegistry.register
class NovedadesGenerator(BaseGenerator):
    """
    Generator for novedades (rejected records) file.
    
    Creates file with same structure as Tipificador plus
    rejection information for operations team.
    """
    
    @property
    def file_type(self) -> str:
        return 'novedades'
    
    @property
    def required_columns(self) -> List[str]:
        return ['motivo_rechazo', 'es_valido']
    
    def generate(self, df: pd.DataFrame, output_path: Path) -> bool:
        """
        Generate novedades file.
        
        Args:
            df: DataFrame with rejected records
            output_path: Output file path
        
        Returns:
            True if successful
        """
        self._reset_counters()
        start_time = datetime.now()
        
        self.logger.info("=" * 80)
        self.logger.info("📝 GENERATING NOVEDADES FILE")
        self.logger.info("=" * 80)
        
        # Check if there are rejected records
        if df.empty:
            self.logger.info("✅ No hay registros rechazados - archivo de novedades no necesario")
            return True
        
        try:
            # Prepare novedades data
            df_novedades = self._prepare_novedades(df)
            
            self.logger.info(f"📊 Novedades: {len(df_novedades):,} registros rechazados")
            
            # Save file
            self._save_novedades_file(df_novedades, output_path)
            
            # Calculate time
            self.generation_time = (datetime.now() - start_time).total_seconds()
            
            # Validate output
            if not self.validate_output(output_path):
                self.logger.error("Output validation failed")
                return False
            
            # Log summary
            self.log_summary(output_path, True)
            
            # Log rejection statistics
            self._log_rejection_stats(df_novedades)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating novedades file: {e}", exc_info=True)
            self.log_summary(output_path, False)
            return False
    
    def _prepare_novedades(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare novedades DataFrame.
        
        Args:
            df: Raw rejected records
        
        Returns:
            Formatted novedades DataFrame
        """
        df_novedades = df.copy()
        
        # Ensure required columns exist
        if 'estado' not in df_novedades.columns:
            df_novedades['ESTADO'] = 'RECHAZADO'
        
        if 'fecha_procesamiento' not in df_novedades.columns:
            df_novedades['FECHA_PROCESAMIENTO'] = datetime.now()
        
        # Ensure validation columns exist
        validation_cols = [
            'validacion_telefono',
            'validacion_asesor',
            'validacion_login',
            'validacion_cliente'
        ]
        
        for col in validation_cols:
            if col not in df_novedades.columns:
                df_novedades[col.upper()] = False
            else:
                # Rename to uppercase for consistency
                df_novedades[col.upper()] = df_novedades[col]
        
        # Ensure MOTIVO_RECHAZO exists
        if 'MOTIVO_RECHAZO' not in df_novedades.columns:
            if 'motivo_rechazo' in df_novedades.columns:
                df_novedades['MOTIVO_RECHAZO'] = df_novedades['motivo_rechazo']
            else:
                df_novedades['MOTIVO_RECHAZO'] = 'Error no especificado'
        
        # Reorder columns: Original columns first, then validation columns
        original_cols = [col for col in df_novedades.columns 
                        if col not in validation_cols + ['MOTIVO_RECHAZO', 'FECHA_PROCESAMIENTO', 'ESTADO']]
        
        final_cols = original_cols + [
            'MOTIVO_RECHAZO',
            'FECHA_PROCESAMIENTO',
            'ESTADO',
            'VALIDACION_TELEFONO',
            'VALIDACION_ASESOR',
            'VALIDACION_LOGIN',
            'VALIDACION_CLIENTE'
        ]
        
        # Select only existing columns
        existing_cols = [col for col in final_cols if col in df_novedades.columns]
        df_novedades = df_novedades[existing_cols]
        
        self.records_processed = len(df_novedades)
        
        return df_novedades
    
    def _save_novedades_file(
        self,
        df: pd.DataFrame,
        output_path: Path
    ) -> None:
        """
        Save novedades file with specific formatting.
        
        Args:
            df: Novedades DataFrame
            output_path: Output path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Novedades', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Novedades']
            
            # Header format (RED - indicates errors)
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FF0000',
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            # Error text format
            error_format = workbook.add_format({
                'bg_color': '#FFE6E6',
                'border': 1
            })
            
            # Apply header formatting
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num, value, header_format)
                
                # Auto-size columns
                max_len = max(
                    df[value].astype(str).apply(len).max(),
                    len(str(value))
                )
                worksheet.set_column(col_num, col_num, min(max_len + 2, 60))
            
            # Highlight MOTIVO_RECHAZO column
            if 'MOTIVO_RECHAZO' in df.columns:
                col_idx = df.columns.get_loc('MOTIVO_RECHAZO')
                for row_num in range(1, len(df) + 1):
                    worksheet.write(
                        row_num,
                        col_idx,
                        df.iloc[row_num - 1]['MOTIVO_RECHAZO'],
                        error_format
                    )
        
        self.logger.debug(f"Novedades file saved: {output_path}")
    
    def _log_rejection_stats(self, df: pd.DataFrame) -> None:
        """Log rejection statistics."""
        self.logger.info("\n" + "-" * 80)
        self.logger.info("📊 ESTADÍSTICAS DE RECHAZO")
        self.logger.info("-" * 80)
        
        # Count by validation type
        if 'VALIDACION_TELEFONO' in df.columns:
            phone_errors = (~df['VALIDACION_TELEFONO']).sum()
            self.logger.info(f"📞 Errores de teléfono: {phone_errors:,}")
        
        if 'VALIDACION_ASESOR' in df.columns:
            asesor_errors = (~df['VALIDACION_ASESOR']).sum()
            self.logger.info(f"👤 Errores de asesor: {asesor_errors:,}")
        
        if 'VALIDACION_LOGIN' in df.columns:
            login_errors = (~df['VALIDACION_LOGIN']).sum()
            self.logger.info(f"🔑 Errores de login: {login_errors:,}")
        
        if 'VALIDACION_CLIENTE' in df.columns:
            cliente_errors = (~df['VALIDACION_CLIENTE']).sum()
            self.logger.info(f"👥 Errores de cliente: {cliente_errors:,}")
        
        # Top rejection reasons
        if 'MOTIVO_RECHAZO' in df.columns:
            self.logger.info("\nPrincipales motivos de rechazo:")
            top_reasons = df['MOTIVO_RECHAZO'].value_counts().head(5)
            for reason, count in top_reasons.items():
                # Truncate long reasons
                reason_str = (reason[:70] + '...') if len(reason) > 70 else reason
                self.logger.info(f"  • {reason_str}: {count:,}")
        
        self.logger.info("-" * 80)
    
    def validate_output(self, file_path: Path) -> bool:
        """
        Validate generated novedades file.
        
        Args:
            file_path: Path to generated file
        
        Returns:
            True if valid
        """
        if not file_path.exists():
            self.logger.error(f"Output file does not exist: {file_path}")
            return False
        
        try:
            df = pd.read_excel(file_path, sheet_name='Novedades')
            
            # Check required columns
            required_cols = ['MOTIVO_RECHAZO', 'ESTADO']
            missing_cols = set(required_cols) - set(df.columns)
            
            if missing_cols:
                self.logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Check that all records have ESTADO = RECHAZADO
            if 'ESTADO' in df.columns:
                if not (df['ESTADO'] == 'RECHAZADO').all():
                    self.logger.warning("Some records don't have ESTADO = RECHAZADO")
            
            self.logger.debug("Output validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating output: {e}")
            return False


# Export
__all__ = ['NovedadesGenerator']
