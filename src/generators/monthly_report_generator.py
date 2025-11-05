"""
Monthly Report Generator for Movistar.

Generates consolidated monthly reports with multiple sheets:
    - CARG DIGITAL: Digital sales
    - CARG FIJA: Fixed line sales
    - CARG MOVIL: Mobile sales

Each sheet contains sales data formatted according to Movistar specifications.

Example:
    >>> generator = MonthlyReportGenerator()
    >>> success = generator.generate_consolidated(
    ...     df_consolidated, df_digital, Path('OCTUBRE_Exitosas.xlsx')
    ... )
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import logging
from datetime import datetime

from src.generators.base_generator import BaseGenerator, GeneratorRegistry

# ✅ Import ServiceCodeMapper for CORRECT codes
try:
    from src.services.service_code_mapper import ServiceCodeMapper
    SERVICE_MAPPER_AVAILABLE = True
except ImportError:
    SERVICE_MAPPER_AVAILABLE = False

logger = logging.getLogger(__name__)


@GeneratorRegistry.register
class MonthlyReportGenerator(BaseGenerator):
    """
    Generator for monthly consolidated reports.
    
    Creates multi-sheet Excel files with sales data
    organized by segment (Digital, Fija, Movil).
    """
    
    SHEET_NAMES = {
        'digital': 'CARG DIGITAL',
        'fija': 'CARG FIJA',
        'movil': 'CARG MOVIL'
    }
    
    @property
    def file_type(self) -> str:
        return 'monthly_report'
    
    @property
    def required_columns(self) -> List[str]:
        return ['telefono_limpio', 'tipo_linea']
    
    def generate(self, df: pd.DataFrame, output_path: Path) -> bool:
        """
        Generate monthly report (single DataFrame).
        
        For multi-DataFrame consolidated reports, use generate_consolidated().
        
        Args:
            df: DataFrame with sales data
            output_path: Path for output Excel file
            
        Returns:
            True if successful, False otherwise
        """
        # For single DataFrame, split by tipo_linea
        df_digital = df[df.get('tipo_venta', '') == 'DIGITAL'].copy()
        df_fija = df[df.get('tipo_linea', '') == 'FIJA'].copy()
        df_movil = df[df.get('tipo_linea', '') == 'MOVIL'].copy()
        
        return self.generate_consolidated(
            df_consolidated=pd.concat([df_fija, df_movil], ignore_index=True),
            df_digital=df_digital,
            output_path=output_path
        )
    
    def generate_consolidated(
        self,
        df_consolidated: pd.DataFrame,
        df_digital: pd.DataFrame,
        output_path: Path
    ) -> bool:
        """
        Generate monthly consolidated report from multiple DataFrames.
        
        Args:
            df_consolidated: Consolidated sales (Fija + Movil)
            df_digital: Digital sales
            output_path: Path for output Excel file
            
        Returns:
            True if successful, False otherwise
        """
        self._reset_counters()
        start_time = datetime.now()
        
        self.logger.info("=" * 80)
        self.logger.info("📝 GENERATING MONTHLY CONSOLIDATED REPORT")
        self.logger.info("=" * 80)
        
        try:
            # Build sheets
            sheets = {}
            
            # CARG DIGITAL
            if not df_digital.empty:
                self.logger.info(f"Building CARG DIGITAL sheet ({len(df_digital):,} records)")
                sheets[self.SHEET_NAMES['digital']] = self._build_sheet_data(
                    df_digital,
                    'Digital'
                )
            
            # CARG FIJA
            df_fija = df_consolidated[df_consolidated['tipo_linea'] == 'FIJA'].copy()
            if not df_fija.empty:
                self.logger.info(f"Building CARG FIJA sheet ({len(df_fija):,} records)")
                sheets[self.SHEET_NAMES['fija']] = self._build_sheet_data(
                    df_fija,
                    'Fija'
                )
            
            # CARG MOVIL
            df_movil = df_consolidated[df_consolidated['tipo_linea'] == 'MOVIL'].copy()
            if not df_movil.empty:
                self.logger.info(f"Building CARG MOVIL sheet ({len(df_movil):,} records)")
                sheets[self.SHEET_NAMES['movil']] = self._build_sheet_data(
                    df_movil,
                    'Móvil'
                )
            
            if not sheets:
                self.logger.warning("No data to generate monthly report")
                return False
            
            # Save multi-sheet Excel
            self._save_multi_sheet_excel(sheets, output_path)
            
            # Calculate time
            self.generation_time = (datetime.now() - start_time).total_seconds()
            
            # Validate output
            if not self.validate_output(output_path):
                self.logger.error("Output validation failed")
                return False
            
            # Log summary
            self.log_summary(output_path, True)
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating monthly report: {e}", exc_info=True)
            self.log_summary(output_path, False)
            return False
    
    def _build_sheet_data(
        self,
        df: pd.DataFrame,
        segment: str
    ) -> pd.DataFrame:
        """
        Build data for a single sheet.
        
        Args:
            df: Input DataFrame
            segment: Segment name (Digital, Fija, Móvil)
            
        Returns:
            DataFrame with formatted data
        """
        records = []
        
        for _, row in df.iterrows():
            try:
                # ✅ Determine COD_SERVICIO using ServiceCodeMapper
                if SERVICE_MAPPER_AVAILABLE:
                    mapper = ServiceCodeMapper()
                    tipo_venta = str(row.get('tipo_venta', '') or row.get('programa', 'TU MASCOTA'))
                    
                    # Determine tipo_linea based on segment
                    if segment == 'Digital':
                        tipo_linea = 'DIGITAL'
                        asesor = 'Digital'
                    elif segment == 'Fija':
                        tipo_linea = 'FIJA'
                        asesor = row.get('nombre_asesor', segment)
                    else:
                        tipo_linea = 'MOVIL'
                        asesor = row.get('nombre_asesor', segment)
                    
                    cod_servicio, programa = mapper.get_code(tipo_venta, tipo_linea)
                else:
                    # ❌ FALLBACK: Old hardcoded method
                    if segment == 'Digital':
                        cod_servicio = '4045'  # Default DIGITAL VIAL
                        asesor = 'Digital'
                        programa = 'Vial'
                    else:
                        cod_servicio = '3823'  # Default MOVIL TU MASCOTA (✅ CORRECTED)
                        asesor = row.get('nombre_asesor', segment)
                        programa = 'TU MASCOTA'
                
                record = {
                    'Source.Name': row.get('_archivo_origen', ''),
                    'FECHA_ALTA': row.get('fecha_venta', ''),
                    'HORA_VENTA': row.get('hora_venta', ''),
                    'NUM. CELULAR': row.get('telefono_limpio', ''),
                    'ASESOR_VENTA': asesor,
                    'COD. SERVICIO': cod_servicio,
                    'PROGRAMA': row.get('programa', 'Vial'),
                    'RTA': row.get('respuesta', 'Exito'),
                    'Contact_Log': ''
                }
                
                records.append(record)
                self.records_processed += 1
                
            except Exception as e:
                self.logger.warning(f"Error processing record: {e}")
                self.records_skipped += 1
                continue
        
        return pd.DataFrame(records)
    
    def _save_multi_sheet_excel(
        self,
        sheets: Dict[str, pd.DataFrame],
        output_path: Path
    ) -> None:
        """
        Save multi-sheet Excel file with formatting.
        
        Args:
            sheets: Dictionary mapping sheet name to DataFrame
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            for sheet_name, df in sheets.items():
                # Write data
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                
                # Header format (green as per spec)
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#70AD47',
                    'font_color': 'black',
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter'
                })
                
                # Apply formatting
                for col_num, value in enumerate(df.columns):
                    worksheet.write(0, col_num, value, header_format)
                    
                    # Auto-size columns
                    max_len = max(
                        df[value].astype(str).apply(len).max(),
                        len(str(value))
                    )
                    worksheet.set_column(col_num, col_num, min(max_len + 2, 30))
                
                self.logger.debug(f"  📄 Sheet '{sheet_name}': {len(df):,} records")
    
    def validate_output(self, file_path: Path) -> bool:
        """
        Validate generated monthly report.
        
        Args:
            file_path: Path to generated file
            
        Returns:
            True if valid, False otherwise
        """
        if not file_path.exists():
            self.logger.error(f"Output file does not exist: {file_path}")
            return False
        
        try:
            # Load all sheets
            xl_file = pd.ExcelFile(file_path)
            
            # Check that we have at least one expected sheet
            expected_sheets = set(self.SHEET_NAMES.values())
            found_sheets = set(xl_file.sheet_names)
            
            if not found_sheets.intersection(expected_sheets):
                self.logger.error(
                    f"No expected sheets found. Expected: {expected_sheets}, Found: {found_sheets}"
                )
                return False
            
            # Validate each sheet
            for sheet_name in found_sheets:
                df = pd.read_excel(xl_file, sheet_name=sheet_name)
                
                # Check required columns
                required_cols = [
                    'FECHA_ALTA', 'NUM. CELULAR', 'ASESOR_VENTA',
                    'COD. SERVICIO', 'PROGRAMA'
                ]
                
                missing_cols = set(required_cols) - set(df.columns)
                if missing_cols:
                    self.logger.error(
                        f"Sheet '{sheet_name}' missing columns: {missing_cols}"
                    )
                    return False
            
            self.logger.debug("Output validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating output: {e}")
            return False


# Export
__all__ = ['MonthlyReportGenerator']
