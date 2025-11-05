"""
Tests de integración para verificar que el nuevo sistema funciona.

Ejecutar con: pytest tests/test_core_integration.py -v
"""

import pytest
from pathlib import Path
from datetime import date
import sys

# Asegurar que src está en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestCoreConfig:
    """Tests para el nuevo sistema de configuración."""
    
    def test_settings_can_be_imported(self):
        """Verificar que Settings se puede importar."""
        from src.core.config import get_settings
        assert get_settings is not None
    
    def test_settings_singleton(self):
        """Verificar que Settings es singleton."""
        from src.core.config import get_settings
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2
    
    def test_settings_properties(self):
        """Verificar propiedades básicas de Settings."""
        from src.core.config import get_settings
        
        settings = get_settings()
        
        # Verificar que las properties existen
        assert hasattr(settings, 'base_dir')
        assert hasattr(settings, 'data_dir')
        assert hasattr(settings, 'input_dir')
        assert hasattr(settings, 'output_dir')
        assert hasattr(settings, 'start_date')
        assert hasattr(settings, 'end_date')
        
        # Verificar que son del tipo correcto
        assert isinstance(settings.base_dir, Path)
        assert isinstance(settings.start_date, date)
        assert isinstance(settings.end_date, date)

class TestCoreExceptions:
    """Tests para custom exceptions."""
    
    def test_phone_validation_error(self):
        """Test PhoneValidationError."""
        from src.core.exceptions import PhoneValidationError
        
        with pytest.raises(PhoneValidationError) as exc_info:
            raise PhoneValidationError(phone="123", reason="Too short")
        
        exception = exc_info.value
        assert "123" in str(exception)
        assert "Too short" in str(exception)
        assert exception.details['phone'] == "123"
        assert exception.details['reason'] == "Too short"
    
    def test_config_error(self):
        """Test ConfigurationError."""
        from src.core.exceptions import ConfigurationError
        
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Invalid config")
        
        assert "Invalid config" in str(exc_info.value)

class TestCoreModels:
    """Tests para domain models."""
    
    def test_sale_record_valid(self):
        """Test creación de SaleRecord válido."""
        from src.core.models import SaleRecord
        from datetime import datetime
        
        record = SaleRecord(
            telefono_servicio="3001234567",
            nombre_cliente="Juan Perez",
            tipo_venta="TU MASCOTA",
            fecha_venta=date.today(),
            marca_temporal=datetime.now(),
            nombre_asesor="Maria Lopez"
        )
        
        assert record.telefono_servicio == "3001234567"
        assert record.nombre_cliente == "Juan Perez"
        assert record.is_valid
    
    def test_sale_record_invalid_phone(self):
        """Test validación de teléfono inválido."""
        from src.core.models import SaleRecord
        from src.core.exceptions import PhoneValidationError
        from datetime import datetime
        from pydantic import ValidationError
        
        with pytest.raises((PhoneValidationError, ValidationError)):
            SaleRecord(
                telefono_servicio="12",  # Muy corto
                nombre_cliente="Juan Perez",
                tipo_venta="TU MASCOTA",
                fecha_venta=date.today(),
                marca_temporal=datetime.now(),
                nombre_asesor="Maria Lopez"
            )
    
    def test_sale_record_invalid_asesor(self):
        """Test validación de asesor inválido."""
        from src.core.models import SaleRecord
        from src.core.exceptions import DataValidationError
        from datetime import datetime
        from pydantic import ValidationError
        
        # El modelo puede levantar DataValidationError o ValidationError
        with pytest.raises((DataValidationError, ValidationError)):
            SaleRecord(
                telefono_servicio="3001234567",
                nombre_cliente="Juan Perez",
                tipo_venta="TU MASCOTA",
                fecha_venta=date.today(),
                marca_temporal=datetime.now(),
                nombre_asesor="Maria123"  # Contiene números
            )

class TestCoreDecorators:
    """Tests para decorators."""
    
    def test_timing_decorator(self):
        """Test que timing decorator funciona."""
        from src.core.decorators import timing
        import time
        
        @timing
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        assert result == "done"
    
    def test_retry_decorator_success(self):
        """Test retry con función que funciona."""
        from src.core.decorators import retry
        
        @retry(max_attempts=3)
        def working_function():
            return "success"
        
        result = working_function()
        assert result == "success"
    
    def test_retry_decorator_eventual_success(self):
        """Test retry con función que falla y luego funciona."""
        from src.core.decorators import retry
        
        counter = {"calls": 0}
        
        @retry(max_attempts=3, delay=0.1)
        def failing_then_working():
            counter["calls"] += 1
            if counter["calls"] < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = failing_then_working()
        assert result == "success"
        assert counter["calls"] == 2

class TestBackwardCompatibility:
    """Tests para verificar compatibilidad hacia atrás."""
    
    def test_old_config_still_works(self):
        """Verificar que el config.py viejo aún funciona."""
        import config
        
        # Verificar que las constantes antiguas existen
        assert hasattr(config, 'BASE_DIR')
        assert hasattr(config, 'INPUT_DIR')
        assert hasattr(config, 'OUTPUT_DIR')
        assert hasattr(config, 'START_DATE')
        assert hasattr(config, 'END_DATE')
        
        # Verificar tipos
        assert isinstance(config.BASE_DIR, Path)
        assert isinstance(config.START_DATE, date)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
