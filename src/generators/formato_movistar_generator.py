"""
Formato Movistar Generator.

Generates the main FORMATO MOVISTAR file with sales data
formatted according to Movistar specifications.

Output Format:
 - FECHA_ALTA: Sale date (DD/MM/YYYY)
 - HORA_VENTA: Sale time (12h format with AM/PM)
 - NUM_CELULAR: Phone number (10 digits)
 - COD_SERVICIO: Service code (2119, 2120, etc.)
 - PROGRAMA: Program name (TU MASCOTA, TU VEHICULO, etc.)
 - ... additional fields

Example:
 >>> generator = FormatoMovistarGenerator()
 >>> success = generator.generate(df_ventas, Path('formato.xlsx'))
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import logging
from datetime import datetime

from src.generators.base_generator import BaseGenerator, GeneratorRegistry

logger = logging.getLogger(__name__)

@GeneratorRegistry.register
class FormatoMovistarGenerator(BaseGenerator):
 """
 Generator for FORMATO MOVISTAR files.
 
 Creates the main sales report file with all required fields
 formatted according to Movistar's specifications.
 """
 
 @property
 def file_type(self) -> str:
 return 'formato_movistar'
 
 @property
 def required_columns(self) -> List[str]:
 return [
 'telefono_limpio',
 'nombre_cliente',
 'tipo_venta',
 'marca_temporal'
 ]
 
 def generate(self, df: pd.DataFrame, output_path: Path) -> bool:
 """
 Generate FORMATO MOVISTAR file.
 
 Args:
 df: DataFrame with sales data
 output_path: Path for output Excel file
 
 Returns:
 True if successful, False otherwise
 """
 self._reset_counters()
 start_time = datetime.now()
 
 self.logger.info("=" * 80)
 self.logger.info(f"[PROCESO] GENERATING FORMATO MOVISTAR")
 self.logger.info("=" * 80)
 
 # Validate input
 if not self.validate_input(df):
 return False
 
 try:
 # Build records
 formato_data = self._build_formato_records(df)
 
 # Create DataFrame
 df_formato = pd.DataFrame(formato_data)
 
 self.logger.info(f"[OK] Built {len(df_formato):,} records")
 
 # Save file
 self._save_excel(df_formato, output_path)
 
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
 self.logger.error(f"Error generating FORMATO MOVISTAR: {e}", exc_info=True)
 self.log_summary(output_path, False)
 return False
 
 def _build_formato_records(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
 """
 Build records for FORMATO MOVISTAR.
 
 Args:
 df: Input DataFrame
 
 Returns:
 List of record dictionaries
 """
 records = []
 
 for _, row in df.iterrows():
 try:
 # Extract date and time
 fecha_alta, hora_venta = self._extract_datetime(row)
 
 # Get service code and program
 cod_servicio, programa = self._get_service_code(row)
 
 # Build observacion and razon
 campo_observacion = self._build_observacion(row, fecha_alta, hora_venta)
 campo_razon = self._build_razon(cod_servicio)
 
 # Create record
 record = {
 'FECHA_ALTA': fecha_alta,
 'HORA_VENTA': hora_venta,
 'NUM_CELULAR': row.get('telefono_limpio', ''),
 'PlanDesc': row.get('plan_desc', ''),
 'COD_PLAN': row.get('cod_plan', ''),
 'NOMBRE_TITULAR': row.get('nombre_cliente', ''),
 'ASESOR_VENTA': row.get('nombre_asesor', ''),
 'CC_AFILIADO': row.get('documento_cliente', ''),
 'Tipo de Envio': '',
 'Dato de envio': '',
 'COD_SERVICIO': cod_servicio,
 'PROGRAMA': programa,
 'INACTIVAR O DESACTIVAR': 'Activar',
 'Campo Observacion': campo_observacion,
 'Campo Razon': campo_razon,
 'RTA': '',
 'Contact_Log': ''
 }
 
 records.append(record)
 self.records_processed += 1
 
 except Exception as e:
 self.logger.warning(f"Error processing record: {e}")
 self.records_skipped += 1
 continue
 
 return records
 
 def _extract_datetime(self, row: pd.Series) -> tuple[str, str]:
 """
 Extract formatted date and time from row.
 
 Args:
 row: Data row
 
 Returns:
 Tuple of (fecha_alta, hora_venta)
 """
 marca_temporal = row.get('marca_temporal', '')
 
 if pd.isna(marca_temporal):
 return ('', '')
 
 try:
 if isinstance(marca_temporal, str):
 dt = pd.to_datetime(marca_temporal)
 else:
 dt = marca_temporal
 
 fecha_alta = dt.strftime('%d/%m/%Y')
 hora_venta = dt.strftime('%I:%M:%S %p')
 
 return (fecha_alta, hora_venta)
 
 except Exception:
 fecha_alta = str(row.get('fecha_venta', ''))
 return (fecha_alta, '')
 
 def _get_service_code(self, row: pd.Series) -> tuple[str, str]:
 """
 Determine service code and program from sale type.
 
 Args:
 row: Data row
 
 Returns:
 Tuple of (cod_servicio, programa)
 """
 tipo_venta = str(row.get('tipo_venta', '')).upper()
 
 # Service code mapping
 if 'MASCOTA' in tipo_venta:
 return ('2119', 'TU MASCOTA')
 elif 'VEHICULO' in tipo_venta or 'VEHÍCULO' in tipo_venta:
 return ('2120', 'TU VEHICULO')
 elif 'HOGAR' in tipo_venta:
 return ('2121', 'TU HOGAR')
 elif 'BIENESTAR' in tipo_venta:
 return ('2119', 'TU BIENESTAR')
 elif 'VIAL' in tipo_venta:
 return ('2119', 'VIAL')
 else:
 # Default to TU MASCOTA
 return ('2119', 'TU MASCOTA')
 
 def _build_observacion(
 self,
 row: pd.Series,
 fecha: str,
 hora: str
 ) -> str:
 """
 Build Campo Observacion field.
 
 Args:
 row: Data row
 fecha: Formatted date
 hora: Formatted time
 
 Returns:
 Formatted observacion string
 """
 asesor = row.get('nombre_asesor', 'N/A')
 
 return (
 f"Asesor de venta {asesor}. "
 f"Fecha de venta {fecha} "
 f"Hora de venta {hora} "
 f"Cliente acepta SI."
 )
 
 def _build_razon(self, cod_servicio: str) -> str:
 """
 Build Campo Razon field.
 
 Args:
 cod_servicio: Service code
 
 Returns:
 Formatted razon string
 """
 return (
 f"Activaciones Serv Suplementarios,Asistencias {cod_servicio}, "
 f"ASISTENCIAS: Venta telefonica hecha por el proveedor Connect Assistance"
 )
 
 def _apply_excel_formatting(
 self,
 writer: pd.ExcelWriter,
 sheet_name: str,
 df: pd.DataFrame
 ) -> None:
 """
 Apply Movistar-specific Excel formatting.
 
 Args:
 writer: ExcelWriter object
 sheet_name: Sheet name
 df: DataFrame
 """
 workbook = writer.book
 worksheet = writer.sheets[sheet_name]
 
 # Header format (blue background)
 header_format = workbook.add_format({
 'bold': True,
 'bg_color': '#4472C4',
 'font_color': 'white',
 'border': 1,
 'align': 'center',
 'valign': 'vcenter'
 })
 
 # Apply to headers
 for col_num, value in enumerate(df.columns):
 worksheet.write(0, col_num, value, header_format)
 
 # Auto-size columns
 max_len = max(
 df[value].astype(str).apply(len).max(),
 len(str(value))
 )
 worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
 
 def validate_output(self, file_path: Path) -> bool:
 """
 Validate generated FORMATO MOVISTAR file.
 
 Args:
 file_path: Path to generated file
 
 Returns:
 True if valid, False otherwise
 """
 if not file_path.exists():
 self.logger.error(f"Output file does not exist: {file_path}")
 return False
 
 try:
 df = pd.read_excel(file_path)
 
 # Check required columns
 required_cols = [
 'FECHA_ALTA', 'HORA_VENTA', 'NUM_CELULAR',
 'COD_SERVICIO', 'PROGRAMA', 'Campo Observacion', 'Campo Razon'
 ]
 
 missing_cols = set(required_cols) - set(df.columns)
 if missing_cols:
 self.logger.error(f"Missing required columns: {missing_cols}")
 return False
 
 # Check not empty
 if df.empty:
 self.logger.warning("Generated file is empty")
 return True # Empty is technically valid
 
 # Check phone numbers format
 phones = df['NUM_CELULAR'].astype(str)
 invalid_phones = phones[~phones.str.match(r'^\d{10}$')]
 
 if len(invalid_phones) > 0:
 self.logger.warning(
 f"{len(invalid_phones)} invalid phone numbers found"
 )
 
 self.logger.debug("Output validation passed")
 return True
 
 except Exception as e:
 self.logger.error(f"Error validating output: {e}")
 return False

# Export
__all__ = ['FormatoMovistarGenerator']
