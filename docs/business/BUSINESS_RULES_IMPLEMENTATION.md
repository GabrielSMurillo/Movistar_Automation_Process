# Implementación de Reglas de Negocio Críticas
## Sistema de Validación y Detección de Novedades

### 📋 Fecha de Implementación
4 de Noviembre, 2025

---

## 🎯 Objetivo

Implementar sistema robusto de validación que asegure que **SOLO registros 100% válidos** sean entregados al cliente, y que registros con problemas sean capturados en un archivo de "Novedades" para revisión por operaciones.

---

## ✅ Reglas de Validación Implementadas

### 1. Validación de Números Telefónicos

#### 1.1 Prefijo 957
- **Regla**: Si el número comienza con 957, tomar los **10 dígitos desde la DERECHA**
- **Ejemplo**: `9573001234567` → `3001234567`
- **Implementado en**: `EnhancedPhoneValidator.validate()`

#### 1.2 Longitud
- **Regla**: El número DEBE tener exactamente 10 dígitos
- **Rechazar**: Números con menos o más de 10 dígitos
- **Implementado en**: `EnhancedPhoneValidator.validate()`

#### 1.3 Números Móviles
- **Regla**: Deben iniciar con `3`
- **Prefijos válidos**: 300-305, 310-324, 350-352
- **Rechazar**: Números que inician con 3 pero tienen prefijo inválido
- **Implementado en**: `EnhancedPhoneValidator._validate_movil()`

#### 1.4 Números Fijos (CRÍTICO)
- **Regla 1**: Deben iniciar con `6`
- **Regla 2**: DEBEN tener código de ciudad (indicativo) válido
- **Códigos válidos**: 601, 602, 604, 605, 606, 607, 608
- **Rechazar**: Números que inician con 6 pero NO tienen código de ciudad válido
- **Ejemplo válido**: `6012345678` (Bogotá)
- **Ejemplo inválido**: `6502345678` (código 650 no existe)
- **Implementado en**: `EnhancedPhoneValidator._validate_fija()`

#### 1.5 Clasificación Correcta
- **Regla**: El tipo de línea (MOVIL/FIJA) debe corresponder al prefijo del número
- **Implementado en**: `NoveltyDetector.validate_record()`

---

### 2. Validación de Nombres de Asesor

#### 2.1 No puede ser número
- **Rechazar**: Nombres que contengan dígitos
- **Ejemplo inválido**: `Juan123`, `Maria2`
- **Implementado en**: `FieldValidators.validate_asesor_name()`

#### 2.2 No puede ser #N/A
- **Rechazar**: `#N/A`, `N/A`, `n/a`, `#¡VALOR!`, `#REF!`, etc.
- **Lista completa**: Ver `FieldValidators.INVALID_TEXT_VALUES`
- **Implementado en**: `FieldValidators.validate_asesor_name()`

#### 2.3 Debe ser string válido
- **Rechazar**: Valores vacíos, espacios en blanco, valores nulos
- **Longitud mínima**: 3 caracteres
- **Al menos 2 letras**: Para evitar nombres como ".", "XY"
- **Implementado en**: `FieldValidators.validate_asesor_name()`

---

### 3. Validación de Login

#### 3.1 Debe ser numérico
- **Rechazar**: Logins no numéricos como `ABC123`, `user@domain`
- **Implementado en**: `FieldValidators.validate_login()`

#### 3.2 No puede ser #N/A
- **Rechazar**: Valores inválidos de Excel (#N/A, etc.)
- **Implementado en**: `FieldValidators.validate_login()`

#### 3.3 Longitud mínima
- **Mínimo**: 3 dígitos
- **Implementado en**: `FieldValidators.validate_login()`

---

### 4. Validación de Nombre de Cliente

#### 4.1 No puede ser #N/A
- **Rechazar**: Valores inválidos de Excel
- **Implementado en**: `FieldValidators.validate_cliente_name()`

#### 4.2 Debe ser string válido
- **Rechazar**: Valores vacíos, nulos
- **Longitud mínima**: 2 caracteres
- **Al menos 1 letra**: Permite nombres de empresas con números
- **Implementado en**: `FieldValidators.validate_cliente_name()`

---

### 5. Validación de Códigos de Servicio (MUY CRÍTICO)

#### 5.1 Códigos por Tipo de Línea
Los códigos son **DIFERENTES** según el tipo de línea:

**MOVIL (Celular - inicia con 3):**
| Plan         | Código |
|--------------|--------|
| TU BIENESTAR | 2119   |
| TU MASCOTA   | 3823   |
| TU HOGAR     | 5000   |
| TU VEHICULO  | 5002   |

**FIJA (Fijo - inicia con 6):**
| Plan         | Código |
|--------------|--------|
| TU BIENESTAR | 15640  |
| TU MASCOTA   | 15639  |
| TU HOGAR     | 15641  |
| TU VEHICULO  | 15642  |

**DIGITAL (Venta Online):**
| Plan            | Código |
|-----------------|--------|
| MASCOTAS        | 4046   |
| MULTIASISTENCIA | 4047   |
| VIAL            | 4045   |

#### 5.2 Validación de Correspondencia
- **Regla**: El código asignado DEBE corresponder al tipo de línea
- **Ejemplo válido**: TU MASCOTA en MOVIL → 3823
- **Ejemplo inválido**: TU MASCOTA en MOVIL → 15639 (es código FIJA)
- **Implementado en**: `ServiceCodeMapper.validate_code()`

---

## 🔄 Flujo del Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  1. CARGA DE DATOS                                          │
│  - Tipificador de Ventas (CSV)                             │
│  - Reporte de Ventas Digitales (CSV)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. PROCESAMIENTO INICIAL                                   │
│  - Limpieza de teléfonos (prefijo 957, formato)            │
│  - Extracción de fecha/hora                                 │
│  - Clasificación de tipo de línea (MOVIL/FIJA)             │
│  - Asignación de códigos de servicio                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. VALIDACIÓN COMPLETA (NoveltyDetector)                  │
│  ✓ Teléfono válido (longitud, prefijo, indicativo)         │
│  ✓ Asesor válido (string, sin números, sin #N/A)           │
│  ✓ Login válido (numérico, sin #N/A)                       │
│  ✓ Cliente válido (string, sin #N/A)                       │
│  ✓ Código de servicio correcto para tipo de línea          │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────┴───────┐
                    ↓               ↓
    ┌─────────────────────┐  ┌─────────────────────┐
    │  REGISTROS VÁLIDOS  │  │     NOVEDADES       │
    │  (Para Cliente)     │  │  (Para Operaciones) │
    └─────────────────────┘  └─────────────────────┘
                ↓                        ↓
    ┌─────────────────────┐  ┌─────────────────────┐
    │  ARCHIVOS CLIENTE:  │  │  ARCHIVOS INTERNOS: │
    │  • Contact Log      │  │  • Tipificador_     │
    │  • FORMATO MOVISTAR │  │    Novedades.xlsx   │
    │  • SVAS (3 archivos)│  │  • Digital_         │
    │  • Formatos internos│  │    Novedades.xlsx   │
    │  • Reporte mensual  │  │                     │
    └─────────────────────┘  └─────────────────────┘
```

---

## 📁 Archivos Generados

### Archivos para Cliente (Solo registros 100% válidos)
1. **Contact Log Movistar Asist_{fecha}.xlsx**
2. **FORMATO MOVISTAR_{fecha}.xlsx**
3. **SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG_{fecha}.xlsx**
4. **SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA_{fecha}.xlsx**
5. **SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_MOVIL_{fecha}.xlsx**
6. **FORMATO MOVISTAR_Digital_{fecha}.xlsx**
7. **FORMATO MOVISTAR_FIJA_{fecha}.xlsx**
8. **FORMATO MOVISTAR_MOVIL_{fecha}.xlsx**
9. **{MES}_Exitosas_Movistar.xlsx** (Reporte consolidado mensual)

### Archivos Internos (Para revisión de operaciones)
1. **Tipificador_Novedades_{fecha}.xlsx**
   - Contiene registros del Tipificador que NO pasaron validación
   - Columnas adicionales:
     - `Teléfono Válido`: TRUE/FALSE
     - `Asesor Válido`: TRUE/FALSE
     - `Login Válido`: TRUE/FALSE
     - `Cliente Válido`: TRUE/FALSE
     - `Código Válido`: TRUE/FALSE
     - `Motivos de Rechazo`: Descripción detallada

2. **Digital_Novedades_{fecha}.xlsx**
   - Contiene registros digitales que NO pasaron validación
   - Misma estructura que Tipificador_Novedades

---

## 🔧 Componentes Implementados

### Nuevos Módulos

1. **`src/services/novelty_detector.py`**
   - Clase: `NoveltyDetector`
   - Métodos:
     - `validate_record()`: Valida un registro completo
     - `separate_valid_and_novelties()`: Separa válidos de inválidos
     - `generate_novelty_report()`: Genera Excel de novedades

2. **`src/services/field_validators.py`**
   - Clase: `FieldValidators`
   - Métodos:
     - `validate_asesor_name()`: Valida nombre de asesor
     - `validate_login()`: Valida login
     - `validate_cliente_name()`: Valida nombre de cliente
     - `validate_record()`: Validación completa de registro

3. **`src/services/phone_validator.py`**
   - Clase: `EnhancedPhoneValidator`
   - Métodos:
     - `validate()`: Validación completa de teléfono
     - `_validate_movil()`: Validación específica móviles
     - `_validate_fija()`: Validación específica fijos (con indicativo)
     - `validate_series()`: Validación en batch de pandas Series

4. **`src/services/service_code_mapper.py`**
   - Clase: `ServiceCodeMapper`
   - Métodos:
     - `get_code()`: Obtiene código correcto según tipo de línea
     - `validate_code()`: Valida que código corresponda a tipo de línea
     - Constantes: `MOVIL_CODES`, `FIJA_CODES`, `DIGITAL_CODES`

### Módulos Modificados

1. **`src/data_processor.py`**
   - Integrado `NoveltyDetector` en:
     - `TipificadorProcessor.process()`
     - `DigitalProcessor.process()`
   - Ahora retorna solo registros válidos
   - Métricas incluyen conteo de novedades

2. **`main.py`**
   - Agregada sección de generación de reportes de novedades
   - Resumen final incluye conteo de novedades
   - Import de `pandas` para manejo de DataFrames de novedades

---

## 📊 Métricas y Reportes

El sistema ahora genera métricas detalladas:

```python
metrics_tip = {
    'ventas_procesadas': {...},          # Ventas antes de validación
    'ventas_validas': {...},             # Ventas que pasan validación
    'novedades': {...},                  # Ventas rechazadas
    'df_novedades': DataFrame,           # DataFrame con novedades
    ...
}
```

### Logs Generados

```
🔍 DETECTANDO NOVEDADES (REGISTROS INVÁLIDOS)
================================================================================
📊 Total registros procesados: 365
✅ Registros válidos: 320 (87.7%)
❌ Novedades detectadas: 45 (12.3%)

📋 DISTRIBUCIÓN DE NOVEDADES:
  📞 Teléfonos inválidos: 23
  👤 Asesores inválidos: 8
  🔑 Logins inválidos: 5
  🧑 Clientes inválidos: 12
  🏷️  Códigos inválidos: 3

📝 EJEMPLOS DE MOTIVOS DE RECHAZO:
  1. Teléfono no inicia con 3 (móvil) ni 6 (fijo): 5
  2. Asesor: Nombre contiene números: Juan123
  3. Cliente: Nombre de cliente inválido: #N/A
  4. Fijo sin código de ciudad válido: 650 (debe ser 601-608)
  5. Login: Login inválido: N/A
================================================================================
```

---

## 🧪 Casos de Prueba

### Caso 1: Teléfono con prefijo 957
```
Input:  9573001234567
Output: 3001234567 (MOVIL) ✅
```

### Caso 2: Teléfono fijo sin indicativo válido
```
Input:  6502345678
Output: RECHAZADO - Código de ciudad 650 no válido ❌
Motivo: "Fijo sin código de ciudad válido: 650 (debe ser 601-608)"
```

### Caso 3: Teléfono fijo con indicativo válido
```
Input:  6012345678
Output: 6012345678 (FIJA - Bogotá) ✅
```

### Caso 4: Asesor con nombre inválido
```
Input:  #N/A
Output: RECHAZADO ❌
Motivo: "Asesor: Nombre inválido: #N/A"
```

### Caso 5: Código incorrecto para tipo de línea
```
Input:  TU MASCOTA, MOVIL, código=15639
Output: RECHAZADO ❌
Motivo: "Código de servicio 15639 no válido para MOVIL"
Correcto: código=3823
```

---

## ⚠️ Puntos Críticos

### 1. Códigos de Servicio
**NUNCA** modificar los códigos sin aprobación del cliente. Los códigos incorrectos causan rechazo total del archivo.

### 2. Fijos con Indicativo
**TODOS** los números fijos (que inician con 6) **DEBEN** tener código de ciudad válido (601-608). Sin excepción.

### 3. Novedades NO van a Cliente
Los registros en archivos de novedades **NUNCA** deben incluirse en archivos para el cliente.

### 4. Preservar Orden de Prioridad
En consolidación mensual, históricos tienen prioridad sobre mes actual para evitar duplicados.

---

## 🚀 Próximos Pasos

1. ✅ Ejecutar pipeline completo con datos reales
2. ✅ Verificar que archivos cliente no tengan registros inválidos
3. ✅ Revisar archivo de novedades para identificar problemas en data source
4. ✅ Ajustar procesos upstream para reducir novedades
5. 📋 Documentar casos edge encontrados
6. 📋 Establecer KPIs de calidad (meta: <5% novedades)

---

## 📞 Contacto

Para preguntas sobre las reglas de negocio o modificaciones al sistema de validación, contactar al equipo de desarrollo.

**Última actualización**: 4 de Noviembre, 2025
