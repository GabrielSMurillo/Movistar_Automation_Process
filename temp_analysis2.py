import pandas as pd

df = pd.read_csv("data/input/_TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv", encoding="utf-8-sig", decimal=",")
df["Marca temporal"] = pd.to_datetime(df["Marca temporal"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
df_oct = df[(df["Marca temporal"] >= "2025-10-08") & (df["Marca temporal"] <= "2025-10-22")].copy()

col_telefono = [c for c in df.columns if "TELEFONO DEL CLIENTE" in c and "CARGAR" in c][0]
df_oct["telefono_clean"] = df_oct[col_telefono].astype(str).str.strip()

print("=== ANÁLISIS DE TELÉFONOS QUE INICIAN CON 9 ===")
df_9 = df_oct[df_oct["telefono_clean"].str.startswith("9")]
print(f"Total con 9: {len(df_9)}")
print(f"\nPrimeros 10 ejemplos:")
print(df_9[col_telefono].head(10).tolist())

print(f"\n=== ANÁLISIS DE LONGITUDES ===")
df_oct["telefono_len"] = df_oct["telefono_clean"].str.len()
print(df_oct["telefono_len"].value_counts().sort_index())

print(f"\n=== TELÉFONOS CON 957 (satelital) ===")
df_957 = df_oct[df_oct["telefono_clean"].str.startswith("957")]
print(f"Total 957: {len(df_957)}")
print(f"Longitud de 957: {df_957['telefono_len'].value_counts()}")

print(f"\n=== RESUMEN ===")
print(f"Con 3 (10 dígitos): {len(df_oct[(df_oct['telefono_clean'].str.startswith('3')) & (df_oct['telefono_len'] == 10)])}")
print(f"Con 6 (10 dígitos): {len(df_oct[(df_oct['telefono_clean'].str.startswith('6')) & (df_oct['telefono_len'] == 10)])}")
print(f"Con 957 (13 dígitos): {len(df_oct[(df_oct['telefono_clean'].str.startswith('957')) & (df_oct['telefono_len'] == 13)])}")
print(f"\nTotal MOVIL (3XX o 957XXXXXXXXXX): {len(df_oct[(df_oct['telefono_clean'].str.startswith('3')) & (df_oct['telefono_len'] == 10)]) + len(df_oct[(df_oct['telefono_clean'].str.startswith('957')) & (df_oct['telefono_len'] == 13)])}")
