"""
Test rápido para verificar el fix de hora en Contact Log
"""
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.generators.contact_log_generator import ContactLogGenerator

# Crear datos de prueba
test_data = pd.DataFrame({
    'telefono_limpio': ['3001234567', '3012345678', '3021234567'],
    'nombre_asesor': ['Juan Pérez', 'María García', 'Pedro López'],
    'fecha_venta': ['2025-10-14', '2025-10-15', '2025-10-16'],
    'hora_venta': ['10:25:00 AM', '02:30:15 PM', '11:45:30 AM'],
    'hora_24h': ['10:25:00', '14:30:15', '11:45:30'],
    'cod_servicio': ['2119', '2120', '2121'],
    'duplicate_status': ['unico', 'unico', 'unico'],
    'estado': ['valido', 'valido', 'valido']
})

print("=" * 80)
print("[TEST] Verificando fix de hora en Contact Log")
print("=" * 80)

# Crear generador
generator = ContactLogGenerator()

# Generar archivo de prueba
output_path = Path('test_contact_log_fix.xlsx')
success = generator.generate(test_data, output_path, validate=False)

if success:
    print(f"\n[OK] Contact Log generado: {output_path}")
    
    # Leer y verificar
    df_result = pd.read_excel(output_path)
    print(f"\n[VERIFICACION] Primeras 3 filas - Campo Observacion:")
    obs_col = df_result.columns[1]
    for idx, val in df_result[obs_col].head(3).items():
        print(f"  {idx}: {val}")
    
    # Verificar que las horas estén completas
    all_obs = df_result[obs_col].tolist()
    issues = []
    for i, obs in enumerate(all_obs):
        if 'Hora de venta AM' in obs or 'Hora de venta PM' in obs:
            if 'Hora de venta AM Cliente' in obs or 'Hora de venta PM Cliente' in obs:
                issues.append(f"Fila {i}: Hora solo muestra AM/PM sin números")
    
    if issues:
        print(f"\n[ERROR] Se encontraron {len(issues)} problemas:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n[SUCCESS] Todas las horas se muestran correctamente!")
    
    # Limpiar
    output_path.unlink()
    print(f"\n[CLEANUP] Archivo de prueba eliminado")
    
else:
    print(f"\n[ERROR] Falló la generación del Contact Log")
    sys.exit(1)

print("\n" + "=" * 80)
print("[COMPLETE] Test finalizado")
print("=" * 80)
