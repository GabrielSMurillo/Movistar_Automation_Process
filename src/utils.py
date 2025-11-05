# src/utils.py
"""
Utilidades mejoradas con extracción de hora y más funciones.
"""

import pandas as pd
from datetime import date
from typing import List, Optional, Tuple, Dict
import logging

from config import DUPLICATE_STATUS_ORIGINAL, DUPLICATE_STATUS_DUPLICATE

logger = logging.getLogger(__name__)

def extract_datetime_components(timestamp: str | pd.Timestamp) -> Dict[str, str]:
 """
 Extrae componentes de fecha y hora desde marca temporal.
 
 Args:
 timestamp: String o Timestamp con fecha y hora
 
 Returns:
 Dict con componentes extraídos
 
 Example:
 >>> extract_datetime_components("10/23/2025 10:25:00")
 {
 'fecha_alta': '23/10/2025',
 'hora_venta': '10:25:00 AM',
 'fecha_iso': '2025-10-23',
 'hora_24h': '10:25:00'
 }
 """
 try:
 if pd.isna(timestamp):
 return {
 'fecha_alta': '',
 'hora_venta': '',
 'fecha_iso': '',
 'hora_24h': '',
 'fecha_date': None
 }
 
 dt = pd.to_datetime(timestamp)
 
 return {
 'fecha_alta': dt.strftime('%d/%m/%Y'), # DD/MM/YYYY
 'hora_venta': dt.strftime('%I:%M:%S %p'), # 12h con AM/PM
 'fecha_iso': dt.strftime('%Y-%m-%d'), # ISO format
 'hora_24h': dt.strftime('%H:%M:%S'), # 24h format
 'fecha_date': dt.date()
 }
 except Exception as e:
 logger.warning(f"Error extrayendo componentes de '{timestamp}': {e}")
 return {
 'fecha_alta': '',
 'hora_venta': '',
 'fecha_iso': '',
 'hora_24h': '',
 'fecha_date': None
 }

def standardize_date(
 date_series: pd.Series,
 dayfirst: bool = True
) -> pd.Series:
 """
 Convierte una serie a datetime.date, manejando múltiples formatos.
 
 Args:
 date_series: Serie con fechas en diferentes formatos
 dayfirst: Si True, interpreta 01/02/2025 como 1 de febrero
 
 Returns:
 Serie de tipo datetime.date
 """
 logger.debug(f"Estandarizando {len(date_series):,} fechas...")
 
 converted = pd.to_datetime(
 date_series,
 errors='coerce',
 dayfirst=dayfirst
 )
 
 invalid_count = converted.isna().sum()
 if invalid_count > 0:
 logger.warning(
 f"[INFO] {invalid_count:,} fechas inválidas "
 f"({invalid_count/len(date_series)*100:.1f}%)"
 )
 
 result = converted.dt.date
 
 return result

def find_duplicates(
 df: pd.DataFrame,
 subset_cols: List[str],
 keep: str = 'first'
) -> pd.DataFrame:
 """
 Identifica y marca duplicados en un DataFrame.
 
 Args:
 df: DataFrame a analizar
 subset_cols: Columnas para identificar duplicados
 keep: 'first', 'last' o False
 
 Returns:
 DataFrame con columna 'duplicate_status' agregada
 """
 df = df.copy()
 
 missing_cols = set(subset_cols) - set(df.columns)
 if missing_cols:
 raise ValueError(f"Columnas no encontradas: {missing_cols}")
 
 logger.info(f"[INFO] Buscando duplicados basados en: {subset_cols}")
 
 df['duplicate_status'] = DUPLICATE_STATUS_ORIGINAL
 duplicates_mask = df.duplicated(subset=subset_cols, keep=keep)
 df.loc[duplicates_mask, 'duplicate_status'] = DUPLICATE_STATUS_DUPLICATE
 
 duplicate_count = duplicates_mask.sum()
 if duplicate_count > 0:
 logger.warning(
 f"[INFO] Encontrados {duplicate_count:,} duplicados "
 f"({duplicate_count/len(df)*100:.1f}%)"
 )
 else:
 logger.info(f"[INFO] No se encontraron duplicados")
 
 return df

def find_empaquetados(
 df: pd.DataFrame,
 phone_col: str = 'telefono_servicio',
 plan_col: str = 'tipo_venta'
) -> pd.DataFrame:
 """
 Identifica ventas "empaquetadas" (mismo cliente, múltiples planes).
 
 Args:
 df: DataFrame con ventas
 phone_col: Nombre de la columna de teléfono
 plan_col: Nombre de la columna de plan/tipo
 
 Returns:
 DataFrame con columnas 'is_empaquetado' y 'cantidad_planes'
 """
 df = df.copy()
 
 logger.info(f"[INFO] Identificando ventas empaquetadas...")
 
 # Contar planes únicos por teléfono
 plans_per_phone = df.groupby(phone_col)[plan_col].transform('nunique')
 df['is_empaquetado'] = plans_per_phone > 1
 df['cantidad_planes'] = plans_per_phone
 
 empaquetado_count = df['is_empaquetado'].sum()
 if empaquetado_count > 0:
 logger.info(
 f"[INFO] Encontradas {empaquetado_count:,} ventas empaquetadas "
 f"({empaquetado_count/len(df)*100:.1f}%)"
 )
 
 return df

def validate_columns(
 df: pd.DataFrame,
 required_cols: List[str],
 df_name: str = "DataFrame"
) -> None:
 """
 Valida que las columnas requeridas existan en un DataFrame.
 
 Args:
 df: DataFrame a validar
 required_cols: Lista de columnas requeridas
 df_name: Nombre del DataFrame para mensajes de error
 
 Raises:
 ValueError: Si faltan columnas requeridas
 """
 missing_cols = set(required_cols) - set(df.columns)
 
 if missing_cols:
 error_msg = (
 f"[ERROR] Faltan columnas requeridas en '{df_name}':\n"
 f" Faltantes: {missing_cols}\n"
 f" Disponibles: {set(df.columns)}"
 )
 logger.error(error_msg)
 raise ValueError(error_msg)
 
 logger.debug(f"[INFO] Todas las columnas requeridas presentes en '{df_name}'")

def filter_by_date_range(
 df: pd.DataFrame,
 date_col: str,
 start_date: date,
 end_date: date
) -> pd.DataFrame:
 """
 Filtra un DataFrame por rango de fechas.
 
 Args:
 df: DataFrame a filtrar
 date_col: Nombre de la columna de fecha
 start_date: Fecha de inicio (inclusiva)
 end_date: Fecha de fin (inclusiva)
 
 Returns:
 DataFrame filtrado
 """
 df = df.copy()
 
 # Asegurar que la columna sea datetime.date
 if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
 if df[date_col].dtype == 'object':
 df[date_col] = pd.to_datetime(df[date_col]).dt.date
 
 original_count = len(df)
 
 # Filtrar
 mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
 df_filtered = df[mask]
 
 filtered_count = len(df_filtered)
 
 retention_pct = (filtered_count/original_count*100) if original_count > 0 else 0.0
 logger.info(
 f"[INFO] Filtrado por fechas [{start_date} - {end_date}]: "
 f"{original_count} {} {filtered_count} registros "
 f"({retention_pct:.1f}% retenido)"
 )
 
 return df_filtered

def detect_referidos(
 df: pd.DataFrame,
 referido_col: str = 'es_referido',
 yes_values: Optional[set] = None
) -> pd.DataFrame:
 """
 Detecta y marca ventas que provienen de referidos.
 
 Args:
 df: DataFrame con columna de referidos
 referido_col: Nombre de la columna de referidos
 yes_values: Set de valores que indican "sí es referido"
 
 Returns:
 DataFrame con columna 'is_referido' (bool) agregada
 """
 from config import REFERIDO_YES_VALUES
  
 if yes_values is None:
 yes_values = REFERIDO_YES_VALUES
 
 df = df.copy()
 
 # Normalizar valores
 df[referido_col] = df[referido_col].astype(str).str.lower().str.strip()
 
 # Marcar referidos
 df['is_referido'] = df[referido_col].isin(yes_values)
 
 referido_count = df['is_referido'].sum()
 referido_pct = (referido_count/len(df)*100) if len(df) > 0 else 0.0
 logger.info(
 f"[INFO] Identificados {referido_count} referidos "
 f"({referido_pct:.1f}%)"
 )
 
 return df

def generate_summary_stats(df: pd.DataFrame, df_name: str) -> dict:
 """
 Genera estadísticas resumidas de un DataFrame.
 
 Args:
 df: DataFrame a analizar
 df_name: Nombre descriptivo
 
 Returns:
 Diccionario con estadísticas
 """
 stats = {
 'nombre': df_name,
 'total_registros': len(df),
 'total_columnas': len(df.columns),
 'memoria_mb': df.memory_usage(deep=True).sum() / 1024**2,
 'registros_duplicados': df.duplicated().sum(),
 'columnas_con_nulos': df.isnull().any().sum(),
 'tasa_nulos_promedio': df.isnull().mean().mean(),
 }
 
 # Agregar stats por columna clave
 if 'telefono_servicio' in df.columns or 'telefono_limpio' in df.columns:
 phone_col = 'telefono_limpio' if 'telefono_limpio' in df.columns else 'telefono_servicio'
 stats['telefonos_unicos'] = df[phone_col].nunique()
 
 if 'nombre_asesor' in df.columns:
 stats['asesores_unicos'] = df['nombre_asesor'].nunique()
 
 if 'tipo_venta' in df.columns:
 stats['tipos_venta'] = df['tipo_venta'].value_counts().to_dict()
 
 if 'tipo_linea' in df.columns:
 stats['distribucion_tipo_linea'] = df['tipo_linea'].value_counts().to_dict()
 
 return stats