# tests/test_validators.py
"""
Tests unitarios para validadores.
"""

import pytest
import pandas as pd
from src.validators import PhoneNumberValidator, DataQualityValidator

class TestPhoneNumberValidator:
    """Tests para PhoneNumberValidator."""
    
    def test_clean_colombian_mobile(self):
        """Test limpieza de números móviles colombianos."""
        test_cases = [
            ('+57 300 123 4567', '3001234567', 'MOVIL'),
            ('57 300 123 4567', '3001234567', 'MOVIL'),
            ('300 123 4567', '3001234567', 'MOVIL'),
            ('3001234567', '3001234567', 'MOVIL'),
            ('957 300 123 4567', '3001234567', 'MOVIL'),
        ]
        
        for phone_input, expected_clean, expected_type in test_cases:
            result = PhoneNumberValidator.clean_and_validate(phone_input)
            assert result.is_valid, f"Número {phone_input} debería ser válido"
            assert result.cleaned_number == expected_clean
            assert result.type == expected_type
    
    def test_clean_colombian_fixed(self):
        """Test limpieza de números fijos colombianos."""
        test_cases = [
            ('601 234 5678', '6012345678', 'FIJA'),
            ('6012345678', '6012345678', 'FIJA'),
            ('234 5678', '2345678', 'FIJA'),  # Fijo sin indicativo
            ('2345678', '2345678', 'FIJA'),
        ]
        
        for phone_input, expected_clean, expected_type in test_cases:
            result = PhoneNumberValidator.clean_and_validate(phone_input)
            assert result.is_valid, f"Número {phone_input} debería ser válido"
            assert result.cleaned_number == expected_clean
            assert result.type == expected_type
    
    def test_invalid_phones(self):
        """Test números inválidos."""
        invalid_cases = [
            '',
            'abc123',
            '123',
            '12345',
            '123456789012345',
            None,
            '999123456',  # Prefijo inválido
        ]
        
        for phone_input in invalid_cases:
            result = PhoneNumberValidator.clean_and_validate(phone_input)
            assert not result.is_valid, f"Número {phone_input} debería ser inválido"
            assert result.cleaned_number is None
            assert result.type == 'INVALIDO'
    
    def test_clean_series(self):
        """Test limpieza de Serie de pandas."""
        phones = pd.Series([
            '3001234567',
            '57 300 123 4567',
            '601 234 5678',
            'invalid',
            None,
        ])
        
        cleaned = PhoneNumberValidator.clean_series(phones)
        
        assert cleaned[0] == '3001234567'
        assert cleaned[1] == '3001234567'
        assert cleaned[2] == '6012345678'
        assert pd.isna(cleaned[3])
        assert pd.isna(cleaned[4])

class TestDataQualityValidator:
    """Tests para DataQualityValidator."""
    
    def test_validate_empty_dataframe(self):
        """Test DataFrame vacío."""
        df = pd.DataFrame()
        is_valid, message = DataQualityValidator.validate_dataframe(df, "Test")
        
        assert not is_valid
        assert "vacío" in message.lower()
    
    def test_validate_missing_columns(self):
        """Test columnas faltantes."""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        required = {'col1', 'col2', 'col3'}
        
        is_valid, message = DataQualityValidator.validate_dataframe(
            df, "Test", required
        )
        
        assert not is_valid
        assert 'col2' in message
        assert 'col3' in message
    
    def test_generate_quality_report(self):
        """Test generación de reporte de calidad."""
        df = pd.DataFrame({
            'numeros': [1, 2, None, 4, 5],
            'textos': ['a', 'b', 'c', None, 'e'],
            'fechas': pd.to_datetime(['2025-01-01', '2025-01-02', None, '2025-01-04', '2025-01-05']),
        })
        
        report = DataQualityValidator.generate_quality_report(df, "Test")
        
        assert len(report) == 3
        assert 'columna' in report.columns
        assert 'tipo_datos' in report.columns
        assert 'valores_nulos' in report.columns