"""
Tests for EnhancedPhoneValidator.

Validates phone number cleaning and classification.
"""

import pytest
import pandas as pd
from src.services.phone_validator import EnhancedPhoneValidator

class TestEnhancedPhoneValidator:
    """Test enhanced phone validator functionality."""
    
    def setup_method(self):
        """Initialize validator for each test."""
        self.validator = EnhancedPhoneValidator()
    
    # ==========================================
    # MOVIL VALIDATION
    # ==========================================
    
    def test_valid_movil_300(self):
        """Test valid mobile number with 300 prefix."""
        result = self.validator.validate('3001234567')
        assert result.is_valid is True
        assert result.cleaned_phone == '3001234567'
        assert result.tipo_linea == 'MOVIL'
    
    def test_valid_movil_310(self):
        """Test valid mobile number with 310 prefix."""
        result = self.validator.validate('3101234567')
        assert result.is_valid is True
        assert result.tipo_linea == 'MOVIL'
    
    def test_valid_movil_320(self):
        """Test valid mobile number with 320 prefix."""
        result = self.validator.validate('3201234567')
        assert result.is_valid is True
        assert result.tipo_linea == 'MOVIL'
    
    def test_invalid_movil_prefix(self):
        """Test invalid mobile prefix (399)."""
        result = self.validator.validate('3991234567')
        assert result.is_valid is False
        assert 'Prefijo móvil no válido' in result.reason
    
    # ==========================================
    # FIJA VALIDATION
    # ==========================================
    
    def test_valid_fija_bogota(self):
        """Test valid Bogotá landline (601)."""
        result = self.validator.validate('6012345678')
        assert result.is_valid is True
        assert result.cleaned_phone == '6012345678'
        assert result.tipo_linea == 'FIJA'
        assert result.city_name == 'Bogotá'
    
    def test_valid_fija_medellin(self):
        """Test valid Medellín landline (604)."""
        result = self.validator.validate('6042345678')
        assert result.is_valid is True
        assert result.city_name == 'Medellín'
    
    def test_invalid_fija_city_code(self):
        """Test invalid city code (609)."""
        result = self.validator.validate('6091234567')
        assert result.is_valid is False
        assert 'Código de ciudad no válido' in result.reason
    
    # ==========================================
    # 957 PREFIX HANDLING (CRITICAL)
    # ==========================================
    
    def test_957_prefix_mobile(self):
        """Test 957 prefix handling - take 10 from right."""
        result = self.validator.validate('9573001234567')
        assert result.is_valid is True
        assert result.cleaned_phone == '3001234567'
        assert result.tipo_linea == 'MOVIL'
    
    def test_957_prefix_landline(self):
        """Test 957 prefix handling for landline."""
        result = self.validator.validate('9576012345678')
        assert result.is_valid is True
        assert result.cleaned_phone == '6012345678'
        assert result.tipo_linea == 'FIJA'
    
    def test_957_prefix_too_short(self):
        """Test 957 prefix with insufficient digits."""
        result = self.validator.validate('957300123')
        assert result.is_valid is False
        assert '957' in result.reason.lower()
    
    # ==========================================
    # EDGE CASES
    # ==========================================
    
    def test_empty_phone(self):
        """Test empty phone number."""
        result = self.validator.validate('')
        assert result.is_valid is False
        assert result.tipo_linea == 'INVALIDO'
    
    def test_none_phone(self):
        """Test None phone number."""
        result = self.validator.validate(None)
        assert result.is_valid is False
    
    def test_phone_with_spaces(self):
        """Test phone with spaces."""
        result = self.validator.validate('300 123 4567')
        assert result.is_valid is True
        assert result.cleaned_phone == '3001234567'
    
    def test_phone_with_dashes(self):
        """Test phone with dashes."""
        result = self.validator.validate('300-123-4567')
        assert result.is_valid is True
        assert result.cleaned_phone == '3001234567'
    
    def test_phone_wrong_length_short(self):
        """Test phone too short."""
        result = self.validator.validate('300123456')  # 9 digits
        assert result.is_valid is False
        assert 'Longitud incorrecta' in result.reason
    
    def test_phone_wrong_length_long(self):
        """Test phone too long."""
        result = self.validator.validate('30012345678')  # 11 digits
        assert result.is_valid is False
    
    def test_phone_starts_with_5(self):
        """Test phone starting with 5 (invalid)."""
        result = self.validator.validate('5551234567')
        assert result.is_valid is False
        assert 'debe iniciar con 3' in result.reason.lower() or 'inicia con' in result.reason.lower()
    
    # ==========================================
    # SERIES VALIDATION
    # ==========================================
    
    def test_validate_series(self):
        """Test validating a Series of phone numbers."""
        phones = pd.Series([
            '3001234567',  # Valid mobile
            '6012345678',  # Valid landline
            '9573009876543',  # Valid with 957
            '5551234567',  # Invalid
            '300123',  # Too short
        ])
        
        cleaned, metadata = self.validator.validate_series(phones)
        
        # Check counts
        assert metadata['es_valido'].sum() == 3  # 3 valid
        assert (~metadata['es_valido']).sum() == 2  # 2 invalid
        
        # Check first (valid mobile)
        assert cleaned.iloc[0] == '3001234567'
        assert metadata.iloc[0]['tipo_linea'] == 'MOVIL'
        
        # Check second (valid landline)
        assert cleaned.iloc[1] == '6012345678'
        assert metadata.iloc[1]['tipo_linea'] == 'FIJA'
        
        # Check third (957 prefix)
        assert cleaned.iloc[2] == '3009876543'
        
        # Check fourth (invalid)
        assert pd.isna(cleaned.iloc[3]) or cleaned.iloc[3] is None
        assert metadata.iloc[3]['es_valido'] == False

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
