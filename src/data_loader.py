# src/data_loader.py
"""
Módulo de carga de datos optimizado para CSVs de Google Sheets.
Ahora soporta CSV y Excel mediante InputAdapters.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List
import logging

from config import CSV_READ_CONFIG
from src.validators import DataQualityValidator
from src.adapters import InputAdapterFactory, read_file

# Importar decorators del nuevo sistema
try:
    from src.core.decorators import retry, timing, log_execution
    from src.core.exceptions import FileNotFoundError as CustomFileNotFoundError
    DECORATORS_AVAILABLE = True
except ImportError:
    # Fallback si no están disponibles
    DECORATORS_AVAILABLE = False
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def timing(func):
        return func
    def log_execution(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


class CSVLoader:
    """Cargador optimizado para CSVs de Google Sheets."""
    
    @staticmethod
    @retry(max_attempts=3, delay=1.0)
    @timing
    def load_csv(
        file_path: Path,
        skiprows: int = 0,
        custom_config: Optional[dict] = None
    ) -> pd.DataFrame:
        """
        Carga un archivo CSV con configuración optimizada para Google Sheets.
        
        Incluye retry automático y medición de performance.
        
        Args:
            file_path: Ruta al archivo CSV
            skiprows: Número de filas a saltar al inicio
            custom_config: Configuración personalizada (sobrescribe CSV_READ_CONFIG)
        
        Returns:
            DataFrame con los datos cargados
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            pd.errors.ParserError: Si hay errores de parsing
        """
        if not file_path.exists():
            raise FileNotFoundError(
                f"Archivo no encontrado: {file_path}\n"
                f"Asegúrate de exportar el archivo desde Google Sheets como CSV"
            )
        
        # Combinar configuración
        config = {**CSV_READ_CONFIG}
        if custom_config:
            config.update(custom_config)
        
        if skiprows > 0:
            config['skiprows'] = skiprows
        
        logger.info(f"📥 Cargando CSV: {file_path.name}")
        logger.debug(f"Configuración de lectura: {config}")
        
        try:
            df = pd.read_csv(file_path, **config)
            
            # Limpieza automática
            df = CSVLoader._clean_dataframe(df)
            
            logger.info(
                f"✅ Archivo cargado: {len(df):,} filas, {len(df.columns)} columnas"
            )
            
            # Validación básica
            is_valid, message = DataQualityValidator.validate_dataframe(
                df, file_path.name
            )
            
            if not is_valid:
                logger.error(f"⚠️ Problemas de calidad: {message}")
            
            return df
        
        except pd.errors.ParserError as e:
            logger.error(
                f"❌ Error parseando CSV '{file_path.name}': {e}\n"
                f"Verifica que el archivo esté correctamente exportado desde Sheets"
            )
            raise
        
        except Exception as e:
            logger.error(f"❌ Error inesperado cargando '{file_path.name}': {e}")
            raise
    
    @staticmethod
    def _clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Limpieza automática de datos comunes en CSVs de Sheets."""
        
        # 1. Eliminar columnas completamente vacías
        df = df.dropna(axis=1, how='all')
        
        # 2. Eliminar filas completamente vacías
        df = df.dropna(axis=0, how='all')
        
        # 3. Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # 4. Resetear índice
        df = df.reset_index(drop=True)
        
        # 5. Eliminar espacios en blanco de strings
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )
        
        return df
    
    @staticmethod
    @timing
    def load_and_concatenate_csvs(
        directory: Path,
        pattern: str = "*.csv"
    ) -> pd.DataFrame:
        """
        Carga múltiples CSVs de un directorio y los concatena.
        
        Con medición de performance automática.
        
        Args:
            directory: Directorio con los archivos
            pattern: Patrón de nombre de archivos (glob pattern)
        
        Returns:
            DataFrame concatenado
        """
        if not directory.exists():
            logger.warning(f"Directorio no existe: {directory}")
            return pd.DataFrame()
        
        matching_files = sorted(directory.glob(pattern))
        
        if not matching_files:
            logger.warning(
                f"No se encontraron archivos con patrón '{pattern}' en {directory}"
            )
            return pd.DataFrame()
        
        logger.info(f"📂 Encontrados {len(matching_files)} archivos CSV para concatenar")
        
        df_list: List[pd.DataFrame] = []
        
        for file_path in matching_files:
            try:
                df = CSVLoader.load_csv(file_path)
                
                # Agregar columna de origen
                df['_archivo_origen'] = file_path.name
                
                df_list.append(df)
                
            except Exception as e:
                logger.error(f"⚠️ Error cargando '{file_path.name}': {e}. Omitiendo.")
                continue
        
        if not df_list:
            logger.error("❌ No se pudo cargar ningún archivo correctamente")
            return pd.DataFrame()
        
        # Concatenar
        result = pd.concat(df_list, ignore_index=True)
        
        logger.info(
            f"✅ Concatenados {len(df_list)} archivos: "
            f"{len(result):,} registros totales"
        )
        
        return result


def load_tipificador(config: dict) -> pd.DataFrame:
    """
    Helper para cargar el tipificador.
    Ahora soporta CSV y Excel automáticamente.
    """
    file_path = Path(config['file_path'])
    skiprows = config.get('skiprows', 0)
    
    # Si es CSV, usar el método tradicional
    if file_path.suffix.lower() == '.csv':
        return CSVLoader.load_csv(file_path, skiprows=skiprows)
    
    # Si es Excel, usar InputAdapter
    logger.info(f"📥 Cargando Tipificador (Excel): {file_path.name}")
    adapter = InputAdapterFactory.create(file_path, skiprows=skiprows)
    df = adapter.read()
    df = CSVLoader._clean_dataframe(df)
    logger.info(f"✅ Archivo cargado: {len(df):,} filas, {len(df.columns)} columnas")
    return df


def load_digital(config: dict) -> pd.DataFrame:
    """
    Helper para cargar ventas digitales.
    Ahora soporta CSV y Excel automáticamente.
    """
    file_path = Path(config['file_path'])
    skiprows = config.get('skiprows', 0)
    
    # Si es CSV, usar el método tradicional
    if file_path.suffix.lower() == '.csv':
        return CSVLoader.load_csv(file_path, skiprows=skiprows)
    
    # Si es Excel, usar InputAdapter
    logger.info(f"📥 Cargando Digital (Excel): {file_path.name}")
    adapter = InputAdapterFactory.create(file_path, skiprows=skiprows)
    df = adapter.read()
    df = CSVLoader._clean_dataframe(df)
    logger.info(f"✅ Archivo cargado: {len(df):,} filas, {len(df.columns)} columnas")
    return df


def load_historical_sales(config: dict) -> pd.DataFrame:
    """Helper para cargar ventas históricas."""
    directory = config['dir']
    pattern = config.get('pattern', '*.csv')
    return CSVLoader.load_and_concatenate_csvs(directory, pattern)