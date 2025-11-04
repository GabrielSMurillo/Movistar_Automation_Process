# ✅ SISTEMA DE CARPETAS CON FECHA Y RANGO DE DATOS

## 📅 Cambio Implementado

He implementado un sistema que **automáticamente crea carpetas** con la fecha de generación y el rango de datos procesados.

---

## 📁 FORMATO DE CARPETA

### Ejemplo:
```
data/output/2024-11-04_Generado_Rango_23-10-2024_al_31-10-2024/
```

### Estructura del nombre:
```
YYYY-MM-DD_Generado_Rango_DD-MM-YYYY_al_DD-MM-YYYY
│          │              │                  │
│          │              │                  └─ Fecha fin de datos
│          │              └─ Fecha inicio de datos
│          └─ Texto descriptivo
└─ Fecha de ejecución del script
```

---

## 📅 CONFIGURACIÓN ACTUALIZADA

### Rango de datos procesados:
```python
START_DATE = 23 de octubre 2024
END_DATE   = 31 de octubre 2024 (inclusive)
```

✅ **El rango incluye ambos días** (23 y 31 de octubre)

---

## 🔧 ARCHIVOS MODIFICADOS

### 1. `config.py`
**Cambios realizados:**

✅ **Actualización de fechas:**
```python
START_DATE = date(2024, 10, 23)  # 23 de octubre 2024
END_DATE = date(2024, 10, 31)    # 31 de octubre 2024
```

✅ **Nueva función `create_output_folder_with_date()`:**
- Crea carpeta con formato: `YYYY-MM-DD_Generado_Rango_DD-MM-YYYY_al_DD-MM-YYYY`
- Usa fecha actual para "Generado"
- Usa START_DATE y END_DATE para "Rango"

✅ **Nueva función `get_output_dir()`:**
- Retorna la carpeta de salida con fecha
- Crea la carpeta si no existe
- Cachea el resultado para usar la misma carpeta en toda la ejecución

### 2. `main.py`
**Cambios realizados:**

✅ **Import de nueva función:**
```python
from config import get_output_dir
```

✅ **Creación de carpeta al inicio:**
```python
output_dir_with_date = get_output_dir()
```

✅ **Actualización de todos los usos de OUTPUT_DIR:**
- `generate_movistar_files()` → usa `output_dir_with_date`
- `generate_internal_files()` → usa `output_dir_with_date`
- `generate_monthly_report()` → usa `output_dir_with_date`
- `contact_log_path` → usa `output_dir_with_date`
- `novelty_tip_path` → usa `output_dir_with_date`
- `novelty_dig_path` → usa `output_dir_with_date`

✅ **Logs mejorados:**
```python
logger.info(f"📅 Periodo de datos: 23/10/2024 → 31/10/2024")
logger.info(f"📁 Carpeta de salida: 2024-11-04_Generado_Rango_23-10-2024_al_31-10-2024")
logger.info(f"📁 Ruta completa: C:\\...\\data\\output\\2024-11-04_Generado_Rango_23-10-2024_al_31-10-2024")
```

---

## 📊 EJEMPLO DE EJECUCIÓN

### Ejecución el 4 de noviembre de 2024:
```
📅 Periodo de datos: 23/10/2024 → 31/10/2024
📁 Carpeta de salida: 2024-11-04_Generado_Rango_23-10-2024_al_31-10-2024
⏰ Inicio de ejecución: 2024-11-04 15:30:00
```

### Archivos generados en:
```
data/output/2024-11-04_Generado_Rango_23-10-2024_al_31-10-2024/
├── OCTUBRE_23_Al_31_OCT_2024_ContactLog_Movistar.xlsx
├── OCTUBRE_23_Al_31_OCT_2024_FORMATO MOVISTAR.xlsx
├── OCTUBRE_23_Al_31_OCT_2024_SVAS_DIG.xlsx
├── OCTUBRE_23_Al_31_OCT_2024_SVAS_FIJA.xlsx
├── OCTUBRE_23_Al_31_OCT_2024_SVAS_MOV.xlsx
├── OCTUBRE_23_Al_31_OCT_2024_Exitosas_Movistar.xlsx
└── ... (otros archivos)
```

---

## 🎯 VENTAJAS DEL SISTEMA

### 1. **Trazabilidad**
- ✅ Sabes exactamente **cuándo** se generaron los archivos
- ✅ Sabes exactamente **qué rango de datos** contienen

### 2. **Organización**
- ✅ Cada ejecución tiene su propia carpeta
- ✅ No se sobreescriben archivos de ejecuciones anteriores
- ✅ Fácil comparar resultados de diferentes fechas

### 3. **Auditoría**
- ✅ Historial completo de generaciones
- ✅ Carpetas ordenadas por fecha (orden alfabético = orden cronológico)
- ✅ Identificación clara del contenido

### 4. **Día Vencido**
- ✅ Preparado para ejecuciones diarias
- ✅ Cada día tendrá su carpeta única
- ✅ Formato compatible con días hábiles

---

## 📝 CÓMO USAR

### Ejecución normal:
```bash
py main.py
```

El sistema automáticamente:
1. ✅ Crea la carpeta con fecha y rango
2. ✅ Procesa datos del 23 al 31 de octubre 2024
3. ✅ Guarda todos los archivos en la nueva carpeta
4. ✅ Muestra la ruta completa en los logs

### Cambiar el rango de fechas:
Edita `config.py`:
```python
START_DATE = date(2024, 11, 1)  # Nuevo rango
END_DATE = date(2024, 11, 5)
```

La próxima ejecución creará:
```
2024-11-04_Generado_Rango_01-11-2024_al_05-11-2024/
```

---

## 🔮 PARA IMPLEMENTAR DÍA VENCIDO

Para procesar automáticamente el día anterior cada día hábil:

### Opción 1: Script diario automático
```python
# En config.py, cambiar a:
from datetime import date, timedelta

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)

START_DATE = YESTERDAY
END_DATE = YESTERDAY
```

### Opción 2: Rango semanal (lunes a viernes)
```python
# Procesar toda la semana anterior
from datetime import date, timedelta

TODAY = date.today()
LAST_MONDAY = TODAY - timedelta(days=TODAY.weekday() + 7)
LAST_FRIDAY = LAST_MONDAY + timedelta(days=4)

START_DATE = LAST_MONDAY
END_DATE = LAST_FRIDAY
```

---

## 📋 RESUMEN

✅ **Implementado**: Sistema de carpetas con fecha de generación y rango de datos  
✅ **Configurado**: Rango del 23 al 31 de octubre 2024 (inclusive)  
✅ **Formato**: `YYYY-MM-DD_Generado_Rango_DD-MM-YYYY_al_DD-MM-YYYY`  
✅ **Automático**: Se crea al ejecutar `main.py`  
✅ **Flexible**: Fácil cambiar fechas en `config.py`  
✅ **Listo**: Para ejecuciones de día vencido

**El sistema está listo para usar. Cada ejecución generará su propia carpeta organizada.** 🎉
