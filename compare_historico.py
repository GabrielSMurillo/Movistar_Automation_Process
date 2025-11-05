import pandas as pd
from datetime import datetime

# Leer histórico
df_historico = pd.read_excel('data/input/historicos/CONSOLIDADOR/10.CARGA OCTUBRE/CARG. MOVIL/FORMATO MOVISTAR_MOVIL_8_Al_22_OCT_2025.xlsx')

print(f"=== ANÁLISIS DEL HISTÓRICO MOVIL ===")
print(f"Total registros: {len(df_historico)}")

# Analizar fechas
df_historico['FECHA_ALTA'] = pd.to_datetime(df_historico['FECHA_ALTA'])
print(f"\nFechas en el histórico:")
print(f"  Primera: {df_historico['FECHA_ALTA'].min()}")
print(f"  Última: {df_historico['FECHA_ALTA'].max()}")

# Filtrar por periodo 8-22
df_periodo = df_historico[
    (df_historico['FECHA_ALTA'] >= '2025-10-08') &
    (df_historico['FECHA_ALTA'] <= '2025-10-22')
]
print(f"\nRegistros entre 8-22 Oct: {len(df_periodo)}")

# Ver distribución por día
print(f"\nDistribución por día:")
print(df_periodo['FECHA_ALTA'].dt.date.value_counts().sort_index())

# Analizar teléfonos
print(f"\n=== ANÁLISIS DE TELÉFONOS ===")
col_tel = 'NUM. CELULAR'
df_periodo[col_tel] = df_periodo[col_tel].astype(str).str.strip()
df_periodo['primer_digito'] = df_periodo[col_tel].str[0]
df_periodo['longitud'] = df_periodo[col_tel].str.len()

print("\nPrimer dígito:")
print(df_periodo['primer_digito'].value_counts())

print("\nLongitud:")
print(df_periodo['longitud'].value_counts())

# Contar por tipo
print(f"\n=== TIPOS DE TELÉFONO ===")
tels_3 = len(df_periodo[df_periodo[col_tel].str.startswith('3') & (df_periodo['longitud'] == 10)])
tels_957 = len(df_periodo[df_periodo[col_tel].str.startswith('957') & (df_periodo['longitud'] == 13)])
print(f"3XX (10 dígitos): {tels_3}")
print(f"957XXXXXXXXXX (13 dígitos): {tels_957}")
print(f"Total MOVIL: {tels_3 + tels_957}")

# Leer lo que generamos
df_generado = pd.read_excel('data/output/2025-11-04_Ejecutado_Periodo_08-10-2025_al_22-10-2025/FORMATO MOVISTAR_MOVIL_08_Al_22_OCT_2025.xlsx')
print(f"\n=== COMPARACIÓN ===")
print(f"Histórico (8-22 Oct): {len(df_periodo)} registros")
print(f"Generado ahora: {len(df_generado)} registros")
print(f"Diferencia: {len(df_periodo) - len(df_generado)} registros")
