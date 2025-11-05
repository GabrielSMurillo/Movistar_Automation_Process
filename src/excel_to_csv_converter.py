"""
Módulo para convertir archivos Excel (.xlsx) a CSV
y analizar su estructura para documentación.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExcelToCSVConverter:
    """Convierte archivos Excel a CSV y analiza su estructura."""
    
    def __init__(self, base_path: str):
        """
        Inicializa el conversor.
        
        Args:
            base_path: Ruta base donde buscar archivos Excel
        """
        self.base_path = Path(base_path)
        self.conversion_report = []
        self.analysis_report = {}
        
    def find_all_excel_files(self) -> List[Path]:
        """
        Encuentra todos los archivos .xlsx en el directorio base.
        
        Returns:
            Lista de rutas a archivos Excel
        """
        excel_files = []
        
        # Buscar recursivamente todos los archivos .xlsx
        for excel_file in self.base_path.rglob("*.xlsx"):
            # Excluir archivos temporales de Excel
            if not excel_file.name.startswith('~$'):
                excel_files.append(excel_file)
                
        logger.info(f"Encontrados {len(excel_files)} archivos Excel")
        return excel_files
    
    def analyze_excel_structure(self, excel_path: Path) -> Dict:
        """
        Analiza la estructura de un archivo Excel.
        
        Args:
            excel_path: Ruta al archivo Excel
            
        Returns:
            Diccionario con información del archivo
        """
        try:
            # Leer información del archivo Excel
            xl_file = pd.ExcelFile(excel_path)
            
            analysis = {
                'file_name': excel_path.name,
                'file_path': str(excel_path),
                'sheets': [],
                'total_sheets': len(xl_file.sheet_names),
                'file_size_mb': excel_path.stat().st_size / (1024 * 1024)
            }
            
            # Analizar cada hoja
            for sheet_name in xl_file.sheet_names:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                
                sheet_info = {
                    'name': sheet_name,
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'null_counts': df.isnull().sum().to_dict(),
                    'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
                }
                
                analysis['sheets'].append(sheet_info)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando {excel_path.name}: {str(e)}")
            return {
                'file_name': excel_path.name,
                'file_path': str(excel_path),
                'error': str(e)
            }
    
    def convert_excel_to_csv(self, excel_path: Path, output_dir: Path = None) -> List[Tuple[str, bool]]:
        """
        Convierte un archivo Excel a CSV.
        Si tiene múltiples hojas, crea un CSV por hoja.
        
        Args:
            excel_path: Ruta al archivo Excel
            output_dir: Directorio de salida (opcional, por defecto mismo directorio)
            
        Returns:
            Lista de tuplas (ruta_csv, exito)
        """
        results = []
        
        try:
            # Definir directorio de salida
            if output_dir is None:
                output_dir = excel_path.parent / "csv_converted"
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Leer archivo Excel
            xl_file = pd.ExcelFile(excel_path)
            base_name = excel_path.stem
            
            # Si solo tiene una hoja, usar el nombre del archivo
            if len(xl_file.sheet_names) == 1:
                df = pd.read_excel(excel_path, sheet_name=0)
                csv_path = output_dir / f"{base_name}.csv"
                
                # Guardar a CSV
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                results.append((str(csv_path), True))
                logger.info(f"✓ Convertido: {excel_path.name} -> {csv_path.name}")
                
            # Si tiene múltiples hojas, crear un CSV por hoja
            else:
                for sheet_name in xl_file.sheet_names:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    
                    # Limpiar nombre de hoja para nombre de archivo
                    safe_sheet_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    csv_path = output_dir / f"{base_name}_{safe_sheet_name}.csv"
                    
                    # Guardar a CSV
                    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    results.append((str(csv_path), True))
                    logger.info(f"✓ Convertido: {excel_path.name} [{sheet_name}] -> {csv_path.name}")
            
            self.conversion_report.append({
                'original': str(excel_path),
                'converted': [r[0] for r in results],
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"✗ Error convirtiendo {excel_path.name}: {str(e)}")
            results.append((str(excel_path), False))
            self.conversion_report.append({
                'original': str(excel_path),
                'converted': [],
                'status': 'error',
                'error': str(e)
            })
        
        return results
    
    def convert_all(self, analyze: bool = True, convert: bool = True) -> Dict:
        """
        Encuentra, analiza y convierte todos los archivos Excel.
        
        Args:
            analyze: Si True, analiza la estructura de los archivos
            convert: Si True, convierte los archivos a CSV
            
        Returns:
            Diccionario con resultados del proceso
        """
        excel_files = self.find_all_excel_files()
        
        results = {
            'total_files': len(excel_files),
            'analyzed': 0,
            'converted': 0,
            'errors': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        for excel_file in excel_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"Procesando: {excel_file.name}")
            logger.info(f"{'='*60}")
            
            # Analizar estructura
            if analyze:
                analysis = self.analyze_excel_structure(excel_file)
                self.analysis_report[excel_file.name] = analysis
                results['analyzed'] += 1
                
                # Mostrar resumen del análisis
                if 'error' not in analysis:
                    logger.info(f"  📊 Hojas: {analysis['total_sheets']}")
                    logger.info(f"  💾 Tamaño: {analysis['file_size_mb']:.2f} MB")
                    for sheet in analysis['sheets']:
                        logger.info(f"    - Hoja '{sheet['name']}': {sheet['rows']} filas × {sheet['columns']} columnas")
            
            # Convertir a CSV
            if convert:
                conversion_results = self.convert_excel_to_csv(excel_file)
                if any(result[1] for result in conversion_results):
                    results['converted'] += 1
                else:
                    results['errors'] += 1
        
        return results
    
    def generate_analysis_report(self, output_path: str = None) -> str:
        """
        Genera un reporte detallado del análisis.
        
        Args:
            output_path: Ruta donde guardar el reporte (opcional)
            
        Returns:
            String con el reporte en formato Markdown
        """
        report_lines = []
        report_lines.append("# 📊 Reporte de Análisis de Archivos Excel\n")
        report_lines.append(f"**Fecha de análisis**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append(f"**Total de archivos analizados**: {len(self.analysis_report)}\n")
        report_lines.append("\n---\n")
        
        for file_name, analysis in self.analysis_report.items():
            report_lines.append(f"\n## 📄 {file_name}\n")
            
            if 'error' in analysis:
                report_lines.append(f"**❌ Error**: {analysis['error']}\n")
                continue
            
            report_lines.append(f"- **Ruta**: `{analysis['file_path']}`")
            report_lines.append(f"- **Tamaño**: {analysis['file_size_mb']:.2f} MB")
            report_lines.append(f"- **Número de hojas**: {analysis['total_sheets']}\n")
            
            for i, sheet in enumerate(analysis['sheets'], 1):
                report_lines.append(f"\n### Hoja {i}: {sheet['name']}\n")
                report_lines.append(f"- **Dimensiones**: {sheet['rows']} filas × {sheet['columns']} columnas")
                
                # Columnas
                report_lines.append(f"\n**Columnas** ({len(sheet['column_names'])}):")
                report_lines.append("```")
                for col in sheet['column_names']:
                    col_type = sheet['column_types'].get(col, 'unknown')
                    null_count = sheet['null_counts'].get(col, 0)
                    report_lines.append(f"  - {col} ({col_type}) - Nulos: {null_count}")
                report_lines.append("```\n")
                
                # Datos de muestra
                if sheet['sample_data']:
                    report_lines.append("**Muestra de datos** (primeras 3 filas):")
                    report_lines.append("```json")
                    import json
                    report_lines.append(json.dumps(sheet['sample_data'], indent=2, ensure_ascii=False))
                    report_lines.append("```\n")
            
            report_lines.append("\n---\n")
        
        report = "\n".join(report_lines)
        
        # Guardar reporte si se especifica ruta
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"✓ Reporte guardado en: {output_path}")
        
        return report
    
    def generate_conversion_summary(self) -> str:
        """
        Genera un resumen de las conversiones realizadas.
        
        Returns:
            String con el resumen
        """
        summary = []
        summary.append("\n" + "="*60)
        summary.append("📋 RESUMEN DE CONVERSIONES")
        summary.append("="*60)
        
        successful = sum(1 for r in self.conversion_report if r['status'] == 'success')
        failed = sum(1 for r in self.conversion_report if r['status'] == 'error')
        
        summary.append(f"\n✅ Exitosos: {successful}")
        summary.append(f"❌ Fallidos: {failed}")
        summary.append(f"📊 Total: {len(self.conversion_report)}\n")
        
        if failed > 0:
            summary.append("\n❌ Archivos con errores:")
            for report in self.conversion_report:
                if report['status'] == 'error':
                    summary.append(f"  - {Path(report['original']).name}: {report.get('error', 'Unknown error')}")
        
        summary.append("\n" + "="*60 + "\n")
        
        return "\n".join(summary)


def main():
    """Función principal para ejecutar el conversor."""
    
    # Ruta base del proyecto
    base_path = Path(__file__).parent.parent / "data" / "historico"
    
    print("="*60)
    print("🔄 CONVERSOR DE EXCEL A CSV")
    print("="*60)
    print(f"\n📂 Directorio base: {base_path}\n")
    
    # Crear conversor
    converter = ExcelToCSVConverter(str(base_path))
    
    # Ejecutar conversión y análisis
    print("🔍 Buscando archivos Excel...\n")
    results = converter.convert_all(analyze=True, convert=True)
    
    # Mostrar resumen de conversión
    print(converter.generate_conversion_summary())
    
    # Generar reporte de análisis
    report_path = Path(__file__).parent.parent / "EXCEL_ANALYSIS_REPORT.md"
    print(f"📝 Generando reporte de análisis...\n")
    converter.generate_analysis_report(str(report_path))
    
    print("="*60)
    print("✅ PROCESO COMPLETADO")
    print("="*60)
    print(f"\n📊 Archivos procesados: {results['total_files']}")
    print(f"📋 Archivos analizados: {results['analyzed']}")
    print(f"✅ Archivos convertidos: {results['converted']}")
    print(f"❌ Errores: {results['errors']}")
    print(f"\n📄 Reporte detallado: {report_path}\n")


if __name__ == "__main__":
    main()
