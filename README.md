# 🚀 Movistar Automation Process

Sistema automatizado de procesamiento, validación y consolidación de reportes de ventas para múltiples segmentos de negocio de Movistar (Digital, Fija, Móvil).

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características Principales](#-características-principales)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Estructura Detallada de Carpetas](#-estructura-detallada-de-carpetas)
- [Flujo de Datos](#-flujo-de-datos)
- [Módulos del Sistema](#-módulos-del-sistema)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Testing](#-testing)
- [Estructura de Datos](#-estructura-de-datos)
- [Áreas de Mejora](#-áreas-de-mejora)

---

## 🎯 Descripción General

Este proyecto automatiza el procesamiento completo de reportes de ventas de Movistar, realizando:

1. **Carga de datos** desde múltiples fuentes (CSV, Excel)
2. **Validación de calidad** de datos (formatos, valores nulos, tipos de datos)
3. **Detección y eliminación de duplicados** con seguimiento histórico
4. **Procesamiento por segmentos** (Digital, Fija, Móvil)
5. **Generación de reportes consolidados** por tipo de negocio
6. **Validación de outputs** contra reglas de negocio
7. **Generación de reportes de ejecución** con métricas y estadísticas

### Segmentos de Negocio Procesados

- **Digital**: Ventas de servicios digitales
- **Fija**: Telefonía fija e internet residencial
- **Móvil**: Planes de telefonía móvil

---

## ✨ Características Principales

- ✅ **Procesamiento automático** de múltiples archivos CSV
- ✅ **Detección inteligente de duplicados** con múltiples criterios
- ✅ **Validación exhaustiva** de datos de entrada y salida
- ✅ **Seguimiento histórico** de registros procesados
- ✅ **Generación de reportes** consolidados por segmento
- ✅ **Logging detallado** de todas las operaciones
- ✅ **Resumen de ejecución** con estadísticas y métricas
- ✅ **Manejo de errores** robusto
- ✅ **Tests unitarios** para componentes críticos

---

## 🏗️ Arquitectura del Proyecto

```
┌─────────────────┐
│  main.py        │  ← Punto de entrada
└────────┬────────┘
         │
         ├──► config.py (Configuración)
         │
         ├──► data_loader.py (Carga)
         │          │
         ├──► validators.py (Validación)
         │          │
         ├──► duplicate_tracker.py (Duplicados)
         │          │
         ├──► data_processor.py (Procesamiento)
         │          │
         ├──► file_generator.py (Generación)
         │          │
         ├──► output_validator.py (Validación Final)
         │          │
         └──► execution_summary.py (Reporte)
```

---

## 📁 Estructura Detallada de Carpetas

```
Movistar_Automation_Process/
│
├── 📂 src/                              # Código fuente principal
│   ├── __init__.py                      # Inicialización del paquete
│   ├── data_loader.py                   # Módulo de carga de datos
│   │   └── Funciones: load_csv(), load_excel(), validate_file_exists()
│   │
│   ├── data_processor.py                # Motor de procesamiento de datos
│   │   └── Funciones: process_segment(), clean_data(), transform_data()
│   │
│   ├── duplicate_tracker.py            # Sistema de detección de duplicados
│   │   └── Funciones: check_duplicates(), track_history(), remove_duplicates()
│   │
│   ├── eda.py                          # Análisis Exploratorio de Datos (EDA)
│   │   └── Funciones: generate_statistics(), create_visualizations(), data_profiling()
│   │
│   ├── file_generator.py               # Generador de archivos de salida
│   │   └── Funciones: generate_consolidated_report(), export_to_excel(), create_summary()
│   │
│   ├── output_validator.py             # Validador de archivos de salida
│   │   └── Funciones: validate_output_schema(), check_business_rules(), verify_totals()
│   │
│   ├── utils.py                        # Utilidades generales
│   │   └── Funciones: setup_logging(), get_timestamp(), format_dates()
│   │
│   └── validators.py                   # Validadores de datos de entrada
│       └── Funciones: validate_schema(), check_data_types(), validate_required_fields()
│
├── 📂 data/                             # Directorio de datos (NO incluido en Git)
│   │
│   ├── 📂 input/                        # Archivos de entrada sin procesar
│   │   ├── _TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv
│   │   │   └── Archivo principal con todas las ventas del mes actual
│   │   │       Columnas esperadas: [fecha, tipo_venta, segmento, cliente, monto, ...]
│   │   │
│   │   └── Reporte de ventas digitales MOVISTAR - Sheet1.csv
│   │       └── Reporte específico de ventas digitales
│   │           Columnas esperadas: [fecha, producto, cliente, canal, valor, ...]
│   │
│   └── 📂 historico/                    # Datos históricos procesados
│       │
│       ├── 📂 CONSOLIDADOR/             # Archivos consolidados por mes
│       │   │
│       │   ├── 📂 10.CARGA OCTUBRE/     # Datos consolidados de Octubre
│       │   │   ├── 📂 CARG. DIGITAL/    # Consolidado Digital Octubre
│       │   │   │   └── consolidado_digital_octubre_YYYY.xlsx
│       │   │   │
│       │   │   ├── 📂 CARG. FIJA/       # Consolidado Fija Octubre
│       │   │   │   └── consolidado_fija_octubre_YYYY.xlsx
│       │   │   │
│       │   │   └── 📂 CARG. MOVIL/      # Consolidado Móvil Octubre
│       │   │       └── consolidado_movil_octubre_YYYY.xlsx
│       │   │
│       │   └── 📂 9.CARGA SEPTIEMBRE/   # Datos consolidados de Septiembre
│       │       ├── 📂 CARG. DIGITAL/
│       │       ├── 📂 CARG. FIJA/
│       │       └── 📂 CARG. MOVIL/
│       │
│       └── 📂 REPORTEVENTAS_ENVIADO/    # Reportes enviados por mes
│           │
│           ├── 📂 OCT/                  # Reportes de Octubre
│           │   ├── 📂 ENV. DIGITAL/     # Reportes enviados - Digital
│           │   ├── 📂 ENV. FIJA/        # Reportes enviados - Fija
│           │   ├── 📂 ENV. MOVIL/       # Reportes enviados - Móvil
│           │   ├── 📂 ENVI. GENERAL/    # Reportes generales enviados
│           │   ├── 📂 ENVI. N.F DIGITAL/# No facturados - Digital
│           │   ├── 📂 ENVI. N.F FIJA/   # No facturados - Fija
│           │   └── 📂 ENVI. N.F MOVIL/  # No facturados - Móvil
│           │
│           └── 📂 SEPT/                 # Reportes de Septiembre
│               ├── 📂 ENV. DIGITAL/
│               ├── 📂 ENV. FIJA/
│               ├── 📂 ENV. MOVIL/
│               ├── 📂 ENVI. GENERAL/
│               ├── 📂 ENVI. N.F DIGITAL/
│               ├── 📂 ENVI. N.F FIJA/
│               └── 📂 ENVI. N.F MOVIL/
│
├── 📂 tests/                            # Suite de tests
│   ├── test_processors.py              # Tests para procesadores
│   └── test_validators.py              # Tests para validadores
│
├── 📄 main.py                           # Punto de entrada principal
├── 📄 config.py                         # Configuración centralizada
├── 📄 execution_summary.py              # Generador de resúmenes de ejecución
├── 📄 requirements.txt                  # Dependencias del proyecto
├── 📄 .gitignore                        # Archivos excluidos de Git
└── 📄 README.md                         # Este archivo

```

---

## 🔄 Flujo de Datos

```
1. ENTRADA (data/input/)
   │
   ├─► _TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv
   └─► Reporte de ventas digitales MOVISTAR - Sheet1.csv
   │
   ↓
2. VALIDACIÓN (validators.py)
   │
   ├─► Validar esquema de columnas
   ├─► Verificar tipos de datos
   ├─► Detectar valores nulos
   └─► Verificar rangos de fechas
   │
   ↓
3. DETECCIÓN DE DUPLICADOS (duplicate_tracker.py)
   │
   ├─► Comparar con histórico
   ├─► Identificar registros duplicados
   └─► Marcar para exclusión
   │
   ↓
4. PROCESAMIENTO (data_processor.py)
   │
   ├─► Limpiar datos
   ├─► Transformar formatos
   ├─► Calcular campos derivados
   └─► Segmentar por tipo (Digital/Fija/Móvil)
   │
   ↓
5. GENERACIÓN (file_generator.py)
   │
   ├─► Crear archivos consolidados por segmento
   ├─► Exportar a Excel
   └─► Generar reportes auxiliares
   │
   ↓
6. VALIDACIÓN DE SALIDA (output_validator.py)
   │
   ├─► Verificar integridad de datos
   ├─► Validar reglas de negocio
   └─► Confirmar totales
   │
   ↓
7. ALMACENAMIENTO (data/historico/)
   │
   ├─► CONSOLIDADOR/[MES]/CARG.[SEGMENTO]/
   └─► REPORTEVENTAS_ENVIADO/[MES]/ENV.[SEGMENTO]/
   │
   ↓
8. RESUMEN DE EJECUCIÓN (execution_summary.py)
   │
   ├─► Registros procesados
   ├─► Duplicados detectados
   ├─► Errores encontrados
   └─► Tiempo de ejecución
```

---

## 🧩 Módulos del Sistema

### 1️⃣ **main.py** - Orquestador Principal
- Inicializa la aplicación
- Coordina el flujo de ejecución
- Maneja excepciones globales
- Genera logs de ejecución

### 2️⃣ **config.py** - Configuración Centralizada
```python
# Rutas de archivos
INPUT_PATH = "data/input/"
OUTPUT_PATH = "data/historico/CONSOLIDADOR/"
HISTORIC_PATH = "data/historico/REPORTEVENTAS_ENVIADO/"

# Parámetros de procesamiento
SEGMENTOS = ["DIGITAL", "FIJA", "MOVIL"]
FECHA_CORTE = "2024-10-31"

# Validaciones
REQUIRED_COLUMNS = [...]
DATA_TYPES = {...}
```

### 3️⃣ **data_loader.py** - Carga de Datos
- Carga archivos CSV y Excel
- Valida existencia de archivos
- Maneja diferentes encodings
- Detecta delimitadores automáticamente

### 4️⃣ **validators.py** - Validación de Entrada
- Valida esquemas de datos
- Verifica tipos de datos
- Detecta valores faltantes
- Valida rangos y formatos

### 5️⃣ **duplicate_tracker.py** - Gestión de Duplicados
- Compara registros con histórico
- Múltiples criterios de duplicación
- Tracking de duplicados por período
- Generación de reportes de duplicados

### 6️⃣ **data_processor.py** - Procesamiento de Datos
- Limpieza de datos
- Transformaciones de negocio
- Cálculos derivados
- Segmentación por tipo

### 7️⃣ **file_generator.py** - Generación de Reportes
- Genera archivos consolidados
- Exporta a múltiples formatos
- Aplica formateo condicional
- Crea hojas de cálculo estructuradas

### 8️⃣ **output_validator.py** - Validación de Salida
- Verifica integridad de archivos generados
- Valida reglas de negocio
- Comprueba consistencia de totales
- Genera alertas de calidad

### 9️⃣ **execution_summary.py** - Reporte de Ejecución
- Estadísticas de procesamiento
- Métricas de calidad
- Tiempo de ejecución
- Logs detallados

### 🔟 **utils.py** - Utilidades
- Funciones de logging
- Manejo de fechas
- Formateo de datos
- Helpers generales

---

## 💻 Requisitos del Sistema

### Software Requerido
- **Python**: 3.8 o superior
- **pip**: Gestor de paquetes de Python
- **Git**: Para control de versiones

### Dependencias de Python (requirements.txt)
```
pandas>=1.5.0          # Manipulación de datos
numpy>=1.23.0          # Operaciones numéricas
openpyxl>=3.0.0        # Lectura/escritura Excel
xlrd>=2.0.0            # Lectura de archivos XLS
python-dateutil>=2.8.0 # Manejo de fechas
pytest>=7.0.0          # Testing
pytest-cov>=4.0.0      # Cobertura de tests
```

### Requisitos de Sistema
- **RAM**: Mínimo 4GB (recomendado 8GB para archivos grandes)
- **Disco**: 500MB libres para datos históricos
- **OS**: Windows 10+, Linux, macOS

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/GabrielSMurillo/Movistar_Automation_Process.git
cd Movistar_Automation_Process
```

### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar instalación

```bash
python -c "import pandas; import numpy; print('✅ Instalación exitosa')"
```

---

## ⚙️ Configuración

### 1. Configurar rutas en `config.py`

```python
# Ajustar según tu estructura de carpetas
INPUT_PATH = "data/input/"
OUTPUT_PATH = "data/historico/CONSOLIDADOR/"
HISTORIC_PATH = "data/historico/REPORTEVENTAS_ENVIADO/"
```

### 2. Preparar archivos de entrada

Colocar en `data/input/`:
- `_TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv`
- `Reporte de ventas digitales MOVISTAR - Sheet1.csv`

### 3. Crear estructura de carpetas (si no existe)

```bash
mkdir -p data/input
mkdir -p data/historico/CONSOLIDADOR
mkdir -p data/historico/REPORTEVENTAS_ENVIADO
```

---

## 🚀 Uso

### Ejecución Básica

```bash
python main.py
```

### Ejecución con Logging Detallado

```bash
python main.py --verbose
```

### Procesar Solo un Segmento

```bash
python main.py --segment DIGITAL
```

### Modo de Prueba (Sin Guardar)

```bash
python main.py --dry-run
```

---

## 🧪 Testing

### Ejecutar todos los tests

```bash
pytest tests/
```

### Ejecutar tests con cobertura

```bash
pytest --cov=src tests/
```

### Ejecutar tests específicos

```bash
pytest tests/test_validators.py
pytest tests/test_processors.py
```

### Ver reporte de cobertura

```bash
pytest --cov=src --cov-report=html tests/
```

---

## 📊 Estructura de Datos

### Archivo de Entrada: _TIPIFICADOR DE VENTAS GENERAL

**Columnas Esperadas:**
```
- FECHA_VENTA (datetime)
- TIPO_VENTA (string): "NUEVA" | "RENOVACION" | "UPGRADE"
- SEGMENTO (string): "DIGITAL" | "FIJA" | "MOVIL"
- CLIENTE_ID (string)
- CLIENTE_NOMBRE (string)
- DOCUMENTO (string)
- PRODUCTO (string)
- PLAN (string)
- VALOR_VENTA (float)
- CANAL (string)
- VENDEDOR (string)
- ESTADO (string): "ACTIVO" | "PENDIENTE" | "CANCELADO"
```

### Archivo de Entrada: Reporte de Ventas Digitales

**Columnas Esperadas:**
```
- FECHA (datetime)
- PRODUCTO_DIGITAL (string)
- CLIENTE (string)
- CANAL_DIGITAL (string)
- VALOR (float)
- TIPO_SERVICIO (string)
- ESTADO_FACTURACION (string): "FACTURADO" | "NO_FACTURADO"
```

### Archivos de Salida: Consolidados

**Estructura de Excel:**
- **Hoja 1**: Datos consolidados
- **Hoja 2**: Estadísticas
- **Hoja 3**: Duplicados detectados
- **Hoja 4**: Registros excluidos

---

## 🎯 Áreas de Mejora

### 🔴 Alta Prioridad

1. **Optimización de Performance**
   - Procesamiento en paralelo de segmentos
   - Uso de chunks para archivos grandes (>100MB)
   - Implementar caché para datos históricos

2. **Manejo de Errores**
   - Implementar retry logic para operaciones críticas
   - Sistema de rollback en caso de fallos
   - Notificaciones por email en errores

3. **Validaciones**
   - Agregar más reglas de negocio específicas
   - Validación cruzada entre segmentos
   - Detección de anomalías en datos

### 🟡 Media Prioridad

4. **Documentación del Código**
   - Agregar docstrings a todas las funciones
   - Documentar algoritmos de detección de duplicados
   - Crear diagramas de flujo

5. **Testing**
   - Aumentar cobertura de tests a >80%
   - Agregar tests de integración
   - Tests de performance con datos grandes

6. **Configuración**
   - Migrar a archivo YAML/JSON
   - Variables de entorno para datos sensibles
   - Perfiles de configuración (dev/prod)

### 🟢 Baja Prioridad

7. **Interfaz de Usuario**
   - Dashboard web para monitoreo
   - Visualizaciones interactivas
   - Sistema de reportes automatizado

8. **Automatización**
   - Scheduler para ejecuciones automáticas
   - Integración con sistemas externos (APIs)
   - Alertas automáticas

9. **Exportación**
   - Soporte para más formatos (Parquet, JSON)
   - Integración con bases de datos
   - API REST para consultas

---

## 🤝 Contribución

### Flujo de Trabajo Git

```bash
# 1. Crear rama para nueva funcionalidad
git checkout -b feature/nombre-funcionalidad

# 2. Hacer cambios y commits
git add .
git commit -m "feat: descripción del cambio"

# 3. Sincronizar con main
git pull origin main

# 4. Subir cambios
git push origin feature/nombre-funcionalidad

# 5. Crear Pull Request en GitHub
```

### Convención de Commits

```
feat: Nueva funcionalidad
fix: Corrección de bug
docs: Cambios en documentación
style: Formato, sin cambios en lógica
refactor: Refactorización de código
test: Agregar o modificar tests
chore: Tareas de mantenimiento
```

---

## 📝 Licencia

Este proyecto es **privado** y de uso interno exclusivo.

---

## 👤 Autor

**Gabriel S. Murillo**
- GitHub: [@GabrielSMurillo](https://github.com/GabrielSMurillo)
- Proyecto: Movistar Automation Process

---

## 📞 Soporte

Para reportar bugs o sugerir mejoras, crear un Issue en GitHub:
https://github.com/GabrielSMurillo/Movistar_Automation_Process/issues

---

**Última actualización**: Noviembre 2025
