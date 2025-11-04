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
    INPUT_DIR
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
    generate_monthly_report,
    generate_quality_reports
)
from src.eda import perform_eda


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
    
    # Banner
    logger.info("=" * 80)
    logger.info("🚀 MVP PROCESAMIENTO DE VENTAS MOVISTAR - VERSIÓN CSV OPTIMIZADA")
    logger.info("=" * 80)
    logger.info(f"📅 Periodo: {START_DATE} → {END_DATE}")
    logger.info(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
        
        # Cargar Digital
        logger.info("\n[2/3] Cargando Ventas Digitales...")
        digital_config = {
            **DIGITAL_CONFIG,
            'file_path': INPUT_DIR / DIGITAL_CONFIG['file_name']
        }
        digital_raw_df = load_digital(digital_config)
        
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
        df_ventas_mes, df_referidos_mes, metrics_tip = TipificadorProcessor.process(
            tipificador_raw_df,
            TIPIFICADOR_COLS_MAP,
            START_DATE,
            END_DATE
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
        
        # Generar archivos para Movistar
        generate_movistar_files(df_ventas_periodo, OUTPUT_FILES, OUTPUT_DIR)
        
        # Generar archivos internos
        generate_internal_files(
            df_digital_periodo,
            df_ventas_periodo,
            OUTPUT_FILES,
            OUTPUT_DIR
        )
        
        # Generar reporte mensual
        generate_monthly_report(
            df_monthly_consolidated,
            df_digital_processed_mes,
            OUTPUT_FILES,
            OUTPUT_DIR
        )
        
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
        generate_quality_reports(all_metrics, OUTPUT_DIR, OUTPUT_FILES)
        
        logger.info("\n✅ Archivos de salida generados")
        
        # ==========================================
        # RESUMEN FINAL
        # ==========================================
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMEN DE EJECUCIÓN")
        logger.info("=" * 80)
        logger.info(f"✅ Ventas procesadas: {len(df_ventas_periodo):,}")
        logger.info(f"✅ Ventas digitales: {len(df_digital_periodo):,}")
        logger.info(f"✅ Referidos identificados: {len(df_referidos_mes):,}")
        logger.info(f"✅ Reporte mensual: {len(df_monthly_consolidated):,} ventas únicas")
        logger.info(f"📁 Archivos generados en: {OUTPUT_DIR}")
        logger.info(f"📊 Reportes EDA en: {PROCESSED_DIR}")
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