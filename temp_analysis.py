import pandas as pd

df = pd.read_csv("data/input/_TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv", encoding="utf-8-sig", decimal=",")
print(f"Total registros: {len(df)}")

df["Marca temporal"] = pd.to_datetime(df["Marca temporal"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
df_oct = df[(df["Marca temporal"] >= "2025-10-08") & (df["Marca temporal"] <= "2025-10-22")]
print(f"Registros entre 8-22 Oct: {len(df_oct)}")

col_telefono = [c for c in df.columns if "TELEFONO DEL CLIENTE" in c and "CARGAR" in c][0]
print(f"\nColumna teléfono: '{col_telefono}'")

df_oct["telefono_clean"] = df_oct[col_telefono].astype(str).str.strip()
df_oct["primer_digito"] = df_oct["telefono_clean"].str[0]

print(f"\n=== Distribribución por primer dígito ===")
print(df_oct["primer_digito"].value_counts())

df_oct_movil = df_oct[df_oct["telefono_clean"].str.startswith("3") & (df_oct["telefono_clean"].str.len() == 10)]
print(f"\n=== MOVIL (3XX, 10 dígitos) ===")
print(f"Registros MOVIL válidos: {len(df_oct_movil)}")

df_oct_fija = df_oct[df_oct["telefono_clean"].str.startswith("6") & (df_oct["telefono_clean"].str.len() == 10)]
print(f"\n=== FIJA (6XX, 10 dígitos) ===")
print(f"Registros FIJA válidos: {len(df_oct_fija)}")

print(f"\n=== COMPARACIÓN CON HISTÓRICO ===")
print(f"Histórico MOVIL 8-22 Oct: 597 registros")
print(f"CSV actual MOVIL 8-22 Oct: {len(df_oct_movil)} registros")
print(f"Diferencia: {597 - len(df_oct_movil)} registros")
