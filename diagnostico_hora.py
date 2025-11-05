"""
Script de diagnóstico para verificar columnas de hora en archivos de salida
"""
import pandas as pd
from pathlib import Path

# Buscar archivos recientes
output_dir = Path('data/output')
output_dirs = sorted(output_dir.glob('output_*'), reverse=True)

if not output_dirs:
    print("[ERROR] No se encontraron carpetas de output")
    exit(1)

latest_dir = output_dirs[0]
print(f"[INFO] Revisando: {latest_dir}")
print("-" * 80)

# Buscar Contact Log
contact_log_files = list(latest_dir.glob('*Contact*Log*.xlsx'))
exitosas_files = list(latest_dir.glob('*Exitosas*.xlsx'))

if contact_log_files:
    print("\n[CONTACT LOG]")
    for file in contact_log_files:
        print(f"  Archivo: {file.name}")
        df = pd.read_excel(file)
        print(f"  Registros: {len(df)}")
        print(f"  Columnas: {list(df.columns)}")
        if len(df) > 0:
            print(f"\n  Primeras 3 filas de 'Campo Observacion':")
            obs_col = df.columns[1]
            for idx, val in df[obs_col].head(3).items():
                print(f"    {idx}: {val}")

if exitosas_files:
    print(f"\n[ARCHIVO EXITOSAS - VERIFICACIÓN DE COLUMNAS]")
    file = exitosas_files[0]
    print(f"  Archivo: {file.name}")
    
    # Leer todas las hojas
    excel_file = pd.ExcelFile(file)
    print(f"  Hojas: {excel_file.sheet_names}")
    
    # Verificar primera hoja
    df = pd.read_excel(file, sheet_name=0)
    print(f"\n  Columnas en hoja '{excel_file.sheet_names[0]}':")
    for col in df.columns:
        print(f"    - {col}")
    
    # Verificar si existen columnas de hora
    hora_cols = [col for col in df.columns if 'hora' in col.lower()]
    if hora_cols:
        print(f"\n  Columnas de HORA encontradas: {hora_cols}")
        print(f"\n  Muestra de datos (primeras 5 filas):")
        sample_cols = ['telefono_servicio', 'fecha_venta'] + hora_cols
        sample_cols = [c for c in sample_cols if c in df.columns]
        print(df[sample_cols].head())
    else:
        print("\n  [WARNING] No se encontraron columnas de hora!")
        print(f"\n  Columnas disponibles relacionadas con fecha:")
        date_cols = [col for col in df.columns if any(word in col.lower() for word in ['fecha', 'date', 'time'])]
        print(f"    {date_cols}")

print("\n" + "=" * 80)
print("[COMPLETE] Diagnóstico finalizado")
