# 🚀 Movistar Automation Process

**Sistema Automatizado de Procesamiento y Generación de Archivos de Ventas para Movistar**

Sistema profesional de procesamiento ETL (Extract, Transform, Load) que automatiza la validación, transformación y generación de archivos de ventas para Movistar. Incluye detección de duplicados, validaciones exhaustivas, análisis exploratorio de datos (EDA), y generación de reportes consolidados con trazabilidad completa.

**Estado:** ✅ **PRODUCCIÓN** | **Versión:** 2.0 | **Última Actualización:** 4 Noviembre 2025

---

---

## 📋 Tabla de Contenidos

- [🎯 Descripción General](#-descripción-general)
- [✨ Características Principales](#-características-principales)
- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
- [📦 Requisitos](#-requisitos)
- [🔧 Instalación](#-instalación)
- [⚙️ Configuración](#️-configuración)
- [🎮 Uso del Sistema](#-uso-del-sistema)
- [🔄 Pipeline de Procesamiento](#-pipeline-de-procesamiento)
- [📄 Archivos Generados](#-archivos-generados)
- [✅ Validaciones Implementadas](#-validaciones-implementadas)
- [📋 Archivo de NOVEDADES](#-archivo-de-novedades)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [📊 Logs y Reportes](#-logs-y-reportes)
- [🔍 Solución de Problemas](#-solución-de-problemas)
- [🎯 Mejoras Implementadas](#-mejoras-implementadas)
- [🧪 Testing](#-testing)

---

## 🚀 Inicio Rápido

### Ejecución en 5 Pasos

```powershell
# 1️⃣ Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2️⃣ Configurar fechas en .env (o dejar vacío para mes anterior automático)
# MOVISTAR_START_DATE=2025-10-01
# MOVISTAR_END_DATE=2025-10-31

# 3️⃣ Colocar archivos CSV en data/input/
# - _TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv
# - Reporte de ventas digitales MOVISTAR - Sheet1.csv

# 4️⃣ Ejecutar pipeline
python main.py

# 5️⃣ Ver resultados
# data/output/YYYY-MM-DD_Ejecutado_Periodo_DD-MM-YYYY_al_DD-MM-YYYY/
```

**⏱️ Tiempo de procesamiento:** ~9 segundos para 3,700+ registros  
**📁 Archivos generados:** 9-11 archivos Excel  
**✅ Tasa de éxito:** 99.7% de ventas procesadas correctamente

---

## 🎯 Descripción General

**Movistar Automation Process** es un sistema ETL (Extract, Transform, Load) profesional que automatiza completamente el ciclo de procesamiento de ventas de Movistar. Diseñado con arquitectura modular, validaciones exhaustivas y manejo robusto de errores.

### 🎬 ¿Qué Hace el Sistema?

```
📥 ENTRADA
└─ Archivos CSV desde Google Sheets (Tipificador + Ventas Digitales)

⚙️ PROCESAMIENTO
├─ Validación de teléfonos (10 dígitos, prefijos válidos)
├─ Validación de asesores y logins
├─ Detección de duplicados con histórico
├─ Clasificación por tipo de línea (MOVIL/FIJA/DIGITAL)
├─ Mapeo de códigos de servicio
├─ Identificación de empaquetados y referidos
└─ Captura de registros inválidos

📤 SALIDA
├─ 9-11 archivos Excel en carpeta organizada por fecha
├─ Contact Log para Movistar
├─ Archivos SVAS por tipo de línea
├─ Formatos internos segmentados
├─ Reporte mensual consolidado
├─ Archivo de NOVEDADES (registros rechazados)
└─ Reportes de validación y EDA

🗂️ ORGANIZACIÓN
└─ data/output/2025-11-04_Ejecutado_Periodo_23-10-2025_al_31-10-2025/
    ├─ Contact Log Movistar Asist_23_Al_31_OCT_2025.xlsx
    ├─ FORMATO MOVISTAR_23_Al_31_OCT_2025.xlsx
    ├─ SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG_23_A_31_OCT.xlsx
    ├─ SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA_23_A_31_OCT.xlsx
    ├─ FORMATO MOVISTAR_DIGITAL_23_Al_31_OCT_2025.xlsx
    ├─ FORMATO MOVISTAR_FIJA_23_Al_31_OCT_2025.xlsx
    ├─ FORMATO MOVISTAR_MOVIL_23_Al_31_OCT_2025.xlsx
    ├─ OCTUBRE_Exitosas_Movistar.xlsx
    └─ NOVEDADES_23_Al_31_OCT_2025.xlsx
```

### 🎭 Casos de Uso Principales

1. **Procesamiento Mensual Automático**
   - Ejecutar día 1 de cada mes → Procesa todo el mes anterior
   - Sin configuración manual de fechas
   - Carpetas organizadas con fecha de ejecución + periodo

2. **Procesamiento de Periodo Específico**
   - Configurar fechas en `.env`
   - Generar archivos para rangos personalizados
   - Útil para correcciones o reprocesos

3. **Control de Calidad**
   - Revisar archivo NOVEDADES
   - Identificar y corregir registros rechazados
   - Reprocesar después de correcciones

4. **Análisis de Datos**
   - EDA automático con estadísticas
   - Reportes de calidad de datos
   - Métricas de validación ETL

### 📊 Estadísticas del Sistema

```
📈 Rendimiento
├─ Velocidad: 3,700+ registros en ~9 segundos
├─ Precisión: 99.7% de ventas válidas procesadas
├─ Archivos: 9-11 archivos Excel generados
└─ Tamaño: 50-100 KB total

🎯 Validaciones
├─ Teléfonos: 10 dígitos, prefijos válidos (3XX o 6X)
├─ Duplicados: Detección contra histórico
├─ Asesores: Validación de nombres y logins
└─ Fechas: Verificación de rangos y formatos

📦 Procesamiento Típico
├─ Enero 2025 (1-31): 166 ventas procesadas
├─ Octubre 2025 (8-22): 554 ventas procesadas
├─ Octubre 2025 (23-31): 365 ventas procesadas
└─ Registros rechazados: ~12 por ejecución (0.3%)
```

---

## ✨ Características Principales

### � Funcionalidades Core

#### 1. **Procesamiento Automatizado de Ventas**

- ✅ Carga automática desde CSV (Google Sheets)
- ✅ Validación de teléfonos con prefijos colombianos (móvil y fijo)
- ✅ Detección de duplicados contra histórico
- ✅ Identificación de ventas empaquetadas (múltiples productos, mismo cliente)
- ✅ Separación de referidos

#### 2. **Generación de Múltiples Formatos**

- ✅ **Contact Log** para Movistar
- ✅ **FORMATO MOVISTAR** (general)
- ✅ **Archivos SVAS** por tipo de línea (DIG, FIJA, MOV)
- ✅ **Formatos internos** segmentados por tipo
- ✅ **Reporte mensual** consolidado
- ✅ **Archivo de NOVEDADES** para registros rechazados ⭐ **NUEVO**

#### 3. **Validaciones Exhaustivas**

```python
Validación de Teléfonos:
✓ 10 dígitos exactos
✓ Móviles: Prefijos 300-350 (inician con 3)
✓ Fijos: Indicativos de ciudad (inician con 6)
✓ Especial: 957 (satelital)
✗ Rechazados: 333, longitud incorrecta, prefijos inválidos

Validación de Datos:
✓ Mapeo de códigos de servicio por tipo de línea
✓ Validación de fechas y marcas temporales
✓ Detección de registros incompletos
✓ ETL Validator con reportes detallados

Estadísticas Típicas:
├─ Total: 3,701 teléfonos
├─ Válidos: 3,689 (99.7%)
└─ Inválidos: 12 (0.3%)
```

#### 4. **Organización Inteligente** ⭐ **NUEVO**

```
📁 Carpetas Organizadas por Fecha
Formato: YYYY-MM-DD_Ejecutado_Periodo_DD-MM-YYYY_al_DD-MM-YYYY

Ejemplo:
2025-11-04_Ejecutado_Periodo_23-10-2025_al_31-10-2025/

Ventajas:
✅ Trazabilidad completa
✅ Historial de ejecuciones preservado
✅ Fácil identificación de periodo procesado
✅ No más sobreescritura accidental de archivos
```

#### 5. **Ejecución a Día Vencido** ⭐ **NUEVO**

```python
# Sin configurar fechas en .env
# El sistema automáticamente procesa el mes anterior completo

Ejecutado el 1 de febrero → Procesa 1 al 31 de enero
Ejecutado el 1 de marzo   → Procesa 1 al 28/29 de febrero
Ejecutado el 1 de noviembre → Procesa 1 al 31 de octubre

# Ideal para automatización con Task Scheduler
```

#### 6. **Análisis y Reportes**

- ✅ **EDA** (Exploratory Data Analysis) automático
- ✅ Reportes de calidad de datos
- ✅ Estadísticas de procesamiento
- ✅ Logs detallados de cada ejecución
- ✅ Métricas de validación ETL

### 🎭 Segmentos de Negocio

| Segmento | Primer Dígito | Dígitos Totales | Ejemplos |
|----------|---------------|-----------------|----------|
| **📱 MOVIL** | 3 | 10 | 3001234567, 3152345678, 3209876543 |
| **📞 FIJA** | 6 | 10 | 6012345678, 6076543210, 6042987654 |
| **💻 DIGITAL** | N/A | N/A | Ventas desde canal web/app |

### 🎁 Productos y Servicios

| Producto | Precio | Código MOVIL | Código FIJA | Código DIGITAL |
|----------|--------|--------------|-------------|----------------|
| **TU MASCOTA** | $16,000 | 2119 / TU MASCOTA | 2162 / TU MASCOTA FIJA | 4046 / Mascotas |
| **TU VEHICULO** | $9,600 | 4046 / Vehiculo | 4046 / Vehiculo | 4046 / Vehiculo |
| **TU BIENESTAR** | $20,500 | TBD | TBD | TBD |
| **PROMO TU MASCOTA** | $16,000 | 2119 / TU MASCOTA | 2162 / TU MASCOTA FIJA | 4046 / Mascotas |

---

## 📊 Contexto del Negocio

### Proceso Actual (Manual)

El proceso actual involucra dos cargas de ventas:

1. **Primera Carga con Diego (Analista de Datos)**
   - Se usa un Google Sheets llamado "Consolidador de Ventas"
   - Se carga mediante script desde "Tipificador de Ventas"
   - Es un proceso manual y lento

2. **Segunda Carga - Reportes a Movistar**
   - Se envían **5 archivos principales** a Movistar
   - Se envían **3 archivos adicionales** por segmento (Digital, Fija, Móvil)
   - Se genera **1 archivo mensual consolidado**

### Migración a Automatización

**🎯 Objetivo**: Migrar de Google Sheets + Scripts a procesamiento Python + CSV

**✅ Beneficios**:
- ⚡ Mayor velocidad de procesamiento
- 📊 Mejor análisis de datos con pandas
- 🔄 Control de versiones con Git
- 🐛 Menos errores humanos
- 📈 Escalabilidad
- 🧪 Testing automatizado

---

## 🔄 Flujo de Procesos

### Proceso de Carga Principal

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRADA DE DATOS                              │
├─────────────────────────────────────────────────────────────────┤
│ 1. TIPIFICADOR DE VENTAS (Google Sheets → CSV)                  │
│    - Datos diarios de ventas ingresados por asesores            │
│    - Se exporta a CSV para procesamiento                         │
│                                                                  │
│ 2. REPORTE DE VENTAS DIGITALES MOVISTAR (Google Sheets → CSV)   │
│    - Ventas específicas del canal digital                       │
│    - Se exporta a CSV para procesamiento                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    VALIDACIÓN Y LIMPIEZA                         │
├─────────────────────────────────────────────────────────────────┤
│ • Validar teléfonos (10 dígitos, inicia con 3 o 6)             │
│ • Validar nombres de asesores (no números, no #N/A)             │
│ • Validar LOGINs (numérico, no vacío)                           │
│ • Detectar y eliminar duplicados vs histórico                   │
│ • Clasificar automáticamente por segmento                       │
│ • Generar archivo de NOVEDADES con registros inválidos         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESAMIENTO POR SEGMENTO                    │
├─────────────────────────────────────────────────────────────────┤
│ • Segmentar datos: DIGITAL / FIJA / MOVIL                       │
│ • Transformar formato según especificaciones                     │
│ • Calcular campos derivados (fecha, hora, códigos)              │
│ • Aplicar reglas de negocio específicas                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    GENERACIÓN DE ARCHIVOS                        │
├─────────────────────────────────────────────────────────────────┤
│ GRUPO 1: Archivos para Movistar (5 archivos)                   │
│ ├─ Contact Log Movistar Asist_[FECHA].xlsx                     │
│ ├─ FORMATO MOVISTAR_[FECHA].xlsx                               │
│ ├─ SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG_[FECHA].xlsx   │
│ ├─ SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA_[FECHA].xlsx  │
│ └─ SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_MOV_[FECHA].xlsx   │
│                                                                  │
│ GRUPO 2: Archivos por segmento (3 archivos)                    │
│ ├─ FORMATO MOVISTAR_DIGITAL_[FECHA].xlsx                       │
│ ├─ FORMATO MOVISTAR_FIJA_[FECHA].xlsx                          │
│ └─ FORMATO MOVISTAR_MOVIL_[FECHA].xlsx                         │
│                                                                  │
│ GRUPO 3: Consolidados mensuales (4 archivos)                   │
│ ├─ [MES]_Exitosas_Movistar.xlsx                                │
│ ├─ [MES]_NO_Exitosas_Movistar.xlsx (NOVEDADES)                │
│ ├─ [MES]_RTA_CONSOLIDADO_Movistar.xlsx                         │
│ └─ [MES]_RTA_PENDIENTES_Movistar.xlsx                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ALMACENAMIENTO HISTÓRICO                      │
├─────────────────────────────────────────────────────────────────┤
│ data/historico/                                                  │
│ ├── CONSOLIDADOR/[MES]/                                         │
│ │   ├── CARG. DIGITAL/                                          │
│ │   ├── CARG. FIJA/                                             │
│ │   ├── CARG. MOVIL/                                            │
│ │   └── Archivos consolidados del mes                           │
│ │                                                                │
│ └── REPORTEVENTAS_ENVIADO/[MES]/                               │
│     ├── ENV. DIGITAL/                                           │
│     ├── ENV. FIJA/                                              │
│     ├── ENV. MOVIL/                                             │
│     ├── ENVI. GENERAL/                                          │
│     ├── ENVI. N.F DIGITAL/ (No Facturados)                     │
│     ├── ENVI. N.F FIJA/                                         │
│     └── ENVI. N.F MOVIL/                                        │
└─────────────────────────────────────────────────────────────────┘
```

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
- ✅ **Clasificación automática** de segmentos (Móvil/Fija)
- ✅ **Archivo de novedades** para registros inválidos

---

## 🔒 Validaciones Críticas

### 📞 Validación de Teléfonos

Todos los números de teléfono deben cumplir las siguientes reglas:

#### ✅ Criterios Válidos

| Tipo | Primer Dígito | Total Dígitos | Segmento | Ejemplo |
|------|---------------|---------------|----------|---------|
| **Móvil** | 3 | 10 | MOVIL | 3001234567 |
| **Fija** | 6 | 10 | FIJA | 6012345678 |

#### ❌ Registros Inválidos

Un registro se marca como **NO VÁLIDO** y se envía al archivo de **NOVEDADES** si:

1. **Teléfono inválido**:
   - No tiene exactamente 10 dígitos
   - No inicia con 3 (móvil) o 6 (fija)
   - Contiene letras o caracteres especiales
   - Está vacío, es "N/A", "NA", "#N/A" o similar

2. **Nombre del asesor inválido**:
   - Contiene números en el nombre
   - Está vacío o es "#N/A"
   - No tiene nombre válido en el campo

3. **LOGIN inválido**:
   - No es numérico
   - Está vacío
   - Contiene caracteres no numéricos

4. **Datos faltantes críticos**:
   - No hay número de teléfono ingresado
   - Campos obligatorios vacíos

### 🎯 Clasificación Automática de Segmento

```python
# Lógica de clasificación
if telefono.startswith('3') and len(telefono) == 10:
    segmento = "MOVIL"
elif telefono.startswith('6') and len(telefono) == 10:
    segmento = "FIJA"
else:
    segmento = "INVALIDO" → Va a NOVEDADES
```

### 📝 Archivo de Novedades

**Nombre**: `[MES]_NO_Exitosas_Movistar.xlsx`

**Contenido**: Registros que NO pasaron las validaciones

**Formato**: Mismo formato que "Tipificador de Ventas" + columna "MOTIVO_RECHAZO"

**Columnas adicionales**:
- `MOTIVO_RECHAZO`: Descripción del error
- `FECHA_PROCESAMIENTO`: Cuándo se procesó
- `ESTADO`: "RECHAZADO"

---

## 📄 Formatos de Archivos de Salida

### 📦 GRUPO 1: Archivos para Movistar (5 archivos)

#### 1. Contact Log Movistar Asist_[FECHA].xlsx

**Ejemplo**: `Contact Log Movistar Asist_8_Al_22_OCT_2025.xlsx`

**Descripción**: Log de contactos con asistencias vendidas

**Columnas**:
```
- FECHA_CONTACTO
- HORA_CONTACTO
- TELEFONO_CLIENTE
- NOMBRE_CLIENTE
- TIPO_ASISTENCIA
- ESTADO
- ASESOR
- OBSERVACIONES
```

#### 2. FORMATO MOVISTAR_[FECHA].xlsx

**Ejemplo**: `FORMATO MOVISTAR_8_Al_22_OCT_2025.xlsx`

**Descripción**: Formato general de ventas Movistar

**Columnas**:
```
- FECHA_ALTA
- HORA_VENTA
- NUM_CELULAR
- NOMBRE_TITULAR
- DOCUMENTO
- TIPO_VENTA
- COD_SERVICIO
- PROGRAMA
- PROCESO
- ASESOR_VENTA
- Campo_Observacion
- Campo_Razon
```

#### 3. SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG_[FECHA].xlsx

**Ejemplo**: `SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG_8_A_22_OCT_(JC).xlsx`

**Descripción**: Asistencias digitales para Movistar

**Columnas**:
```json
{
  "FECHA_ALTA": "2025-10-06",
  "HORA_VENTA": "17:57:34",
  "NUM_CELULAR": "3004233641",
  "PlanDesc": "",
  "COD_PLAN": "",
  "NOMBRE_TITULAR": "",
  "ASESOR_VENTA": "Digital",
  "CC_AFILIADO": "",
  "Tipo_de_Envio": "",
  "Dato_de_envio": "",
  "COD_SERVICIO": "4046",
  "PROGRAMA": "Mascotas",
  "PROCESO": "Activar",
  "Campo_Observacion": "Asesor de venta Digital. Fecha de venta 2025-10-06 Hora de venta 17:57 Cliente acepta SI.",
  "Campo_Razon": "Activaciones Serv Suplementarios, Asistencias 4046, ASISTENCIAS: Venta telefónica hecha por el proveedor Connect Assistance",
  "RTA": "",
  "Contact_Log": ""
}
```

#### 4. SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA_[FECHA].xlsx

**Ejemplo**: `SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA_8_A_22_OCT_(JC).xlsx`

**Descripción**: Asistencias de telefonía fija

**Formato**: Mismo que el archivo DIG (punto 3)

**Diferencia**: Campo `ASESOR_VENTA` = "Fija"

#### 5. SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_MOV_[FECHA].xlsx

**Ejemplo**: `SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_MOV_8_Al_22_OCT_(JC).xlsx`

**Descripción**: Asistencias de móvil

**Formato**: Mismo que el archivo DIG (punto 3)

**Diferencia**: Campo `ASESOR_VENTA` = "Móvil"

### 📦 GRUPO 2: Archivos por Segmento (3 archivos)

#### 6. FORMATO MOVISTAR_DIGITAL_[FECHA].xlsx

**Ejemplo**: `FORMATO MOVISTAR_DIGITAL_8_Al_22_OCT_2025.xlsx`

**Descripción**: Ventas segmentadas de digital

**Formato**: Mismo que SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG

#### 7. FORMATO MOVISTAR_FIJA_[FECHA].xlsx

**Ejemplo**: `FORMATO MOVISTAR_FIJA_8_Al_22_OCT_2025.xlsx`

**Descripción**: Ventas segmentadas de fija

**Formato**: Mismo que SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA

#### 8. FORMATO MOVISTAR_MOVIL_[FECHA].xlsx

**Ejemplo**: `FORMATO MOVISTAR_MOVIL_8_Al_22_OCT_2025.xlsx`

**Descripción**: Ventas segmentadas de móvil

**Formato**: Mismo que SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_MOV

### 📦 GRUPO 3: Consolidados Mensuales (4 archivos)

#### 9. [MES]_Exitosas_Movistar.xlsx

**Ejemplo**: `OCTUBRE_Exitosas_Movistar.xlsx`

**Descripción**: Todas las ventas exitosas del mes consolidadas

**Columnas**: Consolidador de Ventas
```
- Marca temporal
- Correo vendedor/a
- Segmento
- Documento cliente
- # Tel.Llamada
- TELEFONO DEL CLIENTE (DONDE SE VA CARGAR EL SERVICIO)
- Servicio/producto vendido
- Correo Cliente
- Observación
- Dirección Cliente
- $ Costo Plan
- Login
- DD/MM/YYYY
- Día #
- Día - Short
- Día - Long
- Mes #
- Mes - Short
- Mes - Long
- Año #
- Sem_Año
- Sem_Año [S-#]
- Sem_Mes
- Sem_Mes [S-#]
- Hora (H)
- Respuesta
```

#### 10. [MES]_NO_Exitosas_Movistar.xlsx (NOVEDADES)

**Ejemplo**: `OCTUBRE_NO_Exitosas_Movistar.xlsx`

**Descripción**: Registros que NO pasaron validaciones

**Formato**: Tipificador de Ventas + columnas adicionales
```
- Todas las columnas de Tipificador de Ventas
- MOTIVO_RECHAZO (string)
- FECHA_PROCESAMIENTO (datetime)
- ESTADO (string): "RECHAZADO"
- VALIDACION_TELEFONO (bool)
- VALIDACION_ASESOR (bool)
- VALIDACION_LOGIN (bool)
```

#### 11. [MES]_RTA_CONSOLIDADO_Movistar.xlsx

**Ejemplo**: `OCTUBRE_RTA_CONSOLIDADO_Movistar.xlsx`

**Descripción**: Respuestas consolidadas de todas las cargas del mes

**Contenido**: Ventas con respuesta de Movistar

#### 12. [MES]_RTA_PENDIENTES_Movistar.xlsx

**Ejemplo**: `OCTUBRE_RTA_PENDIENTES_Movistar.xlsx`

**Descripción**: Ventas pendientes de respuesta

**Contenido**: Ventas sin respuesta aún de Movistar

---

## 📊 Estructura de Datos de Entrada

### Archivo 1: _TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv

**Fuente**: Google Sheets exportado a CSV

**Columnas** (21 campos):

```python
columnas = [
    "Marca temporal",                    # datetime: "30/10/2025 9:25:34"
    "Dirección de correo electrónico",  # email asesor
    "Puntuación",                        # int (opcional)
    "OPCION",                           # string (opcional)
    "LOGIN",                            # int: 12822 (ID del asesor)
    "Nombre del asesor",                # string: "Carmen Rubiano"
    "BASE ASIGNADA",                    # string: "FIJA", "MOVIL", "DIGITAL"
    "Nombre del cliente",               # string
    "Correo electronico del cliente",   # email
    "TELEFONO DEL CLIENTE (DONDE SE VA CARGAR EL SERVICIO)", # string: 10 dígitos
    "TIPO DE VENTA",                    # string: "TU MASCOTA", "TU VEHICULO", "TU BIENESTAR"
    "¿LA VENTA PROVIENE DE UN REFERIDO?", # string: "Si", "No"
    "TELEFONO DEL CLIENTE DONDE SE REALIZO LA VENTA (GRABACION)", # string: 10 dígitos
    "DIRECCIÓN DEL CLIENTE",            # string
    "Documento de identidad del cliente", # string
    "¿El cliente es empleado de Movistar?", # string: "Si", "No"
    "OBSERVACION",                      # string
    "SI LA RESPUESTA ANTERIOR FUE AFIRMATIVA...", # string (opcional)
    "¿POSTULAS ESTA LLAMADA PARA AUDITORÍA DE CALIDAD?", # string: "SI", "NO"
    "SI LA VENTA ES VEHÍCULO, INGRESA LA PLACA", # string (opcional)
    "costo plan"                        # string: "$16.000", "$9.600", "$20.500"
]
```

**Ejemplo de registro**:
```csv
30/10/2025 9:25:34,carmen.rubiano@connect.inc,,,12822,Carmen Rubiano,FIJA,ALVARO BARBON TORRES,alvarto16@gmail.com,6076688842,TU MASCOTA,No,3105074137,NA,80168873,No,NA,NA,SI,,$16.000
```

### Archivo 2: Reporte de ventas digitales MOVISTAR - Sheet1.csv

**Fuente**: Google Sheets exportado a CSV

**Columnas** (10 campos):

```python
columnas = [
    "Num_Celular",       # string: 10 dígitos iniciando con 3
    "cod_plantarif",     # string: código de plan tarifario
    "Codigo_Bono",       # string (opcional)
    "Cod_ciclo",         # string: código de ciclo
    "Fecha de venta",    # datetime
    "Nombre del cliente",# string
    "Email",            # email
    "Plan",             # string: nombre del plan
    "ENVIADA",          # string: "SI", "NO"
    "RESPUESTA",        # string (opcional)
    "Observación"       # string (opcional)
]
```

---

## 🗂️ Mapeo de Archivos: Consolidador vs Reportes Enviados

### ⚠️ Archivos que se repiten

Algunos archivos aparecen tanto en `CONSOLIDADOR/` como en `REPORTEVENTAS_ENVIADO/`:

| Archivo en CONSOLIDADOR | Archivo en REPORTEVENTAS_ENVIADO | ¿Son iguales? |
|-------------------------|-----------------------------------|---------------|
| `[MES]_Exitosas_Movistar.xlsx` | No existe equivalente | ❌ Solo en CONSOLIDADOR |
| `[MES]_NO_Exitosas_Movistar.xlsx` | No existe equivalente | ❌ Solo en CONSOLIDADOR |
| `CARG. DIGITAL/` | `ENV. DIGITAL/` | ✅ Similar, pero ENV tiene respuesta |
| `CARG. FIJA/` | `ENV. FIJA/` | ✅ Similar, pero ENV tiene respuesta |
| `CARG. MOVIL/` | `ENV. MOVIL/` | ✅ Similar, pero ENV tiene respuesta |

### 📋 Diferencia entre CONSOLIDADOR y REPORTEVENTAS_ENVIADO

**CONSOLIDADOR** (`data/historico/CONSOLIDADOR/[MES]/`):
- Archivos **generados** por el sistema
- Datos **procesados y validados**
- Listos para enviar a Movistar
- **Estado**: "PREPARADO"

**REPORTEVENTAS_ENVIADO** (`data/historico/REPORTEVENTAS_ENVIADO/[MES]/`):
- Archivos **ya enviados** a Movistar
- Incluyen **respuesta de Movistar** (columna RTA)
- **Estado**: "ENVIADO" y "RESPONDIDO"
- Contienen subcarpetas para no facturados (N.F)

**Flujo**:
```
1. Procesar → CONSOLIDADOR/[MES]/CARG.[SEGMENTO]/
2. Enviar a Movistar
3. Recibir respuesta
4. Mover a → REPORTEVENTAS_ENVIADO/[MES]/ENV.[SEGMENTO]/
```

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
- **Python**: 3.10 o superior
- **pip**: Gestor de paquetes de Python
- **Git**: Para control de versiones

### Dependencias de Python (requirements.txt)

#### 📦 **Core Dependencies**
```
pandas>=2.0.0          # Manipulación de datos
numpy>=1.24.0          # Operaciones numéricas
openpyxl>=3.1.0        # Lectura/escritura Excel
xlsxwriter>=3.1.0      # Escritura Excel avanzada
python-dateutil>=2.8.0 # Manejo de fechas
```

#### 🔧 **Configuration & Validation**
```
pydantic>=2.0.0        # Validación de datos y configuración
pydantic-settings>=2.0.0  # Gestión de configuración con .env
python-dotenv>=1.0.0   # Variables de entorno
```

#### 🎨 **CLI & Output**
```
click>=8.1.0           # CLI interface
rich>=13.5.0           # Output formateado y colorido
```

#### 🔄 **Reliability**
```
tenacity>=8.2.0        # Retry logic con exponential backoff
```

#### 🧪 **Development & Testing**
```
pytest>=7.4.0          # Testing framework
pytest-cov>=4.1.0      # Cobertura de tests
pytest-typeguard>=4.0.0  # Type checking en runtime
```

#### 🛠️ **Code Quality**
```
black>=23.0.0          # Formateo de código
isort>=5.12.0          # Ordenar imports
flake8>=6.0.0          # Linting
mypy>=1.5.0            # Type checking estático
bandit>=1.7.0          # Seguridad
pre-commit>=3.4.0      # Git hooks
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

### 🆕 Nuevo Sistema de Configuración (Recomendado)

El sistema ahora soporta configuración mediante **variables de entorno** con **Pydantic Settings**:

#### 1. Crear archivo `.env` en la raíz del proyecto

```bash
# .env - Configuración del sistema

# Entorno de ejecución
MOVISTAR_ENV=development  # development | production | testing

# Fechas de procesamiento
MOVISTAR_START_DATE=2025-10-23
MOVISTAR_END_DATE=2025-10-31

# Rutas personalizadas (opcional)
# MOVISTAR_BASE_DIR=/ruta/personalizada
# MOVISTAR_DATA_DIR=/ruta/personalizada/data

# Configuración de logs
MOVISTAR_LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
```

#### 2. Ventajas del nuevo sistema

✅ **Configuración centralizada**: Todas las settings en un solo lugar  
✅ **Validación automática**: Pydantic valida tipos y valores  
✅ **Multi-entorno**: Diferentes configs para dev/prod/test  
✅ **Type safety**: Type hints en toda la configuración  
✅ **Documentación auto-generada**: Settings con descripción  

#### 3. Uso programático

```python
from src.core.config import get_settings

# Obtener configuración (singleton)
settings = get_settings()

# Acceder a valores
print(settings.start_date)  # date(2025, 10, 23)
print(settings.input_dir)   # Path object
print(settings.environment) # Environment.DEVELOPMENT

# Crear directorios automáticamente
settings.create_directories()
```

### 📋 Sistema Legacy (Todavía soportado)

El sistema antiguo con `config.py` sigue funcionando por **backward compatibility**:

```python
# config.py - Sistema antiguo
import config

BASE_DIR = config.BASE_DIR
START_DATE = config.START_DATE
END_DATE = config.END_DATE
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

O usar el método del nuevo sistema:

```python
from src.core.config import get_settings

settings = get_settings()
settings.create_directories()  # Crea toda la estructura automáticamente
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

## 🚀 Mejoras Recientes (Noviembre 2025)

### ✨ Sistema Profesional Implementado

El sistema ha sido mejorado significativamente con arquitectura profesional y mejores prácticas:

#### 🏗️ **Nuevo Módulo Core (`src/core/`)**

**1. Sistema de Configuración Moderno (`config.py`)**
- ✅ Pydantic Settings con validación automática
- ✅ Soporte para variables de entorno (.env)
- ✅ Multi-entorno (dev/prod/test)
- ✅ Type safety completo
- ✅ Singleton pattern

**2. Excepciones Personalizadas (`exceptions.py`)**
- ✅ 15+ excepciones específicas del dominio
- ✅ Contexto detallado en errores
- ✅ Mejor debugging
- ✅ Wrapping de excepciones originales

**3. Modelos de Dominio (`models.py`)**
- ✅ SaleRecord con validación automática
- ✅ ProcessingMetrics para métricas
- ✅ ValidationResult para resultados
- ✅ Validadores custom (teléfonos, nombres)

**4. Decorators Utilities (`decorators.py`)**
- ✅ @retry con exponential backoff
- ✅ @timing para medición de performance
- ✅ @log_execution para trazabilidad
- ✅ @cache_result para optimización
- ✅ @validate_file_exists para validación

#### 🛡️ **Confiabilidad Mejorada**

- **Retry automático**: Funciones críticas se reintentan en caso de error
- **Timing**: Todas las operaciones se miden para detectar cuellos de botella
- **Logging mejorado**: Trazabilidad completa de ejecución
- **Backward compatibility**: Sistema antiguo sigue funcionando

#### 🧪 **Testing Profesional**

- ✅ 12/12 tests de integración pasando
- ✅ 90% coverage en módulos core
- ✅ Tests automatizados con pytest
- ✅ Type checking con mypy

#### 📦 **Nuevas Tecnologías**

- `pydantic>=2.0.0`: Validación y configuración
- `click>=8.1.0`: CLI interface
- `rich>=13.5.0`: Output formateado
- `tenacity>=8.2.0`: Retry logic
- `mypy`, `black`, `isort`: Code quality tools

#### 🧹 **Código Más Limpio**

- ❌ Eliminados 11 scripts temporales
- ✅ 79% menos archivos en root
- ✅ Estructura más mantenible
- ✅ Documentación actualizada

---

**Última actualización**: 3 de Noviembre 2025
