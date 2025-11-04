# src/data_processor.py
"""
Procesamiento de lógica de negocio para ventas Movistar.
Versión mejorada con extracción de hora y validaciones robustas.
"""

import pandas as pd
import logging
from datetime import date
from typing import Tuple, Dict, Any

# Intentar importar decorators del nuevo sistema
try:
    from src.core.decorators import timing, log_execution, retry
except ImportError:
    # Fallback: decorators no-op si el módulo no está disponible
    def timing(func):
        return func
    def log_execution(func):
        return func
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from src.validators import PhoneNumberValidator, DataQualityValidator
from src.utils import (
    validate_columns,
    extract_datetime_components,
    find_duplicates,
    find_empaquetados,
    filter_by_date_range,
    detect_referidos,
    generate_summary_stats
)
from config import get_service_code

logger = logging.getLogger(__name__)


class TipificadorProcessor:
    """Procesador para datos del Tipificador de Ventas."""
    
    @staticmethod
    @timing
    @log_execution
    def process(
        df: pd.DataFrame,
        col_map: Dict[str, str],
        start_date: date,
        end_date: date
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Procesa el Tipificador de Ventas completo.
        
        Args:
            df: DataFrame crudo del tipificador
            col_map: Mapeo de nombres de columnas
            start_date: Fecha de inicio del periodo
            end_date: Fecha de fin del periodo
        
        Returns:
            (df_ventas, df_referidos, metrics)
        """
        logger.info("=" * 80)
        logger.info("🔄 PROCESANDO TIPIFICADOR DE VENTAS")
        logger.info("=" * 80)
        
        # 1. Renombrar columnas (flexible para variantes)
        df = TipificadorProcessor._rename_columns(df, col_map)
        
        # 2. Validar columnas requeridas
        required_cols = [
            'telefono_servicio', 'nombre_cliente', 'tipo_venta',
            'es_referido', 'marca_temporal', 'nombre_asesor'
        ]
        validate_columns(df, required_cols, "Tipificador")
        
        # 3. Extraer componentes de fecha y hora
        logger.info("📅 Extrayendo fecha y hora de marca temporal...")
        datetime_components = df['marca_temporal'].apply(extract_datetime_components)
        
        df['fecha_alta'] = datetime_components.apply(lambda x: x['fecha_alta'])
        df['hora_venta'] = datetime_components.apply(lambda x: x['hora_venta'])
        df['fecha_venta'] = datetime_components.apply(lambda x: x['fecha_date'])
        df['hora_24h'] = datetime_components.apply(lambda x: x['hora_24h'])
        
        valid_dates = df['fecha_venta'].notna().sum()
        logger.info(f"   ✅ Extraídas {valid_dates:,} fechas válidas")
        
        # 4. Limpiar y validar teléfonos
        logger.info("📞 Limpiando números telefónicos...")
        cleaned_phones, phone_metadata = PhoneNumberValidator.clean_series(
            df['telefono_servicio'],
            return_metadata=True
        )
        
        df['telefono_limpio'] = cleaned_phones
        df['tipo_linea'] = phone_metadata['tipo_linea']
        df['telefono_valido'] = phone_metadata['es_valido']
        df['telefono_tiene_indicativo'] = phone_metadata['tiene_indicativo']
        
        # 5. Determinar código de servicio y programa
        logger.info("🏷️  Asignando códigos de servicio...")
        service_info = df['tipo_venta'].apply(
            lambda x: get_service_code(x, es_digital=False)
        )
        
        df['cod_servicio'] = service_info.apply(lambda x: x[0])
        df['programa'] = service_info.apply(lambda x: x[1])
        
        # 6. Eliminar registros inválidos
        df_valid = df[
            df['telefono_limpio'].notna() & 
            df['fecha_venta'].notna()
        ].copy()
        
        removed_count = len(df) - len(df_valid)
        if removed_count > 0:
            logger.warning(
                f"⚠️ Eliminados {removed_count:,} registros con datos inválidos"
            )
        
        # 7. Filtrar por rango de fechas
        df_valid = filter_by_date_range(
            df_valid, 'fecha_venta', start_date, end_date
        )
        
        # 8. Detectar referidos
        df_valid = detect_referidos(df_valid)
        
        # Separar ventas de base vs referidos
        df_referidos = df_valid[df_valid['is_referido']].copy()
        df_ventas = df_valid[~df_valid['is_referido']].copy()
        
        logger.info(
            f"📊 Separación: {len(df_ventas):,} ventas de base, "
            f"{len(df_referidos):,} referidos"
        )
        
        # 9. Detectar duplicados en ventas de base
        logger.info("🔍 Detectando duplicados en ventas de base...")
        df_ventas = find_duplicates(
            df_ventas,
            subset_cols=['telefono_limpio', 'tipo_venta']
        )
        
        # 10. Detectar empaquetados
        df_ventas = find_empaquetados(
            df_ventas,
            phone_col='telefono_limpio',
            plan_col='tipo_venta'
        )
        
        # 11. Validar clasificación de líneas
        logger.info("🔍 Validando clasificación de líneas...")
        TipificadorProcessor._validate_line_classification(df_ventas)
        
        # 12. Generar métricas
        metrics = {
            'tipificador': generate_summary_stats(df, "Tipificador Original"),
            'ventas_procesadas': generate_summary_stats(df_ventas, "Ventas Base"),
            'referidos': generate_summary_stats(df_referidos, "Referidos"),
            'telefonos_invalidos': removed_count,
            'periodo': f"{start_date} - {end_date}",
        }
        
        # Agregar métricas de teléfonos
        phone_stats = phone_metadata.groupby('tipo_linea').size().to_dict()
        metrics['distribucion_tipo_linea'] = phone_stats
        
        # Métricas de duplicados
        duplicates_count = (df_ventas['duplicate_status'] == 'duplicado').sum()
        empaquetados_count = df_ventas['is_empaquetado'].sum()
        
        metrics['duplicados'] = duplicates_count
        metrics['empaquetados'] = empaquetados_count
        
        # Métricas por asesor
        if 'nombre_asesor' in df_ventas.columns:
            ventas_por_asesor = df_ventas.groupby('nombre_asesor').agg({
                'telefono_limpio': 'count',
                'is_empaquetado': 'sum'
            }).to_dict()
            metrics['ventas_por_asesor'] = ventas_por_asesor
        
        logger.info("=" * 80)
        logger.info("✅ PROCESAMIENTO DEL TIPIFICADOR COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"   📊 Ventas de base: {len(df_ventas):,}")
        logger.info(f"   🔖 Referidos: {len(df_referidos):,}")
        logger.info(f"   ❌ Duplicados: {duplicates_count:,}")
        logger.info(f"   📦 Empaquetados: {empaquetados_count:,}")
        logger.info(f"   📱 Móviles: {phone_stats.get('MOVIL', 0):,}")
        logger.info(f"   ☎️  Fijos: {phone_stats.get('FIJA', 0):,}")
        logger.info("=" * 80)
        
        return df_ventas, df_referidos, metrics
    
    @staticmethod
    def _rename_columns(df: pd.DataFrame, col_map: Dict[str, str]) -> pd.DataFrame:
        """Renombra columnas de forma flexible (maneja variantes)."""
        df = df.copy()
        
        # Crear un mapeo case-insensitive
        df_cols_lower = {col.lower(): col for col in df.columns}
        
        rename_map = {}
        for original, target in col_map.items():
            original_lower = original.lower()
            if original_lower in df_cols_lower:
                actual_col = df_cols_lower[original_lower]
                rename_map[actual_col] = target
        
        df = df.rename(columns=rename_map)
        
        logger.debug(f"Columnas renombradas: {len(rename_map)}")
        
        return df
    
    @staticmethod
    def _validate_line_classification(df: pd.DataFrame) -> None:
        """
        Valida que la clasificación de líneas sea correcta.
        
        - Móviles deben iniciar con 3
        - Fijos deben iniciar con 6 (si tienen 10 dígitos)
        """
        if 'telefono_limpio' not in df.columns or 'tipo_linea' not in df.columns:
            return
        
        # Validar móviles
        moviles = df[df['tipo_linea'] == 'MOVIL'].copy()
        if len(moviles) > 0:
            moviles_incorrectos = moviles[
                ~moviles['telefono_limpio'].str.startswith('3', na=False)
            ]
            
            if len(moviles_incorrectos) > 0:
                logger.error(
                    f"❌ {len(moviles_incorrectos)} números clasificados como MÓVIL "
                    f"pero NO inician con 3"
                )
                logger.error(f"   Ejemplos: {moviles_incorrectos['telefono_limpio'].head(3).tolist()}")
        
        # Validar fijos de 10 dígitos
        fijos_10 = df[
            (df['tipo_linea'] == 'FIJA') & 
            (df['telefono_limpio'].str.len() == 10)
        ].copy()
        
        if len(fijos_10) > 0:
            fijos_incorrectos = fijos_10[
                ~fijos_10['telefono_limpio'].str.startswith('6', na=False)
            ]
            
            if len(fijos_incorrectos) > 0:
                logger.warning(
                    f"⚠️ {len(fijos_incorrectos)} números FIJOS de 10 dígitos "
                    f"que NO inician con 6"
                )
                logger.warning(f"   Ejemplos: {fijos_incorrectos['telefono_limpio'].head(3).tolist()}")


class DigitalProcessor:
    """Procesador para datos de Ventas Digitales."""
    
    @staticmethod
    @timing
    @log_execution
    def process(
        df: pd.DataFrame,
        col_map: Dict[str, str],
        start_date: date,
        end_date: date
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Procesa el reporte de Ventas Digitales.
        
        Returns:
            (df_processed, metrics)
        """
        logger.info("=" * 80)
        logger.info("🔄 PROCESANDO VENTAS DIGITALES")
        logger.info("=" * 80)
        
        # 1. Renombrar columnas
        df = TipificadorProcessor._rename_columns(df, col_map)
        
        # 2. Validar columnas requeridas
        required_cols = ['telefono_servicio', 'fecha_venta']
        validate_columns(df, required_cols, "Digital")
        
        # 3. Extraer componentes de fecha y hora
        logger.info("📅 Extrayendo fecha y hora...")
        datetime_components = df['fecha_venta'].apply(extract_datetime_components)
        
        df['fecha_alta'] = datetime_components.apply(lambda x: x['fecha_alta'])
        df['hora_venta'] = datetime_components.apply(lambda x: x['hora_venta'])
        df['fecha_venta'] = datetime_components.apply(lambda x: x['fecha_date'])
        df['hora_24h'] = datetime_components.apply(lambda x: x['hora_24h'])
        
        # 4. Limpiar teléfonos
        logger.info("📞 Limpiando números telefónicos...")
        cleaned_phones, phone_metadata = PhoneNumberValidator.clean_series(
            df['telefono_servicio'],
            return_metadata=True
        )
        
        df['telefono_limpio'] = cleaned_phones
        df['tipo_linea'] = phone_metadata['tipo_linea']
        
        # 5. Determinar código de servicio (versión digital)
        logger.info("🏷️  Asignando códigos de servicio (digital)...")
        
        # Para digital, usar el plan_desc o un default
        if 'plan_desc' in df.columns:
            service_info = df['plan_desc'].apply(
                lambda x: get_service_code(x, es_digital=True)
            )
        else:
            # Default para digital
            service_info = pd.Series([('4045', 'Mascotas')] * len(df))
        
        df['cod_servicio'] = service_info.apply(lambda x: x[0])
        df['programa'] = service_info.apply(lambda x: x[1])
        
        # 6. Eliminar inválidos
        df_valid = df[
            df['telefono_limpio'].notna() & 
            df['fecha_venta'].notna()
        ].copy()
        
        removed_count = len(df) - len(df_valid)
        if removed_count > 0:
            logger.warning(f"⚠️ Eliminados {removed_count:,} registros inválidos")
        
        # 7. Filtrar por fechas
        df_valid = filter_by_date_range(
            df_valid, 'fecha_venta', start_date, end_date
        )
        
        # 8. Detectar duplicados
        subset_cols = ['telefono_limpio']
        if 'cod_plan' in df_valid.columns:
            subset_cols.append('cod_plan')
        
        df_valid = find_duplicates(df_valid, subset_cols=subset_cols)
        
        # 9. Detectar empaquetados
        if 'cod_plan' in df_valid.columns:
            df_valid = find_empaquetados(
                df_valid,
                phone_col='telefono_limpio',
                plan_col='cod_plan'
            )
        
        # 10. Agregar tipo de venta
        df_valid['tipo_venta'] = 'DIGITAL'
        
        # 11. Agregar asesor de venta
        df_valid['nombre_asesor'] = 'Digital'
        
        # 12. Métricas
        metrics = {
            'digital': generate_summary_stats(df_valid, "Ventas Digitales"),
            'periodo': f"{start_date} - {end_date}",
            'duplicados': (df_valid['duplicate_status'] == 'duplicado').sum(),
        }
        
        # Estadísticas por tipo de línea
        phone_stats = phone_metadata.groupby('tipo_linea').size().to_dict()
        metrics['distribucion_tipo_linea'] = phone_stats
        
        logger.info("=" * 80)
        logger.info("✅ PROCESAMIENTO DE VENTAS DIGITALES COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"   📊 Total registros: {len(df_valid):,}")
        logger.info(f"   ❌ Duplicados: {metrics['duplicados']:,}")
        logger.info(f"   📱 Móviles: {phone_stats.get('MOVIL', 0):,}")
        logger.info("=" * 80)
        
        return df_valid, metrics


class HistoricalSalesProcessor:
    """Procesador para ventas históricas."""
    
    @staticmethod
    @timing
    @log_execution
    def process(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Procesa ventas históricas (ya deberían estar limpias).
        
        Returns:
            (df_processed, metrics)
        """
        logger.info("=" * 80)
        logger.info("🔄 PROCESANDO VENTAS HISTÓRICAS")
        logger.info("=" * 80)
        
        if df.empty:
            logger.warning("⚠️ No hay ventas históricas para procesar")
            return df, {'historicos': {'total_registros': 0}}
        
        # Validación básica
        if 'telefono_servicio' not in df.columns:
            logger.warning(
                "⚠️ Columna 'telefono_servicio' no encontrada. "
                "Buscando alternativas..."
            )
            
            # Buscar columnas alternativas
            phone_cols = [col for col in df.columns if 'telefono' in col.lower() or 'tel' in col.lower()]
            
            if phone_cols:
                df = df.rename(columns={phone_cols[0]: 'telefono_servicio'})
                logger.info(f"✅ Usando columna '{phone_cols[0]}' como telefono_servicio")
            else:
                logger.error("❌ No se encontró columna de teléfono en históricos")
                return df, {'historicos': {'error': 'Sin columna de teléfono'}}
        
        # Estandarizar formato
        if 'telefono_servicio' in df.columns:
            logger.info("📞 Validando teléfonos históricos...")
            
            # Limpiar teléfonos si no están ya limpios
            if 'telefono_limpio' not in df.columns:
                df['telefono_limpio'] = PhoneNumberValidator.clean_series(
                    df['telefono_servicio']
                )
        
        # Validar columna de tipo de línea
        if 'tipo_linea' not in df.columns and 'telefono_limpio' in df.columns:
            logger.info("🏷️  Clasificando tipo de línea...")
            df['tipo_linea'] = df['telefono_limpio'].apply(
                lambda x: PhoneNumberValidator._classify_type(str(x))[0] if pd.notna(x) else 'INVALIDO'
            )
        
        # Estandarizar columnas de fecha
        date_cols = [col for col in df.columns if 'fecha' in col.lower()]
        if date_cols and 'fecha_venta' not in df.columns:
            df = df.rename(columns={date_cols[0]: 'fecha_venta'})
            logger.info(f"✅ Usando columna '{date_cols[0]}' como fecha_venta")
        
        # Generar métricas
        metrics = {
            'historicos': generate_summary_stats(df, "Ventas Históricas"),
            'archivos_fuente': df['_archivo_origen'].nunique() if '_archivo_origen' in df.columns else 0,
        }
        
        # Estadísticas por tipo de línea
        if 'tipo_linea' in df.columns:
            tipo_stats = df['tipo_linea'].value_counts().to_dict()
            metrics['distribucion_tipo_linea'] = tipo_stats
        
        logger.info("=" * 80)
        logger.info("✅ PROCESAMIENTO DE HISTÓRICOS COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"   📊 Total registros: {len(df):,}")
        if 'tipo_linea' in df.columns:
            logger.info(f"   📱 Móviles: {tipo_stats.get('MOVIL', 0):,}")
            logger.info(f"   ☎️  Fijos: {tipo_stats.get('FIJA', 0):,}")
        logger.info("=" * 80)
        
        return df, metrics


def consolidate_monthly_report(
    df_tipificador: pd.DataFrame,
    df_digital: pd.DataFrame,
    df_historical: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Consolida todas las ventas del mes con históricas.
    
    Returns:
        (df_consolidated, metrics)
    """
    logger.info("=" * 80)
    logger.info("🔄 CONSOLIDANDO REPORTE MENSUAL")
    logger.info("=" * 80)
    
    # 1. Seleccionar solo ventas originales (no duplicadas)
    df_tip_original = df_tipificador[
        df_tipificador['duplicate_status'] == 'original'
    ].copy()
    
    df_dig_original = df_digital[
        df_digital['duplicate_status'] == 'original'
    ].copy()
    
    logger.info(
        f"📊 Ventas del mes actual: {len(df_tip_original):,} tipificador + "
        f"{len(df_dig_original):,} digital"
    )
    
    # 2. Estandarizar columnas para concatenación
    common_cols = [
        'telefono_limpio', 'tipo_venta', 'fecha_venta',
        'nombre_cliente', 'nombre_asesor', 'tipo_linea',
        'fecha_alta', 'hora_venta', 'cod_servicio', 'programa'
    ]
    
    def safe_select_columns(df: pd.DataFrame, cols: list) -> pd.DataFrame:
        """Selecciona columnas que existen."""
        available_cols = [col for col in cols if col in df.columns]
        return df[available_cols].copy()
    
    df_tip_clean = safe_select_columns(df_tip_original, common_cols)
    df_dig_clean = safe_select_columns(df_dig_original, common_cols)
    df_hist_clean = safe_select_columns(df_historical, common_cols)
    
    # 3. Agregar etiqueta de origen
    df_tip_clean['origen'] = 'MES_ACTUAL_TIPIFICADOR'
    df_dig_clean['origen'] = 'MES_ACTUAL_DIGITAL'
    df_hist_clean['origen'] = 'HISTORICO'
    
    # 4. Concatenar todo
    df_consolidated = pd.concat(
        [df_hist_clean, df_tip_clean, df_dig_clean],
        ignore_index=True
    )
    
    logger.info(f"📊 Total pre-deduplicación: {len(df_consolidated):,} registros")
    
    # 5. Eliminar duplicados finales (priorizar históricos)
    df_consolidated = df_consolidated.sort_values(
        'origen',
        key=lambda x: x.map({
            'HISTORICO': 0, 
            'MES_ACTUAL_TIPIFICADOR': 1, 
            'MES_ACTUAL_DIGITAL': 2
        })
    )
    
    # Detectar duplicados finales
    df_consolidated = find_duplicates(
        df_consolidated,
        subset_cols=['telefono_limpio', 'tipo_venta']
    )
    
    # Mantener solo originales
    df_final = df_consolidated[
        df_consolidated['duplicate_status'] == 'original'
    ].copy()
    
    duplicates_removed = len(df_consolidated) - len(df_final)
    
    logger.info(f"🗑️  Duplicados eliminados en consolidación: {duplicates_removed:,}")
    logger.info(f"✅ Total final: {len(df_final):,} ventas únicas")
    
    # 6. Métricas
    metrics = {
        'total_consolidado': len(df_final),
        'del_mes_actual': len(df_tip_clean) + len(df_dig_clean),
        'historicos': len(df_hist_clean),
        'duplicados_eliminados': duplicates_removed,
        'distribucion_origen': df_final['origen'].value_counts().to_dict(),
    }
    
    # Estadísticas por tipo de línea
    if 'tipo_linea' in df_final.columns:
        tipo_stats = df_final['tipo_linea'].value_counts().to_dict()
        metrics['distribucion_tipo_linea'] = tipo_stats
        
        logger.info(f"   📱 Móviles: {tipo_stats.get('MOVIL', 0):,}")
        logger.info(f"   ☎️  Fijos: {tipo_stats.get('FIJA', 0):,}")
    
    logger.info("=" * 80)
    logger.info("✅ CONSOLIDACIÓN COMPLETADA")
    logger.info("=" * 80)
    
    return df_final, metrics