"""
Script simplificado para generar archivos Movistar.
Procesa datos del 23 al 31 de octubre de 2024.
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar configuración
from config import (
    INPUT_DIR,
    START_DATE,
    END_DATE,
    get_output_dir,
    TIPIFICADOR_CONFIG,
    DIGITAL_CONFIG,
)

def main():
    """Procesa y genera archivos de ventas Movistar."""
    
    logger.info("=" * 80)
    logger.info("🚀 PROCESAMIENTO SIMPLE DE VENTAS MOVISTAR")
    logger.info("=" * 80)
    
    # Crear carpeta de salida con fecha
    output_dir = get_output_dir()
    logger.info(f"📁 Carpeta de salida: {output_dir.name}")
    logger.info(f"📅 Periodo: {START_DATE.strftime('%d/%m/%Y')} → {END_DATE.strftime('%d/%m/%Y')}")
    logger.info(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    try:
        # 1. Cargar Tipificador
        logger.info("\n[1/2] Cargando Tipificador...")
        tipificador_path = INPUT_DIR / TIPIFICADOR_CONFIG['file_name']
        logger.info(f"📄 Archivo: {tipificador_path.name}")
        
        df_tipificador = pd.read_csv(
            tipificador_path,
            encoding='utf-8-sig',
            sep=',',
            engine='python'
        )
        logger.info(f"✅ Cargadas {len(df_tipificador):,} filas")
        logger.info(f"   Columnas: {list(df_tipificador.columns[:5])}...")
        
        # 2. Cargar Digital
        logger.info("\n[2/2] Cargando Ventas Digitales...")
        digital_path = INPUT_DIR / DIGITAL_CONFIG['file_name']
        logger.info(f"📄 Archivo: {digital_path.name}")
        
        df_digital = pd.read_csv(
            digital_path,
            encoding='utf-8-sig',
            sep=',',
            engine='python'
        )
        logger.info(f"✅ Cargadas {len(df_digital):,} filas")
        logger.info(f"   Columnas: {list(df_digital.columns[:5])}...")
        
        # 3. Crear archivo de resumen simple
        logger.info("\n" + "=" * 80)
        logger.info("📊 GENERANDO ARCHIVO DE RESUMEN")
        logger.info("=" * 80)
        
        resumen_file = output_dir / f"RESUMEN_Procesamiento_{START_DATE.strftime('%d%m%Y')}_al_{END_DATE.strftime('%d%m%Y')}.xlsx"
        
        with pd.ExcelWriter(resumen_file, engine='xlsxwriter') as writer:
            # Hoja 1: Resumen de datos
            resumen_data = {
                'Archivo': ['Tipificador', 'Digital'],
                'Total Registros': [len(df_tipificador), len(df_digital)],
                'Columnas': [len(df_tipificador.columns), len(df_digital.columns)],
                'Periodo Inicio': [START_DATE.strftime('%d/%m/%Y'), START_DATE.strftime('%d/%m/%Y')],
                'Periodo Fin': [END_DATE.strftime('%d/%m/%Y'), END_DATE.strftime('%d/%m/%Y')],
                'Fecha Generación': [datetime.now().strftime('%d/%m/%Y %H:%M'), datetime.now().strftime('%d/%m/%Y %H:%M')]
            }
            df_resumen = pd.DataFrame(resumen_data)
            df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
            
            # Hoja 2: Muestra Tipificador (primeras 100 filas)
            df_tipificador.head(100).to_excel(writer, sheet_name='Muestra_Tipificador', index=False)
            
            # Hoja 3: Muestra Digital (primeras 100 filas)
            df_digital.head(100).to_excel(writer, sheet_name='Muestra_Digital', index=False)
            
            logger.info(f"✅ Archivo generado: {resumen_file.name}")
        
        # 4. Información sobre columnas
        logger.info("\n" + "=" * 80)
        logger.info("📋 INFORMACIÓN DE DATOS")
        logger.info("=" * 80)
        
        logger.info(f"\n📱 TIPIFICADOR:")
        logger.info(f"   Total registros: {len(df_tipificador):,}")
        logger.info(f"   Columnas ({len(df_tipificador.columns)}):")
        for i, col in enumerate(df_tipificador.columns[:10], 1):
            logger.info(f"      {i}. {col}")
        if len(df_tipificador.columns) > 10:
            logger.info(f"      ... y {len(df_tipificador.columns) - 10} más")
        
        logger.info(f"\n💻 DIGITAL:")
        logger.info(f"   Total registros: {len(df_digital):,}")
        logger.info(f"   Columnas ({len(df_digital.columns)}):")
        for i, col in enumerate(df_digital.columns[:10], 1):
            logger.info(f"      {i}. {col}")
        if len(df_digital.columns) > 10:
            logger.info(f"      ... y {len(df_digital.columns) - 10} más")
        
        # Resumen final
        logger.info("\n" + "=" * 80)
        logger.info("✅ PROCESAMIENTO COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"📁 Archivos en: {output_dir}")
        logger.info(f"📁 Ruta completa: {output_dir.absolute()}")
        logger.info(f"⏰ Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)
        
        logger.info("\n🎯 PRÓXIMOS PASOS:")
        logger.info("   1. Revisar el archivo RESUMEN generado")
        logger.info("   2. Verificar las columnas de datos")
        logger.info("   3. Implementar procesadores específicos si es necesario")
        logger.info("   4. Los códigos de servicio correctos ya están en ServiceCodeMapper")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
