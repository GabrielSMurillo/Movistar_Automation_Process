import pandas as pd

# Leer CSV original
df_csv = pd.read_csv("data/input/_TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv", encoding="utf-8-sig", decimal=",")
df_csv["Marca temporal"] = pd.to_datetime(df_csv["Marca temporal"], format="%d/%m/%Y %H:%M:%S")

# Filtrar por periodo
df_oct = df_csv[
    (df_csv["Marca temporal"] >= "2025-10-08") &
    (df_csv["Marca temporal"] <= "2025-10-22 23:59:59")
].copy()

col_tel = "TELEFONO DEL CLIENTE( DONDE SE VA CARGAR EL SERVICIO )"
df_oct[col_tel] = df_oct[col_tel].astype(str).str.strip()

print("=== REGISTROS EN CSV PARA 8-22 OCT ===")
print(f"Total en periodo: {len(df_oct)}")

# Contar por tipo de teléfono
df_oct["primer_digito"] = df_oct[col_tel].str[0]
df_oct["longitud"] = df_oct[col_tel].str.len()

print("\nPrimer dígito:")
print(df_oct["primer_digito"].value_counts())

# Móviles con 3
movil_3 = len(df_oct[(df_oct[col_tel].str.startswith("3")) & (df_oct["longitud"] == 10)])
# Móviles con 957
movil_957_raw = df_oct[df_oct[col_tel].str.startswith("957")]
movil_957 = len(movil_957_raw)

print(f"\n=== MÓVILES EN CSV ===")
print(f"Con 3 (10 dígitos): {movil_3}")
print(f"Con 957 (13 dígitos): {movil_957}")
print(f"Total MOVIL potenciales: {movil_3 + movil_957}")

# Ver BASE ASIGNADA
print(f"\n=== BASE ASIGNADA ===")
print(df_oct["BASE ASIGNADA"].value_counts())

# Filtrar solo MOVIL por base asignada
df_movil_base = df_oct[df_oct["BASE ASIGNADA"] == "MOVIL"]
print(f"\nRegistros con BASE ASIGNADA = MOVIL: {len(df_movil_base)}")

# Ver empaquetados
df_oct_sorted = df_oct.sort_values(["Marca temporal", col_tel])
print(f"\n=== ANÁLISIS DE EMPAQUETADOS ===")
duplicated_tel = df_oct.duplicated(subset=[col_tel], keep=False)
print(f"Teléfonos que aparecen más de una vez: {duplicated_tel.sum()} registros")

# Histórico
df_hist = pd.read_excel("data/input/historicos/CONSOLIDADOR/10.CARGA OCTUBRE/CARG. MOVIL/FORMATO MOVISTAR_MOVIL_8_Al_22_OCT_2025.xlsx")
df_hist["FECHA_ALTA"] = pd.to_datetime(df_hist["FECHA_ALTA"])
df_hist_filtrado = df_hist[
    (df_hist["FECHA_ALTA"] >= "2025-10-08") &
    (df_hist["FECHA_ALTA"] <= "2025-10-22 23:59:59")
]

print(f"\n=== RESUMEN COMPARATIVO ===")
print(f"CSV original (8-22 Oct): {len(df_oct)} registros")
print(f"  - BASE=MOVIL: {len(df_movil_base)} registros")
print(f"  - Teléfonos 3XX: {movil_3} registros")
print(f"  - Teléfonos 957: {movil_957} registros")
print(f"Histórico MOVIL (8-22 Oct): {len(df_hist_filtrado)} registros")
print(f"Generado ahora: 515 registros")
print(f"\nDiferencia CSV{}Generado: {len(df_oct) - 515}")
print(f"Diferencia Histórico{}Generado: {len(df_hist_filtrado) - 515}")
