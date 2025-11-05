# main.py
"""
Pipeline principal de procesamiento de ventas Movistar.
Optimizado para CSVs de Google Sheets.
"""

import logging
import logging.config
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import sys
import io

# Fix console encoding for Windows to support Unicode characters
if sys.platform == 'win32':
 sys.stdout = io.TextIOWrapper(
 sys.stdout.buffer, 
 encoding='utf-8', 
 errors='replace'
 )
 sys.stderr = io.TextIOWrapper(
 sys.stderr.buffer, 
 encoding='utf-8', 
 errors='replace'
 )

# Importar configuración
from config import (
 TIPIFICADOR_CONFIG,
 DIGITAL_CONFIG,
 HISTORICAL_SALES_CONFIG,
 OUTPUT_DIR,
 PROCESSED_DIR,
 OUTPUT_FILES,
 TIPIFICADOR_COLS_MAP,
 DIGITAL_COLS_MAP,
 START_DATE,
 END_DATE,
 LOGGING_CONFIG,
 INPUT_DIR,
 get_output_dir # [OK] Nueva función para carpetas organizadas por fecha
)

# Importar módulos
from src.data_loader import (
 CSVLoader,
 load_tipificador,
 load_digital,
 load_historical_sales
)
from src.data_processor import (
 TipificadorProcessor,
 DigitalProcessor,
 HistoricalSalesProcessor,
 consolidate_monthly_report
)
from src.file_generator import (
 generate_movistar_files,
 generate_internal_files,
 generate_monthly_report
 # generate_quality_reports # TODO: Implementar esta función
)
from src.generators.contact_log_generator import ContactLogGenerator
from src.eda import perform_eda

# [OK] NEW: Import ETL validator for comprehensive validation
try:
 from src.etl_validator import ETLValidator
 ETL_VALIDATOR_AVAILABLE = True
except ImportError:
 ETL_VALIDATOR_AVAILABLE = False
 logging.warning(f"[WARNING] ETL Validator not available - running without validation")

def setup_logging() -> None:
 """Configura el sistema de logging."""
 logging.config.dictConfig(LOGGING_CONFIG)

def validate_input_files() -> bool:
 """
 Valida que los archivos de entrada existan.
 
 Returns:
 True si todos los archivos existen
 """
 logger = logging.getLogger(__name__)
 
 logger.info(f"[INFO] Validando archivos de entrada...")
 
 files_to_check = [
 (INPUT_DIR / TIPIFICADOR_CONFIG['file_name'], "Tipificador"),
 (INPUT_DIR / DIGITAL_CONFIG['file_name'], "Digital"),
 ]
 
 all_exist = True
 
 for file_path, file_type in files_to_check:
   if not file_path.exists():
 logger.error(
 f"[INFO] Archivo {file_type} no encontrado: {file_path}\n"
 f" Asegúrate de exportar desde Google Sheets como CSV"
 )
 all_exist = False
 else:
 logger.info(f"[INFO] {file_type}: {file_path.name}")
 
 # Validar directorio de históricos
 hist_dir = HISTORICAL_SALES_CONFIG['dir']
 if not hist_dir.exists():
 logger.warning(
 f"[INFO] Directorio de históricos no existe: {hist_dir}\n"
 f" Se creará vacío"
 )
 hist_dir.mkdir(parents=True, exist_ok=True)
 else:
 hist_files = list(hist_dir.glob(HISTORICAL_SALES_CONFIG['pattern']))
 logger.info(f"[INFO] Históricos: {len(hist_files)} archivos encontrados")
 
 return all_exist

def main() -> int:
 """
 Función principal del pipeline.
 
 Returns:
 0 si éxito, 1 si error
 """
 # Configurar logging
 setup_logging()
 logger = logging.getLogger(__name__)
 
 # [OK] NEW: Initialize ETL validator
 if ETL_VALIDATOR_AVAILABLE:
 etl_validator = ETLValidator()
 logger.info(f"[INFO] ETL Validator initialized - comprehensive validation enabled")
 else:
 etl_validator = None
 logger.warning(f"[WARNING] Running without ETL validation")
 
 # Banner
 logger.info("=" * 80)
 logger.info(f"[INFO] MVP PROCESAMIENTO DE VENTAS MOVISTAR - VERSIÓN CSV OPTIMIZADA")
 logger.info("=" * 80)
 logger.info(f"[INFO] Periodo: {START_DATE} al {END_DATE}")
 logger.info(f"[TIME] Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 logger.info("=" * 80)
 
 # Cargar variables de entorno
 load_dotenv()
 
 # [OK] Crear carpeta de salida organizada por fecha
 output_folder = get_output_dir()
 logger.info(f"[INFO] Carpeta de salida: {output_folder.name}")
 logger.info("=" * 80)
 
 try:
 # ==========================================
 # FASE 1: VALIDACIÓN
 # ==========================================
 if not validate_input_files():
 logger.error(f"[INFO] Validación de archivos falló. Abortando.")
 return 1
 
 # ==========================================
 # FASE 2: INGESTA DE DATOS
 # ==========================================
 logger.info("\n" + "=" * 80)
 logger.info("[INPUT] FASE 1: INGESTA DE DATOS")
 logger.info("=" * 80)
 
 # Cargar Tipificador
 logger.info("\n[1/3] Cargando Tipificador...")
 tipificador_config = {
 **TIPIFICADOR_CONFIG,
 'file_path': INPUT_DIR / TIPIFICADOR_CONFIG['file_name']
 }
 tipificador_raw_df = load_tipificador(tipificador_config)
 
 # [OK] NEW: Validate load
 if etl_validator:
 result = etl_validator.validate_load(
 df=tipificador_raw_df,
 file_name='Tipificador',
 expected_columns=list(TIPIFICADOR_COLS_MAP.keys())[:5], # Check first 5 columns
 min_records=10
 )
 if not result.passed:
 logger.error(f"[ERROR] Tipificador load validation failed: {result.message}")
 # Continue with warning (don't abort)
 
 # Cargar Digital
 logger.info("\n[2/3] Cargando Ventas Digitales...")
 digital_config = {
 **DIGITAL_CONFIG,
 'file_path': INPUT_DIR / DIGITAL_CONFIG['file_name']
 }
 digital_raw_df = load_digital(digital_config)
 
 # [OK] NEW: Validate load
 if etl_validator:
 etl_validator.validate_load(
 df=digital_raw_df,
 file_name='Digital',
 expected_columns=list(DIGITAL_COLS_MAP.keys())[:3],
 min_records=5
 )
 
 # Cargar Históricos
 logger.info("\n[3/3] Cargando Ventas Históricas...")
 historical_sales_df = load_historical_sales(HISTORICAL_SALES_CONFIG)
 
 logger.info(f"\n{} Ingesta completada")
 
 # ==========================================
 # FASE 3: ANÁLISIS EXPLORATORIO
 # ==========================================
 logger.info("\n" + "=" * 80)
 logger.info(f"[INFO] FASE 2: ANÁLISIS EXPLORATORIO DE DATOS (EDA)")
 logger.info("=" * 80)
 
 if not tipificador_raw_df.empty:
 perform_eda(tipificador_raw_df, "Tipificador_Raw", PROCESSED_DIR)
 
 if not digital_raw_df.empty:
 perform_eda(digital_raw_df, "Digital_Raw", PROCESSED_DIR)
 
 if not historical_sales_df.empty:
 perform_eda(historical_sales_df, "Historicos_Raw", PROCESSED_DIR)
 
 logger.info(f"\n{} EDA completado")
 
 # ==========================================
 # FASE 4: PROCESAMIENTO
 # ==========================================
 logger.info("\n" + "=" * 80)
 logger.info("[CONFIG] FASE 3: PROCESAMIENTO DE DATOS")
 logger.info("=" * 80)
 
 # Procesar Tipificador
 logger.info("\n[1/4] Procesando Tipificador...")
 
 # Store counts before processing
 tipificador_count_before = len(tipificador_raw_df)
 
 df_ventas_mes, df_referidos_mes, df_invalid, metrics_tip = TipificadorProcessor.process(
 tipificador_raw_df,
 TIPIFICADOR_COLS_MAP,
 START_DATE,
 END_DATE
 )
 
 # [OK] NEW: Validate transformation
 if etl_validator:
 etl_validator.validate_transform(
 df_before=tipificador_raw_df,
 df_after=df_ventas_mes,
 transform_name='tipificador_processing',
 min_retention=50.0, # Expect at least 50% retention
 max_retention=100.0
 )
 
 # Procesar Digital
 logger.info("\n[2/4] Procesando Ventas Digitales...")
 df_digital_processed_mes, metrics_dig = DigitalProcessor.process(
 digital_raw_df,
 DIGITAL_COLS_MAP,
 START_DATE,
 END_DATE
 )
 
 # Procesar Históricos
 logger.info("\n[3/4] Procesando Ventas Históricas...")
 df_historical_processed, metrics_hist = HistoricalSalesProcessor.process(
 historical_sales_df
 )
 
 # Consolidar Reporte Mensual
 logger.info("\n[4/4] Consolidando Reporte Mensual...")
 df_monthly_consolidated, metrics_monthly = consolidate_monthly_report(
 df_ventas_mes,
 df_digital_processed_mes,
 df_historical_processed
 )
 
 logger.info(f"\n{} Procesamiento completado")
 
 # ==========================================
 # FASE 5: FILTRADO POR PERIODO
 # ==========================================
 logger.info("\n" + "=" * 80)
 logger.info(f"[INFO] FASE 4: FILTRADO POR PERIODO")
 logger.info("=" * 80)
 
 df_ventas_periodo = df_ventas_mes[
 (df_ventas_mes['fecha_venta'] >= START_DATE) &
 (df_ventas_mes['fecha_venta'] <= END_DATE)
 ].copy()
 
 df_digital_periodo = df_digital_processed_mes[
 (df_digital_processed_mes['fecha_venta'] >= START_DATE) &
 (df_digital_processed_mes['fecha_venta'] <= END_DATE)
 ].copy()
 
 logger.info(
 f"[INFO] Filtrado: {len(df_ventas_periodo):,} ventas base + "
 f"{len(df_digital_periodo):,} digitales para el periodo"
 )
 
 # ==========================================
 # FASE 6: GENERACIÓN DE ARCHIVOS
 # ==========================================
 logger.info("\n" + "=" * 80)
 logger.info(f"[INFO] FASE 5: GENERACIÓN DE ARCHIVOS DE SALIDA")
 logger.info("=" * 80)
 
 # Generar archivos para Movistar
 generate_movistar_files(df_ventas_periodo, OUTPUT_FILES, output_folder)
 
 # Generar archivos internos
 generate_internal_files(
 df_digital_periodo,
 df_ventas_periodo,
 OUTPUT_FILES,
 output_folder
 )
 
 # Generar reporte mensual
 generate_monthly_report(
 df_monthly_consolidated,
 df_digital_processed_mes,
 OUTPUT_FILES,
 output_folder
 )
 
 # Generar Contact Log (nueva funcionalidad automatizada)
 logger.info("\n[4/4] Generando Contact Log...")
 try:
 contact_log_generator = ContactLogGenerator()
 contact_log_path = output_folder / OUTPUT_FILES['movistar_contact_log']
 
 success = contact_log_generator.generate(
 df_ventas_periodo,
 contact_log_path,
 validate=True
 )
 
 if success:
 logger.info(
 f"[INFO] Contact Log generado: {contact_log_path.name}\n"
 f" Registros procesados: {contact_log_generator.records_processed:,}\n"
 f" Registros omitidos: {contact_log_generator.records_skipped:,}"
 )
 else:
 logger.warning(f"[WARNING] Contact Log no pudo ser generado")
 except Exception as e:
 logger.error(f"[ERROR] Error generando Contact Log: {e}", exc_info=True)
 
 # [OK] Generar archivo de NOVEDADES (registros rechazados)
 logger.info("\n[5/5] Generando archivo de NOVEDADES...")
 try:
 from src.generators.novedades_generator import NovedadesGenerator
 
 novedades_generator = NovedadesGenerator()
 novedades_path = output_folder / OUTPUT_FILES.get('novedades', 'NOVEDADES.xlsx')
 
 # Generar archivo de NOVEDADES solo si hay registros inválidos
 success = novedades_generator.generate(
 df_invalid,
 novedades_path
 )
 
 if success and not df_invalid.empty:
 logger.info(
 f"[INFO] Archivo de NOVEDADES generado: {novedades_path.name}\n"
 f" Registros rechazados: {len(df_invalid):,}"
 )
 elif df_invalid.empty:
 logger.info(f"[INFO] No hay registros rechazados - archivo de NOVEDADES no necesario")
 else:
 logger.warning(f"[WARNING] Archivo de NOVEDADES no pudo ser generado")
 except Exception as e:
 logger.error(f"[ERROR] Error generando archivo de NOVEDADES: {e}", exc_info=True)
 
 # Consolidar todas las métricas
 all_metrics = {
 'tipificador': metrics_tip,
 'digital': metrics_dig,
 'historicos': metrics_hist,
 'consolidado_mensual': metrics_monthly,
 'periodo_procesado': {
 'inicio': str(START_DATE),
 'fin': str(END_DATE),
 'ventas_periodo': len(df_ventas_periodo),
 'digital_periodo': len(df_digital_periodo),
 }
 }
 
 # Generar reporte de calidad
 # TODO: Implementar generate_quality_reports()
 logger.info(f"[INFO] Reportes de calidad pendientes de implementación")
 
 logger.info(f"\n{} Archivos de salida generados")
 
 # ==========================================
 # [OK] NEW: VALIDATION REPORT
 # ==========================================
 if etl_validator:
 logger.info("\n" + "=" * 80)
 logger.info(f"[INFO] GENERANDO REPORTE DE VALIDACIÓN")
 logger.info("=" * 80)
 
 # Check for critical issues
 if etl_validator.has_critical_issues():
 logger.error("[EMOJI] CRITICAL VALIDATION ISSUES DETECTED!")
 for check in etl_validator.get_failed_checks():
 if check.severity == 'CRITICAL':
 logger.error(f" - {check.message}")
 
 # Export validation report
 validation_report_path = PROCESSED_DIR / 'ETL_validation_report.xlsx'
 etl_validator.export_report(validation_report_path)
 
 logger.info(f"[INFO] Validation report exported: {validation_report_path.name}")
 
 # Show summary
 df_report = etl_validator.generate_etl_report()
 passed = df_report['passed'].sum()
 total = len(df_report)
 logger.info(f" Validations: {passed}/{total} passed")
 
 # ==========================================
 # RESUMEN FINAL
 # ==========================================
 logger.info("\n" + "=" * 80)
 logger.info(f"[INFO] RESUMEN DE EJECUCIÓN")
 logger.info("=" * 80)
 logger.info(f"[INFO] Ventas procesadas: {len(df_ventas_periodo):,}")
 logger.info(f"[INFO] Ventas digitales: {len(df_digital_periodo):,}")
 logger.info(f"[INFO] Referidos identificados: {len(df_referidos_mes):,}")
 logger.info(f"[INFO] Registros rechazados: {len(df_invalid):,}")
 logger.info(f"[INFO] Reporte mensual: {len(df_monthly_consolidated):,} ventas únicas")
 logger.info(f"[INFO] Contact Log: {contact_log_generator.records_processed:,} registros")
 logger.info(f"[INFO] Archivos generados en: {output_folder.name}")
 logger.info(f" Ruta completa: {output_folder}")
 logger.info(f"[INFO] Reportes EDA en: {PROCESSED_DIR}")
 logger.info("=" * 80)
 logger.info(f"[TIME] Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
 logger.info("=" * 80)
 logger.info("[SUCCESS] MVP EJECUTADO EXITOSAMENTE")
 logger.info("=" * 80)
 
 return 0
 
 except KeyboardInterrupt:
 logger.warning(f"\n{} Ejecución interrumpida por el usuario")
 return 1
 
 except Exception as e:
 logger.error(f"\n{} ERROR CRÍTICO: {e}", exc_info=True)
 return 1

if __name__ == "__main__":
 sys.exit(main())