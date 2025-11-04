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
import pandas as pd

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
    get_output_dir  # ✅ NUEVO: Función para obtener carpeta con fecha
)

# Importar módulos
from src.data_loader import (
    CSVLoader,
    load_tipificador,
    load_digital,
    load_historical_sales
)
# ⚠️ NOTA: src.data_processor no existe, comentando importación
# from src.data_processor import (
#     TipificadorProcessor,
#     DigitalProcessor,
#     HistoricalSalesProcessor,
#     consolidate_monthly_report
# )
from src.file_generator import (
    generate_movistar_files,
    generate_internal_files,
    generate_monthly_report
)
from src.generators.contact_log_generator import ContactLogGenerator
from src.eda import perform_eda

# ✅ NEW: Import ETL validator for comprehensive validation
try:
    from src.etl_validator import ETLValidator
    ETL_VALIDATOR_AVAILABLE = True
except ImportError:
    ETL_VALIDATOR_AVAILABLE = False
    logging.warning("⚠️ ETL Validator not available - running without validation")


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
    
    logger.info("🔍 Validando archivos de entrada...")
    
    files_to_check = [
        (INPUT_DIR / TIPIFICADOR_CONFIG['file_name'], "Tipificador"),
        (INPUT_DIR / DIGITAL_CONFIG['file_name'], "Digital"),
    ]
    
    all_exist = True
    
    for file_path, file_type in files_to_check:
        if not file_path.exists():
            logger.error(
                f"❌ Archivo {file_type} no encontrado: {file_path}\n"
                f"   Asegúrate de exportar desde Google Sheets como CSV"
            )
            all_exist = False
        else:
            logger.info(f"✅ {file_type}: {file_path.name}")
    
    # Validar directorio de históricos
    hist_dir = HISTORICAL_SALES_CONFIG['dir']
    if not hist_dir.exists():
        logger.warning(
            f"⚠️ Directorio de históricos no existe: {hist_dir}\n"
            f"   Se creará vacío"
        )
        hist_dir.mkdir(parents=True, exist_ok=True)
    else:
        hist_files = list(hist_dir.glob(HISTORICAL_SALES_CONFIG['pattern']))
        logger.info(f"✅ Históricos: {len(hist_files)} archivos encontrados")
    
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
    
    # ✅ NEW: Initialize ETL validator
    if ETL_VALIDATOR_AVAILABLE:
        etl_validator = ETLValidator()
        logger.info("✅ ETL Validator initialized - comprehensive validation enabled")
    else:
        etl_validator = None
        logger.warning("⚠️ Running without ETL validation")
    
    # ✅ NUEVO: Crear carpeta de salida con fecha y rango
    output_dir_with_date = get_output_dir()
    
    # Banner
    logger.info("=" * 80)
    logger.info("🚀 MVP PROCESAMIENTO DE VENTAS MOVISTAR - VERSIÓN CSV OPTIMIZADA")
    logger.info("=" * 80)
    logger.info(f"📅 Periodo de datos: {START_DATE.strftime('%d/%m/%Y')} → {END_DATE.strftime('%d/%m/%Y')}")
    logger.info(f"📁 Carpeta de salida: {output_dir_with_date.name}")
    logger.info(f"⏰ Inicio de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    # Cargar variables de entorno
    load_dotenv()
    
    try:
        # ==========================================
        # FASE 1: VALIDACIÓN
        # ==========================================
        if not validate_input_files():
            logger.error("❌ Validación de archivos falló. Abortando.")
            return 1
        
        # ==========================================
        # FASE 2: INGESTA DE DATOS
        # ==========================================
        logger.info("\n" + "=" * 80)
        logger.info("📥 FASE 1: INGESTA DE DATOS")
        logger.info("=" * 80)
        
        # Cargar Tipificador
        logger.info("\n[1/3] Cargando Tipificador...")
        tipificador_config = {
            **TIPIFICADOR_CONFIG,
            'file_path': INPUT_DIR / TIPIFICADOR_CONFIG['file_name']
        }
        tipificador_raw_df = load_tipificador(tipificador_config)
        
        # ✅ NEW: Validate load
        if etl_validator:
            result = etl_validator.validate_load(
                df=tipificador_raw_df,
                file_name='Tipificador',
                expected_columns=list(TIPIFICADOR_COLS_MAP.keys())[:5],  # Check first 5 columns
                min_records=10
            )
            if not result.passed:
                logger.error(f"❌ Tipificador load validation failed: {result.message}")
                # Continue with warning (don't abort)
        
        # Cargar Digital
        logger.info("\n[2/3] Cargando Ventas Digitales...")
        digital_config = {
            **DIGITAL_CONFIG,
            'file_path': INPUT_DIR / DIGITAL_CONFIG['file_name']
        }
        digital_raw_df = load_digital(digital_config)
        
        # ✅ NEW: Validate load
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
        
        logger.info("\n✅ Ingesta completada")
        
        # ==========================================
        # FASE 3: ANÁLISIS EXPLORATORIO
        # ==========================================
        logger.info("\n" + "=" * 80)
        logger.info("📊 FASE 2: ANÁLISIS EXPLORATORIO DE DATOS (EDA)")
        logger.info("=" * 80)
        
        if not tipificador_raw_df.empty:
            perform_eda(tipificador_raw_df, "Tipificador_Raw", PROCESSED_DIR)
        
        if not digital_raw_df.empty:
            perform_eda(digital_raw_df, "Digital_Raw", PROCESSED_DIR)
        
        if not historical_sales_df.empty:
            perform_eda(historical_sales_df, "Historicos_Raw", PROCESSED_DIR)
        
        logger.info("\n✅ EDA completado")
        
        # ==========================================
        # FASE 4: PROCESAMIENTO
        # ==========================================
        logger.info("\n" + "=" * 80)
        logger.info("⚙️  FASE 3: PROCESAMIENTO DE DATOS")
        logger.info("=" * 80)
        
        # Procesar Tipificador
        logger.info("\n[1/4] Procesando Tipificador...")
        
        # Store counts before processing
        tipificador_count_before = len(tipificador_raw_df)
        
        df_ventas_mes, df_referidos_mes, metrics_tip = TipificadorProcessor.process(
            tipificador_raw_df,
            TIPIFICADOR_COLS_MAP,
            START_DATE,
            END_DATE
        )
        
        # ✅ NEW: Validate transformation
        if etl_validator:
            etl_validator.validate_transform(
                df_before=tipificador_raw_df,
                df_after=df_ventas_mes,
                transform_name='tipificador_processing',
                min_retention=50.0,  # Expect at least 50% retention
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
        
        logger.info("\n✅ Procesamiento completado")
        
        # ==========================================
        # FASE 5: FILTRADO POR PERIODO
        # ==========================================
        logger.info("\n" + "=" * 80)
        logger.info("🔍 FASE 4: FILTRADO POR PERIODO")
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
            f"✅ Filtrado: {len(df_ventas_periodo):,} ventas base + "
            f"{len(df_digital_periodo):,} digitales para el periodo"
        )
        
        # ==========================================
        # FASE 6: GENERACIÓN DE ARCHIVOS
        # ==========================================
        logger.info("\n" + "=" * 80)
        logger.info("📤 FASE 5: GENERACIÓN DE ARCHIVOS DE SALIDA")
        logger.info("=" * 80)
        
        # ✅ USAR: Carpeta con fecha de generación
        # Generar archivos para Movistar
        generate_movistar_files(df_ventas_periodo, OUTPUT_FILES, output_dir_with_date)
        
        # Generar archivos internos
        generate_internal_files(
            df_digital_periodo,
            df_ventas_periodo,
            OUTPUT_FILES,
            output_dir_with_date
        )
        
        # Generar reporte mensual
        generate_monthly_report(
            df_monthly_consolidated,
            df_digital_periodo,
            OUTPUT_FILES,
            output_dir_with_date
        )
        
        # Generar Contact Log (nueva funcionalidad automatizada)
        logger.info("\n[4/4] Generando Contact Log...")
        try:
            contact_log_generator = ContactLogGenerator()
            contact_log_path = output_dir_with_date / OUTPUT_FILES['movistar_contact_log']
            
            success = contact_log_generator.generate(
                df_ventas_periodo,
                contact_log_path,
                validate=True
            )
            
            if success:
                logger.info(
                    f"✅ Contact Log generado: {contact_log_path.name}\n"
                    f"   Registros procesados: {contact_log_generator.records_processed:,}\n"
                    f"   Registros omitidos: {contact_log_generator.records_skipped:,}"
                )
            else:
                logger.warning("⚠️ Contact Log no pudo ser generado")
        except Exception as e:
            logger.error(f"❌ Error generando Contact Log: {e}", exc_info=True)
        
        # ✅ NEW: Generate novelty reports (invalid records for operations review)
        logger.info("\n[5/5] Generando Reportes de Novedades...")
        try:
            from src.services.novelty_detector import NoveltyDetector
            detector = NoveltyDetector()
            
            # Combine novelties from tipificador and digital
            df_novedades_tip = metrics_tip.get('df_novedades', pd.DataFrame())
            df_novedades_dig = metrics_dig.get('df_novedades', pd.DataFrame())
            
            total_novedades = len(df_novedades_tip) + len(df_novedades_dig)
            
            if total_novedades > 0:
                # Generate separate reports
                if not df_novedades_tip.empty:
                    novelty_tip_path = output_dir_with_date / f"Tipificador_Novedades_{OUTPUT_FILES['date_range_short']}.xlsx"
                    detector.generate_novelty_report(df_novedades_tip, str(novelty_tip_path))
                
                if not df_novedades_dig.empty:
                    novelty_dig_path = output_dir_with_date / f"Digital_Novedades_{OUTPUT_FILES['date_range_short']}.xlsx"
                    detector.generate_novelty_report(df_novedades_dig, str(novelty_dig_path))
                
                logger.info(f"✅ Reportes de novedades generados:")
                logger.info(f"   ⚠️  Tipificador: {len(df_novedades_tip):,} novedades")
                logger.info(f"   ⚠️  Digital: {len(df_novedades_dig):,} novedades")
            else:
                logger.info("✅ No hay novedades - todos los registros son válidos")
        except Exception as e:
            logger.error(f"❌ Error generando reportes de novedades: {e}", exc_info=True)
        
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
        logger.info("⚠️ Reportes de calidad pendientes de implementación")
        
        logger.info("\n✅ Archivos de salida generados")
        
        # ==========================================
        # ✅ NEW: VALIDATION REPORT
        # ==========================================
        if etl_validator:
            logger.info("\n" + "=" * 80)
            logger.info("📊 GENERANDO REPORTE DE VALIDACIÓN")
            logger.info("=" * 80)
            
            # Check for critical issues
            if etl_validator.has_critical_issues():
                logger.error("🚨 CRITICAL VALIDATION ISSUES DETECTED!")
                for check in etl_validator.get_failed_checks():
                    if check.severity == 'CRITICAL':
                        logger.error(f"  - {check.message}")
            
            # Export validation report
            validation_report_path = PROCESSED_DIR / 'ETL_validation_report.xlsx'
            etl_validator.export_report(validation_report_path)
            
            logger.info(f"✅ Validation report exported: {validation_report_path.name}")
            
            # Show summary
            df_report = etl_validator.generate_etl_report()
            passed = df_report['passed'].sum()
            total = len(df_report)
            logger.info(f"   Validations: {passed}/{total} passed")
        
        # ==========================================
        # RESUMEN FINAL
        # ==========================================
        # Calculate novelties
        total_novedades = len(metrics_tip.get('df_novedades', pd.DataFrame())) + len(metrics_dig.get('df_novedades', pd.DataFrame()))
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMEN DE EJECUCIÓN")
        logger.info("=" * 80)
        logger.info(f"✅ Ventas procesadas: {len(df_ventas_periodo):,}")
        logger.info(f"✅ Ventas digitales: {len(df_digital_periodo):,}")
        logger.info(f"⚠️  Novedades detectadas: {total_novedades:,}")
        logger.info(f"✅ Referidos identificados: {len(df_referidos_mes):,}")
        logger.info(f"✅ Reporte mensual: {len(df_monthly_consolidated):,} ventas únicas")
        logger.info(f"✅ Contact Log: {contact_log_generator.records_processed:,} registros")
        logger.info(f"📁 Archivos generados en: {output_dir_with_date}")
        logger.info(f"📁 Ruta completa: {output_dir_with_date.absolute()}")
        logger.info(f"📊 Reportes EDA en: {PROCESSED_DIR}")
        if total_novedades > 0:
            logger.info(f"⚠️  Reportes de novedades en: {output_dir_with_date}")
        logger.info("=" * 80)
        logger.info(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        logger.info("🎉 MVP EJECUTADO EXITOSAMENTE")
        logger.info("=" * 80)
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Ejecución interrumpida por el usuario")
        return 1
    
    except Exception as e:
        logger.error(f"\n❌ ERROR CRÍTICO: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())