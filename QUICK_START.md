# 🚀 QUICK START - Sistema Mejorado

**Fecha**: 3 de Noviembre 2025  
**Versión**: 2.0 (Sistema Profesional)

---

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Configurar variables de entorno

```bash
# Copiar template de configuración
copy .env.example .env

# Editar .env con tus fechas
# MOVISTAR_START_DATE=2025-10-23
# MOVISTAR_END_DATE=2025-10-31
```

### 2️⃣ Verificar que todo funciona

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar tests
python -m pytest tests/test_core_integration.py -v

# Resultado esperado: 12/12 tests passing ✅
```

### 3️⃣ Ejecutar el sistema

```bash
# Modo normal
python main.py

# Con logging detallado
python main.py --verbose

# Modo dry-run (no guarda archivos)
python main.py --dry-run
```

---

## 🆕 Nuevo Sistema vs Sistema Antiguo

### Sistema Nuevo (Recomendado)

**Configuración con .env:**
```bash
# .env
MOVISTAR_START_DATE=2025-10-23
MOVISTAR_END_DATE=2025-10-31
MOVISTAR_ENV=development
```

**Ventajas:**
- ✅ Validación automática de fechas
- ✅ Type safety completo
- ✅ Fácil cambio entre entornos
- ✅ No tocar código para cambiar config

### Sistema Antiguo (Todavía funciona)

**Configuración en config.py:**
```python
# config.py
START_DATE = date(2025, 10, 23)
END_DATE = YESTERDAY
```

**Nota:** Ambos sistemas funcionan, el sistema se adapta automáticamente.

---

## 📊 Verificar Estado del Sistema

### Ver configuración actual

```python
from src.core.config import get_settings

settings = get_settings()
print(f"Entorno: {settings.environment}")
print(f"Período: {settings.start_date} - {settings.end_date}")
print(f"Input: {settings.input_dir}")
print(f"Output: {settings.output_dir}")
```

### Ver métricas del último run

```python
from src.core.models import ProcessingMetrics

# Las métricas se guardan automáticamente
# Ver logs/ para detalles de ejecución
```

---

## 🛡️ Funcionalidades Nuevas

### 1. Retry Automático

Las funciones críticas se reintentan automáticamente:

```python
# En data_loader.py
@retry(max_attempts=3, delay=1.0)
def load_csv(file_path):
    # Si falla, se reintenta 3 veces automáticamente
    pass
```

### 2. Timing Automático

Todas las operaciones se miden:

```python
# En data_processor.py
@timing
def process(df):
    # Se mide el tiempo automáticamente
    # Resultados en logs
    pass
```

### 3. Validación Automática

Los datos se validan al crear objetos:

```python
from src.core.models import SaleRecord

# ✅ Válido
record = SaleRecord(
    telefono_servicio="3001234567",  # 10 dígitos, inicia con 3
    nombre_asesor="María López",      # Sin números
    # ...
)

# ❌ Inválido - levanta PhoneValidationError
record = SaleRecord(
    telefono_servicio="123",  # Muy corto!
    # ...
)
```

### 4. Excepciones Específicas

Los errores son más descriptivos:

```python
from src.core.exceptions import PhoneValidationError

try:
    # procesar datos
    pass
except PhoneValidationError as e:
    print(f"Teléfono inválido: {e.phone}")
    print(f"Razón: {e.reason}")
    print(f"Detalles: {e.details}")
```

---

## 📁 Estructura de Archivos

### Archivos de Entrada (data/input/)

```
data/input/
├── _TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv
└── Reporte de ventas digitales MOVISTAR - Sheet1.csv
```

### Archivos de Salida (data/output/)

El sistema genera automáticamente:

```
data/output/
├── Contact Log Movistar Asist_[FECHA].xlsx
├── FORMATO MOVISTAR_[FECHA].xlsx
├── SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG_[FECHA].xlsx
├── SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA_[FECHA].xlsx
├── SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_MOV_[FECHA].xlsx
├── FORMATO MOVISTAR_DIGITAL_[FECHA].xlsx
├── FORMATO MOVISTAR_FIJA_[FECHA].xlsx
├── FORMATO MOVISTAR_MOVIL_[FECHA].xlsx
└── [MES]_Exitosas_Movistar.xlsx
```

---

## 🧪 Testing

### Ejecutar todos los tests

```bash
# Tests básicos
pytest tests/ -v

# Tests con coverage
pytest tests/ --cov=src --cov-report=html

# Solo tests core
pytest tests/test_core_integration.py -v
```

### Resultado esperado

```
======================== 12 passed in 1.70s ========================
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pydantic'"

**Solución:**
```bash
pip install -r requirements.txt
```

### Error: "NameError: name 'TODAY' is not defined"

**Solución:**
- Ya está corregido en la versión actual
- Ejecuta `git pull` para obtener la última versión

### Error: "FileNotFoundError: data/input/..."

**Solución:**
```bash
# Crear directorios necesarios
mkdir -p data/input
mkdir -p data/output
mkdir -p data/historico

# O usar Python
python -c "from src.core.config import get_settings; get_settings().create_directories()"
```

### Sistema usa configuración antigua

**Solución:**
- Verifica que `.env` existe en la raíz
- Verifica que las variables empiezan con `MOVISTAR_`
- Ejecuta tests para verificar: `pytest tests/test_core_integration.py::TestCoreConfig -v`

---

## 📚 Documentación Completa

Para más detalles, consulta:

- **README.md**: Documentación completa del sistema
- **RESUMEN_MEJORAS_IMPLEMENTADAS.md**: Resumen ejecutivo de mejoras
- **REFACTORIZACION_PROFESIONAL.md**: Plan técnico detallado
- **GUIA_IMPLEMENTACION.md**: Guía paso a paso

---

## 💡 Consejos

### Para Desarrollo

1. **Usar .env para configuración**: No editar config.py
2. **Ejecutar tests antes de commit**: `pytest tests/ -v`
3. **Ver logs para debugging**: Revisar `logs/` después de cada ejecución
4. **Usar type hints**: El sistema espera tipos correctos

### Para Producción

1. **Configurar MOVISTAR_ENV=production** en .env
2. **Hacer backup** antes de procesamiento importante
3. **Verificar outputs** antes de enviar a Movistar
4. **Revisar logs** después de cada ejecución

---

## 🆘 Soporte

**Issues**: https://github.com/GabrielSMurillo/Movistar_Automation_Process/issues

**Documentación**: Ver archivos .md en el proyecto

**Tests**: Ejecutar `pytest tests/ -v` para diagnóstico

---

**Última actualización**: 3 de Noviembre 2025
