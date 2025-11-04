# tests/test_processors.py
"""
Tests unitarios para procesadores.
"""

import pytest
import pandas as pd
from datetime import date
from src.data_processor import TipificadorProcessor, DigitalProcessor
from config import TIPIFICADOR_COLS_MAP


class TestTipificadorProcessor:
    """Tests para TipificadorProcessor."""
    
    @pytest.fixture
    def sample_tipificador_data(self):
        """Fixture con datos de ejemplo del tipificador."""
        return pd.DataFrame({
            'Marca temporal': ['2025-10-23 10:00', '2025-10-24 11:00', '2025-10-25 12:00'],
            'Nombre del asesor': ['Juan Pérez', 'María López', 'Carlos Gómez'],
            'Nombre del cliente': ['Cliente 1', 'Cliente 2', 'Cliente 3'],
            'TELEFONO DEL CLIENTE( DONDE SE VA CARGAR EL SERVICIO )': ['3001234567', '57 300 234 5678', '601 234 5678'],
            'TIPO DE VENTA': ['MOVIL', 'MOVIL', 'FIJA'],
            '¿LA VENTA PROVIENE DE UN REFERIDO?': ['no', 'sí', 'no'],
            'BASE ASIGNADA': ['Base1', 'Base2', 'Base3'],
            'Documento de identidad del cliente': ['123456', '234567', '345678'],
            'costo plan': ['50000', '60000', '70000'],
            'Dirección del cliente': ['Calle 1', 'Calle 2', 'Calle 3'],
        })
    
    def test_process_tipificador(self, sample_tipificador_data):
        """Test procesamiento completo del tipificador."""
        df_ventas, df_referidos, metrics = TipificadorProcessor.process(
            sample_tipificador_data,
            TIPIFICADOR_COLS_MAP,
            date(2025, 10, 23),
            date(2025, 10, 25)
        )
        
        # Verificar separación de ventas y referidos
        assert len(df_ventas) == 2  # Dos ventas de base
        assert len(df_referidos) == 1  # Un referido
        
        # Verificar que los teléfonos fueron limpiados
        assert 'telefono_limpio' in df_ventas.columns
        assert df_ventas['telefono_limpio'].notna().all()
        
        # Verificar detección de tipo de línea
        assert 'tipo_linea' in df_ventas.columns
        
        # Verificar métricas
        assert 'tipificador' in metrics
        assert 'ventas_procesadas' in metrics
        assert 'referidos' in metrics


class TestDigitalProcessor:
    """Tests para DigitalProcessor."""
    
    @pytest.fixture
    def sample_digital_data(self):
        """Fixture con datos de ejemplo de digital."""
        return pd.DataFrame({
            'Num_Celular': ['3001234567', '3002345678'],
            'Fecha de venta': ['2025-10-23', '2025-10-24'],
            'Nombre del cliente': ['Cliente A', 'Cliente B'],
            'cod_plantarif': ['PLAN001', 'PLAN002'],
            'Plan': ['Plan 50GB', 'Plan 100GB'],
        })
    
    def test_process_digital(self, sample_digital_data):
        """Test procesamiento de ventas digitales."""
        from config import DIGITAL_COLS_MAP
        
        df_processed, metrics = DigitalProcessor.process(
            sample_digital_data,
            DIGITAL_COLS_MAP,
            date(2025, 10, 23),
            date(2025, 10, 25)
        )
        
        # Verificar que se procesaron ambos registros
        assert len(df_processed) == 2
        
        # Verificar limpieza de teléfonos
        assert 'telefono_limpio' in df_processed.columns
        assert df_processed['telefono_limpio'].notna().all()
        
        # Verificar tipo de venta asignado
        assert 'tipo_venta' in df_processed.columns
        assert (df_processed['tipo_venta'] == 'DIGITAL').all()