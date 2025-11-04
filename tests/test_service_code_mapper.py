"""
Tests for ServiceCodeMapper.

Validates that service codes are correct for each line type.
"""

import pytest
from src.services.service_code_mapper import ServiceCodeMapper


class TestServiceCodeMapper:
    """Test service code mapping functionality."""
    
    def setup_method(self):
        """Initialize mapper for each test."""
        self.mapper = ServiceCodeMapper()
    
    # ==========================================
    # MOVIL CODES (CRITICAL TESTS)
    # ==========================================
    
    def test_movil_mascota_code(self):
        """Test TU MASCOTA MOVIL returns correct code."""
        code, program = self.mapper.get_code('TU MASCOTA', 'MOVIL')
        assert code == '3823', f"Expected '3823', got '{code}'"
        assert program == 'TU MASCOTA'
    
    def test_movil_hogar_code(self):
        """Test TU HOGAR MOVIL returns correct code."""
        code, program = self.mapper.get_code('TU HOGAR', 'MOVIL')
        assert code == '5000', f"Expected '5000', got '{code}'"
    
    def test_movil_vehiculo_code(self):
        """Test TU VEHICULO MOVIL returns correct code."""
        code, program = self.mapper.get_code('TU VEHICULO', 'MOVIL')
        assert code == '5002', f"Expected '5002', got '{code}'"
    
    def test_movil_bienestar_code(self):
        """Test TU BIENESTAR MOVIL returns correct code."""
        code, program = self.mapper.get_code('TU BIENESTAR', 'MOVIL')
        assert code == '2119', f"Expected '2119', got '{code}'"
    
    # ==========================================
    # FIJA CODES (CRITICAL TESTS)
    # ==========================================
    
    def test_fija_mascota_code(self):
        """Test TU MASCOTA FIJA returns correct code."""
        code, program = self.mapper.get_code('TU MASCOTA', 'FIJA')
        assert code == '15639', f"Expected '15639', got '{code}'"
        assert program == 'TU MASCOTA'
    
    def test_fija_hogar_code(self):
        """Test TU HOGAR FIJA returns correct code."""
        code, program = self.mapper.get_code('TU HOGAR', 'FIJA')
        assert code == '15641', f"Expected '15641', got '{code}'"
    
    def test_fija_vehiculo_code(self):
        """Test TU VEHICULO FIJA returns correct code."""
        code, program = self.mapper.get_code('TU VEHICULO', 'FIJA')
        assert code == '15642', f"Expected '15642', got '{code}'"
    
    def test_fija_bienestar_code(self):
        """Test TU BIENESTAR FIJA returns correct code."""
        code, program = self.mapper.get_code('TU BIENESTAR', 'FIJA')
        assert code == '15640', f"Expected '15640', got '{code}'"
    
    # ==========================================
    # DIGITAL CODES (CRITICAL TESTS)
    # ==========================================
    
    def test_digital_mascotas_code(self):
        """Test MASCOTAS DIGITAL returns correct code."""
        code, program = self.mapper.get_code('MASCOTAS', 'DIGITAL')
        assert code == '4046', f"Expected '4046', got '{code}'"
        assert program == 'Mascotas'
    
    def test_digital_vial_code(self):
        """Test VIAL DIGITAL returns correct code."""
        code, program = self.mapper.get_code('VIAL', 'DIGITAL')
        assert code == '4045', f"Expected '4045', got '{code}'"
    
    def test_digital_multiasistencia_code(self):
        """Test MULTIASISTENCIA DIGITAL returns correct code."""
        code, program = self.mapper.get_code('HOGAR', 'DIGITAL')
        assert code == '4047', f"Expected '4047', got '{code}'"
    
    # ==========================================
    # EDGE CASES
    # ==========================================
    
    def test_case_insensitive(self):
        """Test that matching is case-insensitive."""
        code1, _ = self.mapper.get_code('tu mascota', 'MOVIL')
        code2, _ = self.mapper.get_code('TU MASCOTA', 'MOVIL')
        code3, _ = self.mapper.get_code('Tu Mascota', 'MOVIL')
        
        assert code1 == code2 == code3 == '3823'
    
    def test_keyword_matching(self):
        """Test that keywords in descriptions work."""
        code, _ = self.mapper.get_code('Venta de MASCOTA premium', 'MOVIL')
        assert code == '3823', "Should match MASCOTA keyword"
    
    def test_default_movil(self):
        """Test default code for unknown product MOVIL."""
        code, _ = self.mapper.get_code('PRODUCTO DESCONOCIDO', 'MOVIL')
        assert code in ['2119', '3823', '5000', '5002'], "Should return valid MOVIL code"
    
    def test_default_fija(self):
        """Test default code for unknown product FIJA."""
        code, _ = self.mapper.get_code('PRODUCTO DESCONOCIDO', 'FIJA')
        assert code in ['15639', '15640', '15641', '15642'], "Should return valid FIJA code"
    
    # ==========================================
    # VALIDATION TESTS
    # ==========================================
    
    def test_validate_movil_codes(self):
        """Test code validation for MOVIL."""
        assert self.mapper.validate_code('3823', 'MOVIL') is True
        assert self.mapper.validate_code('15639', 'MOVIL') is False  # FIJA code
    
    def test_validate_fija_codes(self):
        """Test code validation for FIJA."""
        assert self.mapper.validate_code('15639', 'FIJA') is True
        assert self.mapper.validate_code('3823', 'FIJA') is False  # MOVIL code
    
    def test_validate_digital_codes(self):
        """Test code validation for DIGITAL."""
        assert self.mapper.validate_code('4046', 'DIGITAL') is True
        assert self.mapper.validate_code('3823', 'DIGITAL') is False  # MOVIL code
    
    def test_get_all_codes(self):
        """Test getting all codes returns complete mapping."""
        all_codes = self.mapper.get_all_codes()
        
        assert 'MOVIL' in all_codes
        assert 'FIJA' in all_codes
        assert 'DIGITAL' in all_codes
        
        assert len(all_codes['MOVIL']) == 4
        assert len(all_codes['FIJA']) == 4
        assert len(all_codes['DIGITAL']) == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
