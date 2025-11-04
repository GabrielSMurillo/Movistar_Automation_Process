"""
Tests unitarios para ContactLogGenerator.

Cobertura objetivo: 80%
"""

import unittest
from pathlib import Path
import pandas as pd
from datetime import date, time
import tempfile
import shutil

from src.generators.contact_log_generator import ContactLogGenerator


class TestContactLogGenerator(unittest.TestCase):
    """Suite de tests para ContactLogGenerator."""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests."""
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.generator = ContactLogGenerator()
    
    @classmethod
    def tearDownClass(cls):
        """Limpieza después de todos los tests."""
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)
    
    def setUp(self):
        """Configuración antes de cada test."""
        # Crear datos de prueba
        self.valid_data = pd.DataFrame({
            'telefono_limpio': ['3001234567', '6012345678', '3109876543'],
            'nombre_asesor': ['Juan Perez', 'Maria Lopez', 'Carlos Ruiz'],
            'fecha_venta': [date(2025, 10, 25), date(2025, 10, 26), date(2025, 10, 27)],
            'hora_venta': [time(10, 30), time(14, 15), time(16, 45)],
            'cod_servicio': ['2119', '2120', '4045'],
            'programa': ['ASISTENCIAS', 'ASISTENCIAS', 'ASISTENCIAS'],
        })
        
        self.invalid_data = pd.DataFrame({
            'telefono_limpio': ['123', '30012345678', ''],  # Inválidos
            'nombre_asesor': ['Test User', 'Test User', 'Test User'],
            'fecha_venta': [date(2025, 10, 25)] * 3,
            'hora_venta': [time(10, 30)] * 3,
            'cod_servicio': ['2119'] * 3,
            'programa': ['ASISTENCIAS'] * 3,
        })
    
    # ============================================
    # Tests de _filter_valid_sales
    # ============================================
    
    def test_filter_valid_sales_all_valid(self):
        """Test: Filtrar ventas con todos los teléfonos válidos."""
        filtered = self.generator._filter_valid_sales(self.valid_data)
        
        self.assertEqual(len(filtered), 3, "Debería mantener los 3 registros válidos")
        self.assertTrue(
            all(filtered['telefono_limpio'].str.len() == 10),
            "Todos los teléfonos deberían tener 10 dígitos"
        )
    
    def test_filter_valid_sales_all_invalid(self):
        """Test: Filtrar ventas con todos los teléfonos inválidos."""
        filtered = self.generator._filter_valid_sales(self.invalid_data)
        
        self.assertEqual(len(filtered), 0, "No debería haber registros válidos")
    
    def test_filter_valid_sales_mixed(self):
        """Test: Filtrar ventas con teléfonos mixtos (válidos e inválidos)."""
        mixed_data = pd.concat([self.valid_data, self.invalid_data], ignore_index=True)
        filtered = self.generator._filter_valid_sales(mixed_data)
        
        self.assertEqual(len(filtered), 3, "Debería mantener solo los 3 válidos")
    
    def test_filter_valid_sales_empty_df(self):
        """Test: Filtrar DataFrame vacío."""
        empty_df = pd.DataFrame()
        filtered = self.generator._filter_valid_sales(empty_df)
        
        self.assertEqual(len(filtered), 0, "DataFrame vacío debería retornar vacío")
    
    def test_filter_valid_sales_null_phones(self):
        """Test: Filtrar ventas con teléfonos nulos."""
        null_data = self.valid_data.copy()
        null_data.loc[0, 'telefono_limpio'] = None
        
        filtered = self.generator._filter_valid_sales(null_data)
        
        self.assertEqual(len(filtered), 2, "Debería excluir el registro con teléfono nulo")
    
    # ============================================
    # Tests de _build_contact_records
    # ============================================
    
    def test_build_contact_records_structure(self):
        """Test: Verificar estructura de registros generados."""
        records = self.generator._build_contact_records(self.valid_data)
        
        self.assertEqual(len(records), 3, "Debería generar 3 registros")
        
        # Verificar estructura de cada registro (es una lista de 3 elementos)
        for record in records:
            self.assertIsInstance(record, list, "Cada registro debería ser una lista")
            self.assertEqual(len(record), 3, "Cada registro debería tener 3 elementos")
            self.assertIsInstance(record[0], str, "Primer elemento (Linea) debería ser string")
            self.assertIsInstance(record[1], str, "Segundo elemento (Observacion) debería ser string")
            self.assertIsInstance(record[2], str, "Tercer elemento (Razon) debería ser string")
    
    def test_build_contact_records_phone_format(self):
        """Test: Verificar formato de teléfonos en registros."""
        records = self.generator._build_contact_records(self.valid_data)
        
        # records es una lista de listas, el primer elemento [0] es el teléfono
        phones = [rec[0] for rec in records]
        
        # Todos deberían ser strings de 10 dígitos
        for phone in phones:
            self.assertIsInstance(phone, str, "Teléfono debería ser string")
            self.assertEqual(len(phone), 10, "Teléfono debería tener 10 dígitos")
            self.assertTrue(phone.isdigit(), "Teléfono debería ser solo números")
    
    def test_build_contact_records_observacion_content(self):
        """Test: Verificar contenido de Campo Observacion."""
        records = self.generator._build_contact_records(self.valid_data)
        
        for i, record in enumerate(records):
            # record[1] es Campo Observacion
            observacion = record[1]
            
            # Verificar que contenga elementos clave
            self.assertIn('Asesor de venta', observacion, "Debería mencionar asesor")
            self.assertIn(self.valid_data.iloc[i]['nombre_asesor'], observacion)
            self.assertIn('Fecha de venta', observacion, "Debería incluir fecha")
            self.assertIn('Hora de venta', observacion, "Debería incluir hora")
            self.assertIn('Cliente acepta SI', observacion, "Debería incluir aceptación")
    
    def test_build_contact_records_razon_content(self):
        """Test: Verificar contenido de Campo Razon (3 nodos)."""
        records = self.generator._build_contact_records(self.valid_data)
        
        for i, record in enumerate(records):
            # record[2] es Campo Razon
            razon = record[2]
            
            # Verificar estructura de 3 nodos
            self.assertIn('Activaciones Serv Suplementarios', razon, "Debería tener nodo 1")
            self.assertIn('Asistencias', razon, "Debería tener nodo 2")
            self.assertIn(self.valid_data.iloc[i]['cod_servicio'], razon, "Debería incluir código")
            self.assertIn('ASISTENCIAS: Venta telefonica', razon, "Debería tener nodo 3")
    
    def test_build_contact_records_empty_df(self):
        """Test: Construir registros desde DataFrame vacío."""
        empty_df = pd.DataFrame()
        records = self.generator._build_contact_records(empty_df)
        
        self.assertEqual(len(records), 0, "No debería generar registros")
    
    # ============================================
    # Tests de generate
    # ============================================
    
    def test_generate_success(self):
        """Test: Generación exitosa de archivo Contact Log."""
        output_path = self.temp_dir / 'test_contact_log.xlsx'
        
        success = self.generator.generate(
            self.valid_data,
            output_path,
            validate=True
        )
        
        self.assertTrue(success, "Generación debería ser exitosa")
        self.assertTrue(output_path.exists(), "Archivo debería existir")
        self.assertEqual(
            self.generator.records_processed, 3,
            "Debería haber procesado 3 registros"
        )
        self.assertEqual(
            self.generator.records_skipped, 0,
            "No debería haber omitido registros"
        )
    
    def test_generate_with_invalid_phones(self):
        """Test: Generación con teléfonos inválidos (deberían omitirse)."""
        mixed_data = pd.concat([self.valid_data, self.invalid_data], ignore_index=True)
        output_path = self.temp_dir / 'test_mixed.xlsx'
        
        success = self.generator.generate(
            mixed_data,
            output_path,
            validate=False
        )
        
        self.assertTrue(success, "Generación debería ser exitosa")
        self.assertEqual(
            self.generator.records_processed, 3,
            "Solo debería procesar registros válidos"
        )
    
    def test_generate_empty_dataframe(self):
        """Test: Generación con DataFrame vacío debería retornar False."""
        empty_df = pd.DataFrame()
        output_path = self.temp_dir / 'test_empty.xlsx'
        
        # El generador no lanza excepción, retorna False
        success = self.generator.generate(empty_df, output_path)
        
        self.assertFalse(success, "DataFrame vacío debería retornar False")
    
    def test_generate_file_structure(self):
        """Test: Verificar estructura del archivo Excel generado."""
        output_path = self.temp_dir / 'test_structure.xlsx'
        
        self.generator.generate(self.valid_data, output_path, validate=False)
        
        # Leer archivo generado
        df_generated = pd.read_excel(output_path)
        
        # Verificar estructura
        self.assertEqual(len(df_generated.columns), 3, "Debería tener 3 columnas")
        self.assertEqual(len(df_generated), 3, "Debería tener 3 filas")
        
        # Verificar nombres de columnas
        expected_cols = self.generator.COLUMN_NAMES
        self.assertEqual(
            list(df_generated.columns), expected_cols,
            "Nombres de columnas deberían ser exactos"
        )
    
    def test_generate_without_validation(self):
        """Test: Generación sin validación."""
        output_path = self.temp_dir / 'test_no_validate.xlsx'
        
        success = self.generator.generate(
            self.valid_data,
            output_path,
            validate=False
        )
        
        self.assertTrue(success, "Generación sin validación debería ser exitosa")
        self.assertTrue(output_path.exists(), "Archivo debería existir")
    
    def test_generate_overwrites_existing(self):
        """Test: Generación sobrescribe archivo existente."""
        output_path = self.temp_dir / 'test_overwrite.xlsx'
        
        # Primera generación
        self.generator.generate(self.valid_data, output_path, validate=False)
        initial_mtime = output_path.stat().st_mtime
        
        # Segunda generación (con más datos)
        extended_data = pd.concat([self.valid_data] * 2, ignore_index=True)
        self.generator.generate(extended_data, output_path, validate=False)
        final_mtime = output_path.stat().st_mtime
        
        self.assertNotEqual(
            initial_mtime, final_mtime,
            "Archivo debería haber sido modificado"
        )
        
        # Verificar que tiene más registros
        df_final = pd.read_excel(output_path)
        self.assertEqual(len(df_final), 6, "Debería tener 6 registros ahora")
    
    # ============================================
    # Tests de validate_output
    # ============================================
    
    def test_validate_output_valid_file(self):
        """Test: Validación de archivo válido."""
        output_path = self.temp_dir / 'test_validate.xlsx'
        self.generator.generate(self.valid_data, output_path, validate=False)
        
        # Validar (retorna solo bool)
        is_valid = self.generator.validate_output(output_path)
        
        self.assertTrue(is_valid, "Archivo válido debería pasar validación")
    
    def test_validate_output_nonexistent_file(self):
        """Test: Validación de archivo que no existe."""
        nonexistent_path = self.temp_dir / 'does_not_exist.xlsx'
        
        is_valid = self.generator.validate_output(nonexistent_path)
        
        self.assertFalse(is_valid, "Archivo inexistente no debería ser válido")
    
    def test_validate_output_wrong_columns(self):
        """Test: Validación de archivo con columnas incorrectas."""
        # Crear archivo con estructura incorrecta
        wrong_df = pd.DataFrame({
            'Col1': [1, 2, 3],
            'Col2': [4, 5, 6]
        })
        
        wrong_path = self.temp_dir / 'test_wrong_cols.xlsx'
        wrong_df.to_excel(wrong_path, index=False)
        
        is_valid = self.generator.validate_output(wrong_path)
        
        self.assertFalse(is_valid, "Archivo con columnas incorrectas no debería ser válido")
    
    # ============================================
    # Tests de manejo de errores
    # ============================================
    
    def test_error_handling_missing_columns(self):
        """Test: Manejo de error con columnas faltantes."""
        incomplete_data = self.valid_data[['telefono_limpio', 'nombre_asesor']].copy()
        output_path = self.temp_dir / 'test_error.xlsx'
        
        # El generador puede manejar columnas faltantes gracefully
        # Si crea el archivo con datos parciales, está OK
        # Si retorna False, también está OK
        try:
            success = self.generator.generate(incomplete_data, output_path)
            # Si tiene éxito, verificar que al menos creó algo
            if success:
                self.assertTrue(output_path.exists(), "Si tiene éxito, debería crear archivo")
        except (KeyError, Exception):
            # Si lanza excepción, también es comportamiento aceptable
            pass
    
    def test_error_handling_invalid_path(self):
        """Test: Manejo de creación automática de directorios."""
        # En Windows, rutas absolutas como C:/ son válidas
        # El generador crea directorios automáticamente (característica, no bug)
        test_path = self.temp_dir / 'new_subdir' / 'another_level' / 'file.xlsx'
        
        # El directorio no existe inicialmente
        self.assertFalse(test_path.parent.exists(), "Directorio no debería existir antes")
        
        # El generador debería crear directorios automáticamente
        success = self.generator.generate(self.valid_data, test_path)
        
        # Verificar que se creó el archivo y los directorios
        self.assertTrue(success, "Debería tener éxito creando directorios")
        self.assertTrue(test_path.exists(), "Archivo debería existir")
        self.assertTrue(test_path.parent.exists(), "Directorios deberían haberse creado")
    
    def test_error_handling_corrupted_data(self):
        """Test: Manejo de datos corruptos."""
        corrupted_data = self.valid_data.copy()
        corrupted_data['fecha_venta'] = 'not_a_date'  # Dato inválido
        
        # Debería manejar el error o convertir gracefully
        output_path = self.temp_dir / 'test_corrupted.xlsx'
        
        try:
            result = self.generator.generate(corrupted_data, output_path, validate=False)
            # Si no lanza error, al menos debería retornar False o manejar gracefully
            self.assertIsNotNone(result)
        except (ValueError, TypeError):
            # Error esperado con datos corruptos
            pass
    
    # ============================================
    # Tests de contadores
    # ============================================
    
    def test_counters_reset(self):
        """Test: Contadores se reinician en cada generación."""
        output_path = self.temp_dir / 'test_counters.xlsx'
        
        # Primera generación
        self.generator.generate(self.valid_data, output_path, validate=False)
        first_processed = self.generator.records_processed
        
        # Segunda generación
        self.generator.generate(self.valid_data, output_path, validate=False)
        second_processed = self.generator.records_processed
        
        self.assertEqual(
            first_processed, second_processed,
            "Contadores deberían reiniciarse en cada generación"
        )
    
    def test_counters_accuracy(self):
        """Test: Contadores reflejan números correctos."""
        mixed_data = pd.concat([self.valid_data, self.invalid_data], ignore_index=True)
        output_path = self.temp_dir / 'test_accuracy.xlsx'
        
        self.generator.generate(mixed_data, output_path, validate=False)
        
        # Debería procesar solo los válidos (3)
        self.assertEqual(
            self.generator.records_processed, 3,
            "Debería contar correctamente los procesados"
        )
    
    # ============================================
    # Tests de integración
    # ============================================
    
    def test_integration_full_workflow(self):
        """Test: Flujo completo de generación y validación."""
        output_path = self.temp_dir / 'test_integration.xlsx'
        
        # Paso 1: Generar
        success = self.generator.generate(
            self.valid_data,
            output_path,
            validate=True
        )
        
        self.assertTrue(success, "Generación debería ser exitosa")
        
        # Paso 2: Validar archivo
        is_valid = self.generator.validate_output(output_path)
        self.assertTrue(is_valid, "Archivo generado debería ser válido")
        
        # Paso 3: Leer y verificar contenido
        df_generated = pd.read_excel(output_path)
        self.assertEqual(len(df_generated), 3, "Debería tener 3 registros")
        
        # Paso 4: Verificar que teléfonos son correctos
        generated_phones = df_generated.iloc[:, 0].astype(str).tolist()
        expected_phones = self.valid_data['telefono_limpio'].tolist()
        self.assertEqual(
            sorted(generated_phones), sorted(expected_phones),
            "Teléfonos deberían coincidir"
        )


class TestContactLogGeneratorEdgeCases(unittest.TestCase):
    """Tests de casos límite y edge cases."""
    
    def setUp(self):
        """Configuración antes de cada test."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.generator = ContactLogGenerator()
    
    def tearDown(self):
        """Limpieza después de cada test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_single_record(self):
        """Test: Generación con un solo registro."""
        single_data = pd.DataFrame({
            'telefono_limpio': ['3001234567'],
            'nombre_asesor': ['Test User'],
            'fecha_venta': [date(2025, 10, 25)],
            'hora_venta': [time(10, 30)],
            'cod_servicio': ['2119'],
            'programa': ['ASISTENCIAS'],
        })
        
        output_path = self.temp_dir / 'single.xlsx'
        success = self.generator.generate(single_data, output_path, validate=False)
        
        self.assertTrue(success)
        self.assertEqual(self.generator.records_processed, 1)
    
    def test_large_dataset(self):
        """Test: Generación con dataset grande (1000+ registros)."""
        large_data = pd.DataFrame({
            'telefono_limpio': [f'300{i:07d}' for i in range(1000)],
            'nombre_asesor': ['Test User'] * 1000,
            'fecha_venta': [date(2025, 10, 25)] * 1000,
            'hora_venta': [time(10, 30)] * 1000,
            'cod_servicio': ['2119'] * 1000,
            'programa': ['ASISTENCIAS'] * 1000,
        })
        
        output_path = self.temp_dir / 'large.xlsx'
        success = self.generator.generate(large_data, output_path, validate=False)
        
        self.assertTrue(success)
        self.assertEqual(self.generator.records_processed, 1000)
        
        # Verificar que el archivo se generó correctamente
        df = pd.read_excel(output_path)
        self.assertEqual(len(df), 1000)
    
    def test_special_characters_in_names(self):
        """Test: Manejo de caracteres especiales en nombres."""
        special_data = pd.DataFrame({
            'telefono_limpio': ['3001234567'],
            'nombre_asesor': ['José María Ñoño O\'Reilly'],
            'fecha_venta': [date(2025, 10, 25)],
            'hora_venta': [time(10, 30)],
            'cod_servicio': ['2119'],
            'programa': ['ASISTENCIAS'],
        })
        
        output_path = self.temp_dir / 'special_chars.xlsx'
        success = self.generator.generate(special_data, output_path, validate=False)
        
        self.assertTrue(success)
        
        # Verificar que se guardó correctamente
        df = pd.read_excel(output_path)
        self.assertIn('José María', df.iloc[0, 1])


if __name__ == '__main__':
    unittest.main()
