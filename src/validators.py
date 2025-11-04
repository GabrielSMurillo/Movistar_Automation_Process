# src/validators.py
"""
Validadores mejorados con soporte completo para fijos y móviles.
"""

from typing import Optional, Tuple
import phonenumbers
from phonenumbers import NumberParseException
import pandas as pd
import logging
from dataclasses import dataclass

from config import MOBILE_PREFIXES, FIXED_LINE_CODES, DATA_QUALITY_THRESHOLDS

logger = logging.getLogger(__name__)


@dataclass
class PhoneValidationResult:
    """Resultado de validación de teléfono."""
    is_valid: bool
    cleaned_number: Optional[str]
    type: str  # 'MOVIL', 'FIJA', 'INVALIDO'
    error_message: Optional[str] = None
    has_city_code: bool = False  # Para fijos


class PhoneNumberValidator:
    """Validador robusto de números telefónicos colombianos."""
    
    @staticmethod
    def clean_and_validate(phone: str) -> PhoneValidationResult:
        """
        Valida y limpia un número telefónico colombiano.
        
        Reglas:
        - Móviles: 10 dígitos, inician con 3, prefijo válido
        - Fijos: 7 dígitos (sin indicativo) o 10 dígitos iniciando con 6
        
        Args:
            phone: Número a validar
        
        Returns:
            PhoneValidationResult con detalles de validación
        """
        if pd.isna(phone) or str(phone).strip() == '':
            return PhoneValidationResult(
                is_valid=False,
                cleaned_number=None,
                type='INVALIDO',
                error_message='Número vacío'
            )
        
        try:
            phone_str = str(phone).strip()
            
            # Intentar con phonenumbers primero
            try:
                parsed = phonenumbers.parse(phone_str, 'CO')
                
                if phonenumbers.is_valid_number(parsed):
                    national = phonenumbers.format_number(
                        parsed,
                        phonenumbers.PhoneNumberFormat.NATIONAL
                    ).replace(' ', '').replace('-', '')
                    
                    phone_type, has_city_code = PhoneNumberValidator._classify_type(national)
                    
                    return PhoneValidationResult(
                        is_valid=True,
                        cleaned_number=national,
                        type=phone_type,
                        has_city_code=has_city_code
                    )
            
            except NumberParseException:
                pass
            
            # Limpieza manual
            cleaned = ''.join(filter(str.isdigit, phone_str))
            
            # Remover prefijos internacionales
            if cleaned.startswith('57') and len(cleaned) > 10:
                cleaned = cleaned[2:]
            elif cleaned.startswith('957') and len(cleaned) > 10:
                cleaned = cleaned[3:]
            
            # Validar longitud
            if len(cleaned) not in {7, 10}:
                return PhoneValidationResult(
                    is_valid=False,
                    cleaned_number=None,
                    type='INVALIDO',
                    error_message=f'Longitud inválida: {len(cleaned)} dígitos'
                )
            
            # Clasificar y validar tipo
            phone_type, has_city_code = PhoneNumberValidator._classify_type(cleaned)
            
            if phone_type == 'INVALIDO':
                return PhoneValidationResult(
                    is_valid=False,
                    cleaned_number=None,
                    type='INVALIDO',
                    error_message='Prefijo no reconocido'
                )
            
            return PhoneValidationResult(
                is_valid=True,
                cleaned_number=cleaned,
                type=phone_type,
                has_city_code=has_city_code
            )
        
        except Exception as e:
            logger.error(f"Error validando teléfono '{phone}': {e}")
            return PhoneValidationResult(
                is_valid=False,
                cleaned_number=None,
                type='INVALIDO',
                error_message=str(e)
            )
    
    @staticmethod
    def _classify_type(phone: str) -> Tuple[str, bool]:
        """
        Clasifica un número como MOVIL, FIJA o INVALIDO.
        
        Returns:
            (tipo, tiene_codigo_ciudad)
        """
        # Móvil: 10 dígitos iniciando con 3
        if len(phone) == 10 and phone[0] == '3':
            prefix = phone[:3]
            if prefix in MOBILE_PREFIXES:
                return 'MOVIL', False
            else:
                logger.warning(f"Prefijo móvil no reconocido: {prefix}")
                return 'INVALIDO', False
        
        # Fijo con indicativo: 10 dígitos iniciando con 6
        if len(phone) == 10 and phone[0] == '6':
            city_code = phone[:3]
            if city_code in FIXED_LINE_CODES:
                return 'FIJA', True
            else:
                logger.warning(f"Indicativo fijo no reconocido: {city_code}")
                # Aceptar de todas formas si inicia con 6
                return 'FIJA', True
        
        # Fijo sin indicativo: 7 dígitos
        if len(phone) == 7:
            return 'FIJA', False
        
        return 'INVALIDO', False
    
    @classmethod
    def clean_series(
        cls,
        series: pd.Series,
        return_metadata: bool = False
    ) -> pd.Series | Tuple[pd.Series, pd.DataFrame]:
        """
        Aplica validación a una Serie de pandas.
        
        Args:
            series: Serie de números a validar
            return_metadata: Si True, retorna DataFrame con metadata
        
        Returns:
            Serie con números limpios (None si inválidos)
            Opcionalmente: DataFrame con metadata
        """
        logger.info(f"🔍 Validando {len(series):,} números telefónicos...")
        
        results = series.apply(cls.clean_and_validate)
        
        cleaned = results.apply(
            lambda r: r.cleaned_number if r.is_valid else None
        )
        
        # Estadísticas
        valid_count = cleaned.notna().sum()
        invalid_count = cleaned.isna().sum()
        
        # Contar por tipo
        movil_count = sum(1 for r in results if r.type == 'MOVIL')
        fija_count = sum(1 for r in results if r.type == 'FIJA')
        
        logger.info(
            f"✅ Validación completada: {valid_count:,} válidos, "
            f"{invalid_count:,} inválidos ({invalid_count/len(series)*100:.1f}%)"
        )
        logger.info(f"   📱 Móviles: {movil_count:,}")
        logger.info(f"   ☎️  Fijos: {fija_count:,}")
        
        if not return_metadata:
            return cleaned
        
        # Crear DataFrame de metadata
        metadata = pd.DataFrame({
            'telefono_original': series,
            'telefono_limpio': cleaned,
            'tipo_linea': results.apply(lambda r: r.type),
            'es_valido': results.apply(lambda r: r.is_valid),
            'tiene_indicativo': results.apply(lambda r: r.has_city_code),
            'error': results.apply(lambda r: r.error_message),
        })
        
        return cleaned, metadata


class DataQualityValidator:
    """Validador de calidad general de DataFrames."""
    
    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame,
        df_name: str,
        required_columns: Optional[set] = None
    ) -> Tuple[bool, str]:
        """
        Valida la calidad de un DataFrame.
        
        Returns:
            (is_valid, error_message)
        """
        if df.empty:
            return False, f"DataFrame '{df_name}' está vacío"
        
        if required_columns:
            missing_cols = required_columns - set(df.columns)
            if missing_cols:
                return False, f"Faltan columnas requeridas: {missing_cols}"
        
        # Verificar tasa de nulos
        null_rates = df.isnull().mean()
        high_null_cols = null_rates[
            null_rates > DATA_QUALITY_THRESHOLDS['max_null_rate']
        ]
        
        if not high_null_cols.empty:
            logger.warning(
                f"⚠️ Columnas con alta tasa de nulos en '{df_name}': "
                f"{high_null_cols.to_dict()}"
            )
        
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            logger.warning(
                f"⚠️ {duplicate_count:,} filas completamente duplicadas en '{df_name}'"
            )
        
        return True, "OK"
    
    @staticmethod
    def generate_quality_report(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
        """Genera un reporte detallado de calidad de datos."""
        
        report_data = []
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            null_rate = null_count / len(df)
            unique_count = df[col].nunique()
            dtype = str(df[col].dtype)
            
            if pd.api.types.is_numeric_dtype(df[col]):
                data_type = 'Numérico'
                min_val = df[col].min()
                max_val = df[col].max()
                mean_val = df[col].mean()
                stats = f"Min: {min_val}, Max: {max_val}, Mean: {mean_val:.2f}"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                data_type = 'Fecha'
                min_val = df[col].min()
                max_val = df[col].max()
                stats = f"Desde: {min_val}, Hasta: {max_val}"
            else:
                data_type = 'Texto'
                top_values = df[col].value_counts().head(3).to_dict()
                stats = f"Top 3: {top_values}"
            
            report_data.append({
                'columna': col,
                'tipo_datos': data_type,
                'dtype_pandas': dtype,
                'registros_totales': len(df),
                'valores_nulos': null_count,
                'tasa_nulos': f"{null_rate:.2%}",
                'valores_unicos': unique_count,
                'estadisticas': stats,
                'estado': '⚠️ REVISAR' if null_rate > 0.3 else '✅ OK'
            })
        
        return pd.DataFrame(report_data)