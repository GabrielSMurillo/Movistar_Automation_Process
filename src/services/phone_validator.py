"""
Enhanced Phone Number Validator with Complete Business Rules.

Validation Rules:
1. Handle 957 prefix: Take 10 digits from RIGHT
2. Must be exactly 10 digits
3. MOVIL: Starts with 3, valid mobile prefix
4. FIJA: Starts with 6, valid city code
5. FIJA must have city code prefix

Example:
    >>> validator = EnhancedPhoneValidator()
    >>> result = validator.validate('9573001234567')
    >>> print(result)
    ValidationResult(
        is_valid=True,
        cleaned_phone='3001234567',
        tipo_linea='MOVIL',
        reason=''
    )
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Set
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class PhoneValidationResult:
    """Result of phone validation."""
    is_valid: bool
    cleaned_phone: Optional[str]
    tipo_linea: str  # MOVIL, FIJA, INVALIDO
    reason: str  # Rejection reason if invalid
    has_city_code: bool = False  # For FIJA
    city_name: Optional[str] = None  # For FIJA


class EnhancedPhoneValidator:
    """
    Enhanced phone validator with complete business rules.
    
    Implements all validation requirements including:
    - 957 prefix handling
    - Mobile/landline classification
    - Prefix validation
    - City code validation for landlines
    """
    
    # Valid mobile prefixes (Colombia)
    MOBILE_PREFIXES: Set[str] = {
        '300', '301', '302', '303', '304', '305',
        '310', '311', '312', '313', '314', '315',
        '316', '317', '318', '319', '320', '321',
        '322', '323', '324', '350', '351', '352'
    }
    
    # Valid city codes for landlines (Colombia)
    CITY_CODES: dict[str, str] = {
        '601': 'Bogotá',
        '602': 'Cali',
        '604': 'Medellín',
        '605': 'Cartagena',
        '606': 'Pereira',
        '607': 'Bucaramanga',
        '608': 'Barranquilla',
    }
    
    def __init__(self):
        """Initialize enhanced phone validator."""
        self.logger = logging.getLogger(f"{__name__}.EnhancedPhoneValidator")
    
    def validate(self, phone: any) -> PhoneValidationResult:
        """
        Validate phone number with complete business rules.
        
        Args:
            phone: Raw phone number (string or number)
        
        Returns:
            PhoneValidationResult with validation details
        
        Example:
            >>> validator = EnhancedPhoneValidator()
            >>> result = validator.validate('9573001234567')
            >>> print(result.cleaned_phone)  # '3001234567'
            >>> print(result.tipo_linea)  # 'MOVIL'
        """
        # Check if empty
        if pd.isna(phone) or phone == '' or phone is None:
            return PhoneValidationResult(
                is_valid=False,
                cleaned_phone=None,
                tipo_linea='INVALIDO',
                reason='Número vacío'
            )
        
        # Clean phone (keep only digits)
        cleaned = ''.join(filter(str.isdigit, str(phone)))
        
        if not cleaned:
            return PhoneValidationResult(
                is_valid=False,
                cleaned_phone=None,
                tipo_linea='INVALIDO',
                reason='Número sin dígitos válidos'
            )
        
        # CRITICAL: Handle 957 prefix
        if cleaned.startswith('957'):
            original_length = len(cleaned)
            # Take 10 digits from RIGHT
            if len(cleaned) > 10:
                cleaned = cleaned[-10:]
                self.logger.debug(
                    f"Removido prefijo 957: {original_length} dígitos → {len(cleaned)} dígitos"
                )
            else:
                return PhoneValidationResult(
                    is_valid=False,
                    cleaned_phone=None,
                    tipo_linea='INVALIDO',
                    reason=f'Número con prefijo 957 inválido: solo {len(cleaned)} dígitos'
                )
        
        # Remove international prefix if present
        if cleaned.startswith('57') and len(cleaned) == 12:
            cleaned = cleaned[2:]  # Remove +57
        
        # Validate length
        if len(cleaned) != 10:
            return PhoneValidationResult(
                is_valid=False,
                cleaned_phone=None,
                tipo_linea='INVALIDO',
                reason=f'Longitud incorrecta: {len(cleaned)} dígitos (se requieren 10)'
            )
        
        # Classify and validate based on first digit
        first_digit = cleaned[0]
        
        if first_digit == '3':
            return self._validate_movil(cleaned)
        elif first_digit == '6':
            return self._validate_fija(cleaned)
        else:
            return PhoneValidationResult(
                is_valid=False,
                cleaned_phone=None,
                tipo_linea='INVALIDO',
                reason=f'Número debe iniciar con 3 (móvil) o 6 (fijo). Inicia con: {first_digit}'
            )
    
    def _validate_movil(self, phone: str) -> PhoneValidationResult:
        """
        Validate mobile number.
        
        Args:
            phone: Cleaned 10-digit number starting with 3
        
        Returns:
            PhoneValidationResult
        """
        prefix = phone[:3]
        
        if prefix not in self.MOBILE_PREFIXES:
            return PhoneValidationResult(
                is_valid=False,
                cleaned_phone=None,
                tipo_linea='INVALIDO',
                reason=f'Prefijo móvil no válido: {prefix}'
            )
        
        return PhoneValidationResult(
            is_valid=True,
            cleaned_phone=phone,
            tipo_linea='MOVIL',
            reason=''
        )
    
    def _validate_fija(self, phone: str) -> PhoneValidationResult:
        """
        Validate landline number.
        
        CRITICAL: Landlines MUST have city code prefix.
        
        Args:
            phone: Cleaned 10-digit number starting with 6
        
        Returns:
            PhoneValidationResult
        """
        city_code = phone[:3]
        
        if city_code not in self.CITY_CODES:
            return PhoneValidationResult(
                is_valid=False,
                cleaned_phone=None,
                tipo_linea='INVALIDO',
                reason=f'Código de ciudad no válido: {city_code}. Códigos válidos: {list(self.CITY_CODES.keys())}'
            )
        
        city_name = self.CITY_CODES[city_code]
        
        return PhoneValidationResult(
            is_valid=True,
            cleaned_phone=phone,
            tipo_linea='FIJA',
            reason='',
            has_city_code=True,
            city_name=city_name
        )
    
    def validate_series(
        self,
        series: pd.Series
    ) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Validate a pandas Series of phone numbers.
        
        Args:
            series: Series with phone numbers
        
        Returns:
            Tuple of:
            - Series with cleaned phones (None for invalid)
            - DataFrame with validation metadata
        
        Example:
            >>> validator = EnhancedPhoneValidator()
            >>> phones = pd.Series(['3001234567', '9573009876543', '5551234567'])
            >>> cleaned, metadata = validator.validate_series(phones)
            >>> print(cleaned)
            0    3001234567
            1    3009876543
            2          None
        """
        results = series.apply(self.validate)
        
        # Extract data
        cleaned_phones = results.apply(lambda r: r.cleaned_phone if r.is_valid else None)
        
        # Create metadata DataFrame
        metadata = pd.DataFrame({
            'telefono_original': series,
            'telefono_limpio': cleaned_phones,
            'tipo_linea': results.apply(lambda r: r.tipo_linea),
            'es_valido': results.apply(lambda r: r.is_valid),
            'tiene_indicativo': results.apply(lambda r: r.has_city_code),
            'ciudad': results.apply(lambda r: r.city_name),
            'motivo_rechazo': results.apply(lambda r: r.reason if not r.is_valid else ''),
        })
        
        # Log statistics
        valid_count = metadata['es_valido'].sum()
        invalid_count = (~metadata['es_valido']).sum()
        movil_count = (metadata['tipo_linea'] == 'MOVIL').sum()
        fija_count = (metadata['tipo_linea'] == 'FIJA').sum()
        
        self.logger.info("=" * 60)
        self.logger.info("📞 VALIDACIÓN DE TELÉFONOS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total procesados: {len(series):,}")
        self.logger.info(f"✅ Válidos: {valid_count:,} ({valid_count/len(series)*100:.1f}%)")
        self.logger.info(f"❌ Inválidos: {invalid_count:,} ({invalid_count/len(series)*100:.1f}%)")
        self.logger.info(f"📱 Móviles: {movil_count:,}")
        self.logger.info(f"☎️  Fijos: {fija_count:,}")
        
        if invalid_count > 0:
            self.logger.info("\nMotivos de rechazo:")
            rejection_reasons = metadata[~metadata['es_valido']]['motivo_rechazo'].value_counts()
            for reason, count in rejection_reasons.items():
                self.logger.info(f"  • {reason}: {count:,}")
        
        self.logger.info("=" * 60)
        
        return cleaned_phones, metadata


# Export
__all__ = ['EnhancedPhoneValidator', 'PhoneValidationResult']
