#!/usr/bin/env python3
"""
Script de prueba rápida de los Input Adapters.
"""

from pathlib import Path
from src.adapters import InputAdapterFactory, read_file, get_file_info

# Probar con un CSV histórico
csv_path = Path("data/historico/CONSOLIDADOR/9.CARGA SEPTIEMBRE/csv_converted/SEPTIEMBRE_Exitosas_Movistar_CARG MOVIL.csv")

print("=" * 80)
print("🧪 TEST DE INPUT ADAPTERS")
print("=" * 80)

if csv_path.exists():
    print(f"\n📄 Probando CSVAdapter con: {csv_path.name}")
    
    # Método 1: Usar factory
    adapter = InputAdapterFactory.create(csv_path)
    print(f"   Adapter creado: {adapter}")
    
    # Leer datos
    df = adapter.read()
    print(f"   ✅ Datos leídos: {len(df)} filas, {len(df.columns)} columnas")
    
    # Información del archivo
    info = adapter.get_file_info()
    print(f"\n📊 Información del archivo:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Método 2: Función de conveniencia
    print(f"\n🔧 Probando función read_file()...")
    df2 = read_file(csv_path)
    print(f"   ✅ Datos leídos: {len(df2)} filas, {len(df2.columns)} columnas")
    
    print("\n✅ Todos los tests de CSV pasaron")
else:
    print(f"\n⚠️  Archivo de prueba no encontrado: {csv_path}")

# Buscar un archivo Excel de prueba (Contact Log)
excel_path = Path("data/historico/CONTACT LOG/OCT/Contact Log Movistar Asist_8_Al_22_OCT_2025.xlsx")

if excel_path.exists():
    print(f"\n📊 Probando ExcelAdapter con: {excel_path.name}")
    
    # Usar factory
    adapter = InputAdapterFactory.create(excel_path)
    print(f"   Adapter creado: {adapter}")
    
    # Listar hojas
    if hasattr(adapter, 'list_sheets'):
        sheets = adapter.list_sheets()
        print(f"   Hojas disponibles: {sheets}")
    
    # Leer datos
    df = adapter.read()
    print(f"   ✅ Datos leídos: {len(df)} filas, {len(df.columns)} columnas")
    print(f"   Columnas: {list(df.columns)}")
    
    # Información del archivo
    info = adapter.get_file_info()
    print(f"\n📊 Información del archivo:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Todos los tests de Excel pasaron")
else:
    print(f"\n⚠️  Archivo Excel de prueba no encontrado: {excel_path}")

print("\n" + "=" * 80)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 80)
