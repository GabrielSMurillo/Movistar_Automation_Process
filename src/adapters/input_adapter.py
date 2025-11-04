"""
Input Adapters para manejar diferentes formatos de archivo.

Este módulo implementa el patrón Adapter para permitir que el sistema
procese tanto archivos CSV como Excel (.xlsx) de manera transparente.

Arquitectura:
- InputAdapter (ABC): Interfaz base
- CSVAdapter: Implementación para archivos CSV
- ExcelAdapter: Implementación para archivos Excel
- InputAdapterFactory: Factory para crear el adapter apropiado

Ejemplo:
    >>> from src.adapters.input_adapter import InputAdapterFactory
    >>> adapter = InputAdapterFactory.create("datos.csv")
    >>> df = adapter.read()
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class InputAdapter(ABC):
    """
    Interfaz base para adaptadores de entrada.
    
    Define el contrato que todos los adaptadores deben implementar.
    """
    
    def __init__(self, file_path: Path, **kwargs):
        """
        Inicializa el adapter.
        
        Args:
            file_path: Ruta al archivo a leer
            **kwargs: Argumentos adicionales específicos del adapter
        """
        self.file_path = Path(file_path)
        self.kwargs = kwargs
        self._validate_file()
    
    def _validate_file(self) -> None:
        """Valida que el archivo exista y sea accesible."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.file_path}")
        
        if not self.file_path.is_file():
            raise ValueError(f"La ruta no es un archivo: {self.file_path}")
    
    @abstractmethod
    def read(self) -> pd.DataFrame:
        """
        Lee el archivo y retorna un DataFrame.
        
        Returns:
            DataFrame con los datos del archivo
            
        Raises:
            IOError: Si hay error al leer el archivo
        """
        pass
    
    @abstractmethod
    def get_file_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre el archivo.
        
        Returns:
            Diccionario con metadatos del archivo
        """
        pass
    
    def __repr__(self) -> str:
        """Representación en string del adapter."""
        return f"{self.__class__.__name__}(file_path='{self.file_path}')"


class CSVAdapter(InputAdapter):
    """
    Adapter para archivos CSV.
    
    Soporta opciones comunes de pandas.read_csv:
    - encoding
    - sep (delimiter)
    - skiprows
    - usecols
    - etc.
    """
    
    def __init__(
        self,
        file_path: Path,
        encoding: str = 'utf-8',
        sep: str = ',',
        **kwargs
    ):
        """
        Inicializa el CSV adapter.
        
        Args:
            file_path: Ruta al archivo CSV
            encoding: Codificación del archivo (default: utf-8)
            sep: Separador de columnas (default: ,)
            **kwargs: Argumentos adicionales para pandas.read_csv
        """
        self.encoding = encoding
        self.sep = sep
        super().__init__(file_path, **kwargs)
    
    def read(self) -> pd.DataFrame:
        """
        Lee el archivo CSV.
        
        Returns:
            DataFrame con los datos del CSV
            
        Raises:
            IOError: Si hay error al leer el archivo
        """
        try:
            logger.debug(f"📄 Leyendo CSV: {self.file_path.name}")
            logger.debug(f"   Encoding: {self.encoding}, Separador: '{self.sep}'")
            
            df = pd.read_csv(
                self.file_path,
                encoding=self.encoding,
                sep=self.sep,
                **self.kwargs
            )
            
            logger.debug(f"   ✓ Leídas {len(df):,} filas, {len(df.columns)} columnas")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error leyendo CSV {self.file_path.name}: {e}")
            raise IOError(f"Error al leer CSV: {e}") from e
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre el archivo CSV.
        
        Returns:
            Diccionario con metadatos
        """
        stat = self.file_path.stat()
        
        return {
            'type': 'CSV',
            'path': str(self.file_path),
            'name': self.file_path.name,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': pd.Timestamp.fromtimestamp(stat.st_mtime),
            'encoding': self.encoding,
            'separator': self.sep,
        }


class ExcelAdapter(InputAdapter):
    """
    Adapter para archivos Excel (.xlsx, .xls).
    
    Soporta opciones comunes de pandas.read_excel:
    - sheet_name
    - skiprows
    - usecols
    - header
    - etc.
    """
    
    def __init__(
        self,
        file_path: Path,
        sheet_name: str | int = 0,
        **kwargs
    ):
        """
        Inicializa el Excel adapter.
        
        Args:
            file_path: Ruta al archivo Excel
            sheet_name: Nombre o índice de la hoja a leer (default: 0 = primera hoja)
            **kwargs: Argumentos adicionales para pandas.read_excel
        """
        self.sheet_name = sheet_name
        super().__init__(file_path, **kwargs)
        
        # Validar extensión
        if self.file_path.suffix.lower() not in ['.xlsx', '.xls', '.xlsm']:
            raise ValueError(
                f"Extensión inválida: {self.file_path.suffix}. "
                f"Se esperaba .xlsx, .xls o .xlsm"
            )
    
    def read(self) -> pd.DataFrame:
        """
        Lee el archivo Excel.
        
        Returns:
            DataFrame con los datos del Excel
            
        Raises:
            IOError: Si hay error al leer el archivo
        """
        try:
            logger.debug(f"📊 Leyendo Excel: {self.file_path.name}")
            logger.debug(f"   Hoja: {self.sheet_name}")
            
            df = pd.read_excel(
                self.file_path,
                sheet_name=self.sheet_name,
                **self.kwargs
            )
            
            logger.debug(f"   ✓ Leídas {len(df):,} filas, {len(df.columns)} columnas")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error leyendo Excel {self.file_path.name}: {e}")
            raise IOError(f"Error al leer Excel: {e}") from e
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre el archivo Excel.
        
        Returns:
            Diccionario con metadatos
        """
        stat = self.file_path.stat()
        
        # Obtener lista de hojas
        try:
            xl_file = pd.ExcelFile(self.file_path)
            sheet_names = xl_file.sheet_names
        except Exception:
            sheet_names = ['N/A']
        
        return {
            'type': 'Excel',
            'path': str(self.file_path),
            'name': self.file_path.name,
            'size_bytes': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': pd.Timestamp.fromtimestamp(stat.st_mtime),
            'sheet_name': self.sheet_name,
            'available_sheets': sheet_names,
        }
    
    def list_sheets(self) -> list[str]:
        """
        Lista todas las hojas disponibles en el archivo.
        
        Returns:
            Lista de nombres de hojas
        """
        try:
            xl_file = pd.ExcelFile(self.file_path)
            return xl_file.sheet_names
        except Exception as e:
            logger.error(f"❌ Error listando hojas: {e}")
            return []


class InputAdapterFactory:
    """
    Factory para crear adaptadores de entrada según el tipo de archivo.
    
    Determina automáticamente el adapter apropiado basándose en la
    extensión del archivo.
    """
    
    @staticmethod
    def create(
        file_path: str | Path,
        **kwargs
    ) -> InputAdapter:
        """
        Crea el adapter apropiado para el tipo de archivo.
        
        Args:
            file_path: Ruta al archivo
            **kwargs: Argumentos adicionales para el adapter
            
        Returns:
            InputAdapter apropiado (CSVAdapter o ExcelAdapter)
            
        Raises:
            ValueError: Si la extensión del archivo no es soportada
            FileNotFoundError: Si el archivo no existe
            
        Ejemplo:
            >>> adapter = InputAdapterFactory.create("datos.csv")
            >>> df = adapter.read()
        """
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        logger.debug(f"🏭 Factory: Detectando adapter para {file_path.name}")
        logger.debug(f"   Extensión: {extension}")
        
        # Determinar adapter según extensión
        if extension == '.csv':
            logger.debug("   ✓ Seleccionado: CSVAdapter")
            return CSVAdapter(file_path, **kwargs)
        
        elif extension in ['.xlsx', '.xls', '.xlsm']:
            logger.debug("   ✓ Seleccionado: ExcelAdapter")
            return ExcelAdapter(file_path, **kwargs)
        
        else:
            raise ValueError(
                f"Extensión no soportada: {extension}\n"
                f"Extensiones válidas: .csv, .xlsx, .xls, .xlsm"
            )
    
    @staticmethod
    def supported_extensions() -> list[str]:
        """
        Retorna lista de extensiones soportadas.
        
        Returns:
            Lista de extensiones (ej: ['.csv', '.xlsx', '.xls'])
        """
        return ['.csv', '.xlsx', '.xls', '.xlsm']
    
    @staticmethod
    def is_supported(file_path: str | Path) -> bool:
        """
        Verifica si la extensión del archivo es soportada.
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            True si es soportado, False en caso contrario
        """
        extension = Path(file_path).suffix.lower()
        return extension in InputAdapterFactory.supported_extensions()


# Funciones de conveniencia
def read_file(file_path: str | Path, **kwargs) -> pd.DataFrame:
    """
    Función de conveniencia para leer cualquier archivo soportado.
    
    Args:
        file_path: Ruta al archivo
        **kwargs: Argumentos adicionales para el adapter
        
    Returns:
        DataFrame con los datos del archivo
        
    Ejemplo:
        >>> df = read_file("datos.csv", encoding='latin-1')
        >>> df = read_file("reporte.xlsx", sheet_name="Ventas")
    """
    adapter = InputAdapterFactory.create(file_path, **kwargs)
    return adapter.read()


def get_file_info(file_path: str | Path) -> Dict[str, Any]:
    """
    Obtiene información sobre un archivo.
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Diccionario con metadatos del archivo
    """
    adapter = InputAdapterFactory.create(file_path)
    return adapter.get_file_info()
