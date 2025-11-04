"""
SVAS Generator for Movistar.

Generates SVAS (Servicios de Valor Agregado Suplementarios) files
for different segments: Digital, Fija, Movil.

Output Format:
    - Num_Celular: Phone number
    - cod_plantarif: Tariff plan code
    - Codigo_Bono: Bonus code
    - Cod_ciclo: Cycle code
    - EMPLEADO: Employee indicator (Yes/No)

Example:
    >>> generator = SVASGenerator()
    >>> success = generator.generate(df_digital, Path('svas_digital.xlsx'), segment='DIG')
"""

from pathlib import Path
from typing import Dict, Any, List, Literal
import pandas as pd
import logging
from datetime import datetime

from src.generators.base_generator import BaseGenerator, GeneratorRegistry

logger = logging.getLogger(__name__)


@GeneratorRegistry.register
class SVASGenerator(BaseGenerator):
    """
    Generator for SVAS files (Digital, Fija, Movil).
    
    Creates SVAS format files for each segment with
    appropriate service codes and configurations.
    """
    
    # Segment-specific configurations
    SEGMENT_CONFIGS = {
        'DIG': {
            'name': 'Digital',
            'header_color': '#FFC000',  # Orange
            'default_code': '4045'
        },
        'FIJA': {
            'name': 'Fija',
            'header_color': '#4472C4',  # Blue
            'default_code': '4046'
        },
        'MOV': {
            'name': 'Móvil',
            'header_color': '#70AD47',  # Green
            'default_code': '4045'
        }
    }
    
    @property
    def file_type(self) -> str:
        return 'svas'
    
    @property
    def required_columns(self) -> List[str]:
        return ['telefono_limpio']
    
    def generate(
        self,
        df: pd.DataFrame,
        output_path: Path,
        segment: Literal['DIG', 'FIJA', 'MOV'] = 'DIG'
    ) -> bool:
        """
        Generate SVAS file for specified segment.
        
        Args:
            df: DataFrame with sales data
            output_path: Path for output Excel file
            segment: Segment type ('DIG', 'FIJA', 'MOV')
            
        Returns:
            True if successful, False otherwise
        """
        self._reset_counters()
        start_time = datetime.now()
        
        segment_name = self.SEGMENT_CONFIGS[segment]['name']
        
        self.logger.info("=" * 80)
        self.logger.info(f"📝 GENERATING SVAS {segment_name.upper()}")
        self.logger.info("=" * 80)
        
        # Validate input
        if not self.validate_input(df):
            return False
        
        try:
            # Filter by segment if not Digital
            if segment != 'DIG':
                df = df[df['tipo_linea'] == segment].copy()
                self.logger.info(f"Filtered to {len(df):,} {segment_name} records")
            
            if df.empty:
                self.logger.warning(f"No data for SVAS {segment_name}")
                return False
            
            # Build records
            svas_data = self._build_svas_records(df, segment)
            
            # Create DataFrame
            df_svas = pd.DataFrame(svas_data)
            
            self.logger.info(f"📊 Built {len(df_svas):,} records")
            
            # Save file with segment-specific formatting
            self._save_excel_with_segment_format(df_svas, output_path, segment)
            
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
            self.logger.error(f"Error generating SVAS {segment_name}: {e}", exc_info=True)
            self.log_summary(output_path, False)
            return False
    
    def _build_svas_records(
        self,
        df: pd.DataFrame,
        segment: str
    ) -> List[Dict[str, Any]]:
        """
        Build records for SVAS file.
        
        Args:
            df: Input DataFrame
            segment: Segment type
            
        Returns:
            List of record dictionaries
        """
        records = []
        default_code = self.SEGMENT_CONFIGS[segment]['default_code']
        
        for _, row in df.iterrows():
            try:
                record = {
                    'Num_Celular': row.get('telefono_limpio', ''),
                    'cod_plantarif': row.get('cod_plan', '6322'),  # Default from spec
                    'Codigo_Bono': row.get('cod_bono', default_code),
                    'Cod_ciclo': row.get('cod_ciclo', '20'),  # Default from spec
                    'EMPLEADO': row.get('es_empleado_movistar', 'No')
                }
                
                records.append(record)
                self.records_processed += 1
                
            except Exception as e:
                self.logger.warning(f"Error processing record: {e}")
                self.records_skipped += 1
                continue
        
        return records
    
    def _save_excel_with_segment_format(
        self,
        df: pd.DataFrame,
        output_path: Path,
        segment: str
    ) -> None:
        """
        Save Excel with segment-specific formatting.
        
        Args:
            df: DataFrame to save
            output_path: Output path
            segment: Segment type
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Get segment-specific color
            header_color = self.SEGMENT_CONFIGS[segment]['header_color']
            
            # Header format
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': header_color,
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            # Apply formatting
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)  # Fixed width
    
    def validate_output(self, file_path: Path) -> bool:
        """
        Validate generated SVAS file.
        
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
                'Num_Celular', 'cod_plantarif', 'Codigo_Bono',
                'Cod_ciclo', 'EMPLEADO'
            ]
            
            missing_cols = set(required_cols) - set(df.columns)
            if missing_cols:
                self.logger.error(f"Missing required columns: {missing_cols}")
                return False
            
            # Check not empty
            if df.empty:
                self.logger.warning("Generated file is empty")
                return True
            
            self.logger.debug("Output validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating output: {e}")
            return False


# Export
__all__ = ['SVASGenerator']
