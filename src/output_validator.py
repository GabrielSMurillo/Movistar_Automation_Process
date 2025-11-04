# src/output_validator.py
"""
Validador de archivos de salida generados.
Asegura que cumplan con especificaciones exactas.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict
import logging

logger = logging.getLogger(__name__)


class OutputFileValidator:
    """Valida que los archivos generados cumplan especificaciones."""
    
    # Columnas requeridas por tipo de archivo
    REQUIRED_COLUMNS = {
        'contact_log': [
            'Linea',
        ],
        'formato_movistar': [
            'FECHA_ALTA', 'HORA_VENTA', 'NUM_CELULAR', 
            'COD_SERVICIO', 'PROGRAMA'
        ],
        'svas': [
            'Num_Celular', 'cod_plantarif', 'Codigo_Bono', 
            'Cod_ciclo', 'EMPLEADO'
        ],
        'formato_digital': [
            'FECHA_ALTA', 'HORA_VENTA', 'NUM_CELULAR',
            'ASESOR_VENTA', 'COD_SERVICIO'
        ]
    }
    
    @classmethod
    def validate_file(
        cls, 
        file_path: Path, 
        file_type: str
    ) -> Tuple[bool, List[str]]:
        """
        Valida un archivo generado.
        
        Args:
            file_path: Ruta al archivo
            file_type: Tipo de archivo (contact_log, formato_movistar, etc)
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Verificar que exista
        if not file_path.exists():
            return False, [f"❌ Archivo no existe: {file_path.name}"]
        
        # 2. Leer archivo
        try:
            df = pd.read_excel(file_path, sheet_name=0)
        except Exception as e:
            return False, [f"❌ Error leyendo archivo: {e}"]
        
        # 3. Verificar que no esté vacío
        if df.empty:
            errors.append("⚠️ Archivo está vacío")
        
        # 4. Verificar columnas requeridas
        if file_type in cls.REQUIRED_COLUMNS:
            required = cls.REQUIRED_COLUMNS[file_type]
            missing = []
            
            for col in required:
                # Buscar columna de forma flexible (puede tener texto adicional)
                found = any(col.lower() in str(c).lower() for c in df.columns)
                if not found:
                    missing.append(col)
            
            if missing:
                errors.append(f"⚠️ Faltan columnas: {missing}")
        
        # 5. Validaciones específicas por tipo
        if file_type == 'contact_log':
            cls._validate_contact_log(df, errors)
        
        if file_type in ['formato_movistar', 'formato_digital', 'svas']:
            cls._validate_phone_numbers(df, errors)
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def _validate_contact_log(df: pd.DataFrame, errors: List[str]) -> None:
        """Validaciones específicas para Contact Log."""
        if 'Linea' in df.columns:
            # Verificar que Linea sea numérica
            if not pd.api.types.is_numeric_dtype(df['Linea']):
                errors.append("⚠️ Columna 'Linea' no es numérica")
            
            # Verificar que sea secuencial
            if not df['Linea'].is_monotonic_increasing:
                errors.append("⚠️ Columna 'Linea' no es secuencial")
    
    @staticmethod
    def _validate_phone_numbers(df: pd.DataFrame, errors: List[str]) -> None:
        """Validaciones de números telefónicos."""
        phone_cols = ['NUM_CELULAR', 'Num_Celular']
        
        for col in phone_cols:
            if col in df.columns:
                # Verificar longitud
                invalid_phones = df[col].apply(
                    lambda x: len(str(x)) not in {7, 10} if pd.notna(x) else False
                )
                
                if invalid_phones.any():
                    count = invalid_phones.sum()
                    errors.append(
                        f"⚠️ {count} teléfonos con longitud inválida en '{col}'"
                    )
                
                # Verificar que sean numéricos
                non_numeric = df[col].apply(
                    lambda x: not str(x).isdigit() if pd.notna(x) else False
                )
                
                if non_numeric.any():
                    count = non_numeric.sum()
                    errors.append(
                        f"⚠️ {count} teléfonos no numéricos en '{col}'"
                    )
    
    @classmethod
    def validate_all_outputs(
        cls, 
        output_dir: Path, 
        output_files: Dict[str, str]
    ) -> Dict[str, Dict]:
        """
        Valida todos los archivos de salida.
        
        Args:
            output_dir: Directorio de salida
            output_files: Diccionario con nombres de archivos
        
        Returns:
            Diccionario con resultados de validación
        """
        logger.info("=" * 80)
        logger.info("🔍 VALIDANDO ARCHIVOS DE SALIDA")
        logger.info("=" * 80)
        
        validation_results = {}
        
        # Mapeo de keys a tipos de archivo
        file_type_mapping = {
            'movistar_contact_log': 'contact_log',
            'movistar_general': 'formato_movistar',
            'movistar_svas_dig': 'svas',
            'movistar_svas_fija': 'svas',
            'movistar_svas_mov': 'svas',
            'internal_digital': 'formato_digital',
            'internal_fija': 'formato_digital',
            'internal_movil': 'formato_digital',
        }
        
        for key, filename in output_files.items():
            if key not in file_type_mapping:
                continue
            
            file_path = output_dir / filename
            file_type = file_type_mapping[key]
            
            is_valid, errors = cls.validate_file(file_path, file_type)
            
            validation_results[filename] = {
                'valid': is_valid,
                'errors': errors,
                'file_type': file_type
            }
            
            if is_valid:
                logger.info(f"✅ {filename}")
            else:
                logger.error(f"❌ {filename}")
                for error in errors:
                    logger.error(f"   {error}")
        
        # Resumen
        total = len(validation_results)
        valid = sum(1 for r in validation_results.values() if r['valid'])
        invalid = total - valid
        
        logger.info("=" * 80)
        logger.info(f"📊 Resumen de Validación:")
        logger.info(f"   Total archivos: {total}")
        logger.info(f"   ✅ Válidos: {valid}")
        logger.info(f"   ❌ Inválidos: {invalid}")
        logger.info("=" * 80)
        
        return validation_results