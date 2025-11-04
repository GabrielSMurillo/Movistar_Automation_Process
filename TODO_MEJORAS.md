# ✅ TODO LIST - Mejoras Sistema Movistar Automation

## 🎯 ESTADO ACTUAL (3 de Noviembre, 2025)

### ✅ COMPLETADO

- [x] **Análisis exhaustivo de arquitectura**
  - Identificados 3 problemas críticos
  - Descubiertos patrones de archivos consolidados
  - Documentado flujo de datos completo

- [x] **Contact Log Generator**
  - Implementado en: `src/generators/contact_log_generator.py`
  - 600+ líneas de código con documentación completa
  - Validación integrada de outputs
  - Formato exacto según especificaciones Movistar
  - Tests unitarios pendientes

- [x] **Documentación comprehensiva**
  - `ARQUITECTURA_MEJORADA_PROPUESTA.md` (1000+ líneas)
  - `RESUMEN_EJECUTIVO.md`
  - Análisis de Contact Logs (estructura identificada)
  - Patrones de códigos de servicio documentados

---

## 🚀 PRIORIDAD ALTA (Sprint 1 - Próximas 2 semanas)

### 1. Integrar Contact Log Generator en Pipeline Principal

**Archivo**: `main.py` y `src/file_generator.py`

**Tareas**:
- [ ] Importar `ContactLogGenerator` en `main.py`
- [ ] Agregar llamada a generación de Contact Log
- [ ] Integrar con sistema de validación existente
- [ ] Probar con datos reales de octubre/septiembre
- [ ] Comparar outputs con archivos históricos manuales

**Código a agregar**:
```python
# En main.py, después de FASE 6: GENERACIÓN DE ARCHIVOS

from src.generators.contact_log_generator import ContactLogGenerator

# Generar Contact Log
logger.info("\n[1/N] Generando Contact Log...")
contact_log_generator = ContactLogGenerator()
success = contact_log_generator.generate(
    df_ventas_periodo,
    OUTPUT_DIR / OUTPUT_FILES['movistar_contact_log']
)

if success:
    stats = contact_log_generator.get_stats()
    logger.info(f"✅ Contact Log: {stats['records_processed']:,} registros")
else:
    logger.error("❌ Error generando Contact Log")
```

**Tiempo estimado**: 2-3 horas

---

### 2. Crear Tests Unitarios para Contact Log Generator

**Archivo**: `tests/unit/test_contact_log_generator.py`

**Tareas**:
- [ ] Test: Generación exitosa con datos válidos
- [ ] Test: Formato de columnas correcto
- [ ] Test: Validación de teléfonos (10 dígitos)
- [ ] Test: Formato de Campo Observacion
- [ ] Test: Formato de Campo Razon (3 nodos)
- [ ] Test: Manejo de DataFrame vacío
- [ ] Test: Filtrado de duplicados
- [ ] Test: Validación de archivo generado
- [ ] Test: Comparación con archivo legacy

**Cobertura objetivo**: 100% del ContactLogGenerator

**Tiempo estimado**: 1 día

---

### 3. Implementar Input Adapters (CSV/Excel)

**Archivos nuevos**:
- `src/adapters/__init__.py`
- `src/adapters/input_adapter.py` (clase abstracta)
- `src/adapters/csv_adapter.py`
- `src/adapters/excel_adapter.py`

**Tareas**:
- [ ] Crear clase abstracta `InputAdapter`
- [ ] Implementar `CSVInputAdapter`
- [ ] Implementar `ExcelInputAdapter`
- [ ] Agregar detección automática de formato
- [ ] Modificar `src/data_loader.py` para usar adapters
- [ ] Tests unitarios para cada adapter
- [ ] Probar con archivos reales (CSV y XLSX)

**Beneficio**: Elimina necesidad de conversión manual Excel→CSV

**Código ejemplo**:
```python
# src/adapters/input_adapter.py

from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd

class InputAdapter(ABC):
    """Clase base para adapters de entrada."""
    
    @abstractmethod
    def read(self, file_path: Path) -> pd.DataFrame:
        """Lee archivo y retorna DataFrame."""
        pass
    
    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Verifica si el adapter soporta el archivo."""
        pass

class AdapterFactory:
    """Factory para crear adapters según tipo de archivo."""
    
    @staticmethod
    def create(file_path: Path) -> InputAdapter:
        """Crea adapter apropiado según extensión."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            return CSVInputAdapter()
        elif suffix in ['.xlsx', '.xls']:
            return ExcelInputAdapter()
        else:
            raise ValueError(f"Formato no soportado: {suffix}")
```

**Tiempo estimado**: 2-3 días

---

### 4. Extraer Configuración a YAML

**Archivos nuevos**:
- `config/schemas/v1/service_codes.yaml`
- `config/schemas/v1/phone_classification.yaml`
- `config/schemas/v1/output_files.yaml`
- `src/config/yaml_loader.py`

**Tareas**:
- [ ] Crear estructura de carpetas `config/schemas/v1/`
- [ ] Migrar `SERVICE_CODE_MAPPING` a YAML
- [ ] Migrar `PHONE_CLASSIFICATION` a YAML
- [ ] Migrar `OUTPUT_FILES` templates a YAML
- [ ] Implementar cargador de configuración YAML
- [ ] Modificar `config.py` para leer desde YAML
- [ ] Tests de carga de configuración
- [ ] Documentar estructura de YAMLs

**Ejemplo `service_codes.yaml`**:
```yaml
# config/schemas/v1/service_codes.yaml

version: "1.0"
description: "Mapeo de tipos de venta a códigos de servicio"

movistar_format:
  TU MASCOTA: "2119"
  TU VEHICULO: "2120"
  TU HOGAR: "2121"
  TU BIENESTAR: "2119"
  VIAL: "2119"

digital_format:
  Mascotas: "4045"
  Vehiculo: "4046"
  Hogar: "4047"
  Bienestar: "4045"
  Vial: "4045"

defaults:
  movistar: "2119"
  digital: "4045"
```

**Beneficio**: Configuración versionada, fácil de modificar sin tocar código

**Tiempo estimado**: 2 días

---

### 5. Implementar Validadores de Output

**Archivo nuevo**: `src/validators/output_validators.py`

**Tareas**:
- [ ] Crear clase `OutputValidator` abstracta
- [ ] Implementar `ContactLogValidator`
- [ ] Implementar `FormatoMovistarValidator`
- [ ] Implementar `SVASValidator`
- [ ] Agregar validación automática post-generación
- [ ] Log de errores de validación
- [ ] Tests unitarios para cada validador

**Validaciones a implementar**:
- ✓ Archivo existe
- ✓ Tiene columnas correctas
- ✓ Formato de datos correcto (teléfonos, fechas, códigos)
- ✓ No hay valores nulos en campos obligatorios
- ✓ Rangos válidos (fechas, montos)
- ✓ Referencias cruzadas consistentes

**Tiempo estimado**: 2 días

---

## 🔄 PRIORIDAD MEDIA (Sprint 2-3 - Semanas 3-6)

### 6. Refactorizar file_generator.py

**Objetivo**: Separar generación monolítica en generadores especializados

**Archivos afectados**:
- `src/file_generator.py` (modificar)
- `src/generators/formato_movistar_generator.py` (nuevo)
- `src/generators/svas_generator.py` (nuevo)
- `src/generators/monthly_report_generator.py` (nuevo)

**Tareas**:
- [ ] Extraer `generate_formato_movistar()` a clase especializada
- [ ] Extraer `generate_svas()` a clase especializada
- [ ] Extraer `generate_monthly_report()` a clase especializada
- [ ] Implementar clase base `FileGenerator` (abstracta)
- [ ] Aplicar Factory Pattern
- [ ] Actualizar `main.py` para usar nuevos generadores
- [ ] Tests de regresión (comparar outputs)

**Tiempo estimado**: 5 días

---

### 7. Implementar Modelos de Datos (Dataclasses)

**Archivo nuevo**: `src/models/venta.py`

**Tareas**:
- [ ] Crear dataclass `Venta`
- [ ] Crear enums `TipoLinea`, `EstadoVenta`
- [ ] Implementar métodos `to_dict()`, `from_dict()`
- [ ] Implementar factory methods por tipo de input
- [ ] Validación integrada en `__post_init__()`
- [ ] Type hints completos
- [ ] Tests unitarios exhaustivos

**Beneficio**:
- Tipo de datos fuertemente tipado
- Validación automática
- Mejor IDE support (autocomplete)
- Menos errores en runtime

**Tiempo estimado**: 2 días

---

### 8. Implementar Factory Pattern para Generadores

**Archivo nuevo**: `src/core/generator_factory.py`

**Tareas**:
- [ ] Crear `GeneratorFactory`
- [ ] Implementar registro de generadores (decorator)
- [ ] Modificar generadores para usar factory
- [ ] Agregar config de generadores en YAML
- [ ] Tests de factory

**Código ejemplo**:
```python
from src.core.generator_factory import GeneratorFactory

@GeneratorFactory.register('contact_log')
class ContactLogGenerator(FileGenerator):
    pass

# Uso:
generator = GeneratorFactory.create('contact_log')
generator.generate(df, output_path)
```

**Tiempo estimado**: 2 días

---

### 9. Schema Versioning

**Objetivo**: Soportar múltiples versiones de schemas

**Estructura**:
```
config/schemas/
├── v1/
│   ├── tipificador_schema.yaml
│   ├── digital_schema.yaml
│   └── output_schemas.yaml
├── v2/
│   └── ... (futuros cambios)
└── current -> v1  (symlink)
```

**Tareas**:
- [ ] Crear estructura de carpetas versionadas
- [ ] Implementar `SchemaManager`
- [ ] Migrar validaciones a schemas YAML
- [ ] Detección automática de versión de archivo
- [ ] Migración automática v1→v2
- [ ] Tests de compatibilidad

**Tiempo estimado**: 3 días

---

### 10. Aumentar Cobertura de Tests

**Objetivo**: De 30% a >80%

**Tareas**:
- [ ] Tests unitarios para todos los processors
- [ ] Tests unitarios para todos los generators
- [ ] Tests unitarios para todos los validators
- [ ] Tests de integración end-to-end
- [ ] Tests de regresión (comparar con outputs legacy)
- [ ] Tests de performance (benchmarks)
- [ ] Configurar coverage reporting
- [ ] Integrar en CI/CD

**Comando**:
```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

**Tiempo estimado**: 5 días (distribuido en todos los módulos)

---

## 🌟 MEJORAS FUTURAS (Backlog - Meses 3+)

### 11. Procesamiento en Paralelo

**Objetivo**: Reducir tiempo de ejecución de 5 min a <3 min

**Implementación**:
- Usar `multiprocessing` para procesar segmentos en paralelo
- Async I/O para carga de archivos
- Pool de workers para generación de archivos

**Tiempo estimado**: 1 semana

---

### 12. Integración Directa con Google Sheets

**Objetivo**: Eliminar paso de exportación CSV

**Implementación**:
- Implementar `GoogleSheetsAdapter`
- OAuth authentication
- Read/Write directo desde Sheets
- Sincronización bidireccional

**Beneficio**: Proceso 100% automatizado, sin intervención manual

**Tiempo estimado**: 2 semanas

---

### 13. Dashboard Web de Monitoreo

**Stack tecnológico**:
- Backend: FastAPI
- Frontend: React o Streamlit
- Base de datos: SQLite / PostgreSQL

**Features**:
- Visualización de métricas en tiempo real
- Historial de ejecuciones
- Alertas configurables
- Explorador de archivos generados
- Comparación de periodos

**Tiempo estimado**: 4 semanas

---

### 14. API REST para Consultas

**Endpoints propuestos**:
```
GET  /api/v1/ventas?fecha_inicio=2025-10-01&fecha_fin=2025-10-31
GET  /api/v1/ventas/{id}
GET  /api/v1/reportes
POST /api/v1/pipeline/execute
GET  /api/v1/metrics
```

**Beneficio**: Integración con otros sistemas

**Tiempo estimado**: 2 semanas

---

### 15. Sistema de Notificaciones

**Canales**:
- Email (SMTP)
- Slack webhook
- Microsoft Teams webhook

**Triggers**:
- Pipeline exitoso
- Errores de validación
- Duplicados detectados
- Nuevos archivos generados

**Tiempo estimado**: 1 semana

---

## 📊 MÉTRICAS DE PROGRESO

### Cobertura de Tests

```
Actual:     ████░░░░░░ 30%
Objetivo:   ████████░░ 80%
Sprint 1:   ████████░░ 60% (Contact Log + Adapters)
Sprint 2:   ████████░░ 80% (Generadores + Models)
```

### Complejidad Ciclomática

```
Actual:     ████████░░ ALTA (file_generator.py: 15+)
Objetivo:   ████░░░░░░ MEDIA (<10 por función)
Sprint 2:   ████░░░░░░ Reducción 40%
```

### Tiempo de Ejecución

```
Actual:     ████████░░ ~5 minutos
Objetivo:   ████░░░░░░ <3 minutos
Sprint 3:   ████████░░ ~4 minutos (optimizaciones I/O)
Sprint 4:   ████░░░░░░ ~2 minutos (paralelización)
```

---

## 🎯 CRITERIOS DE ACEPTACIÓN

### Para considerar Sprint 1 completado:

- [ ] Contact Log se genera automáticamente (sin intervención manual)
- [ ] Sistema acepta inputs CSV y XLSX transparentemente
- [ ] Configuración de códigos de servicio en YAML
- [ ] Cobertura de tests ≥60%
- [ ] Todos los tests pasan (green)
- [ ] Documentación actualizada
- [ ] No hay regresiones (outputs idénticos a sistema actual)

### Para considerar Sprint 2 completado:

- [ ] Generadores refactorizados (uno por tipo de archivo)
- [ ] Factory Pattern implementado
- [ ] Modelos de datos con dataclasses
- [ ] Cobertura de tests ≥80%
- [ ] Output validators funcionando
- [ ] Schema versioning implementado
- [ ] Performance ≥ sistema actual

---

## 🚨 RIESGOS Y MITIGACIÓN

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Regresión en outputs | MEDIO | ALTO | Tests exhaustivos de comparación |
| Cambios en formato Movistar | BAJO | ALTO | Schema versioning + adapters |
| Performance degradado | BAJO | MEDIO | Benchmarks antes/después |
| Resistencia al cambio | MEDIO | BAJO | Training + documentación clara |
| Bugs en producción | BAJO | ALTO | Testing comprehensivo + rollback plan |

---

## 📞 PRÓXIMOS PASOS INMEDIATOS

### Esta Semana (3-10 Nov)

1. **Lunes-Martes**: 
   - [ ] Revisar y aprobar Contact Log Generator
   - [ ] Ejecutar con datos reales
   - [ ] Comparar con archivos históricos

2. **Miércoles-Jueves**:
   - [ ] Integrar Contact Log en pipeline principal
   - [ ] Crear tests unitarios básicos
   - [ ] Ejecutar suite completa de tests

3. **Viernes**:
   - [ ] Code review completo
   - [ ] Documentar lecciones aprendidas
   - [ ] Planificar Sprint 2

---

## ✅ CHECKLIST DE REVISIÓN

Antes de considerar el trabajo terminado:

- [ ] Código revisado (code review)
- [ ] Tests pasando (100% green)
- [ ] Cobertura de tests adecuada (>60% Sprint 1, >80% Sprint 2)
- [ ] Documentación actualizada
- [ ] Changelog actualizado
- [ ] No hay warnings en linter
- [ ] Type hints completos (mypy passing)
- [ ] Performance aceptable (benchmarks)
- [ ] Outputs validados contra sistema legacy
- [ ] Manual de usuario actualizado
- [ ] Training realizado (si aplica)

---

## 📚 RECURSOS Y REFERENCIAS

- **Documentación técnica**: `/ARQUITECTURA_MEJORADA_PROPUESTA.md`
- **Resumen ejecutivo**: `/RESUMEN_EJECUTIVO.md`
- **Código nuevo**: `/src/generators/contact_log_generator.py`
- **Tests**: `/tests/unit/test_contact_log_generator.py` (pendiente)
- **Configuración**: `/config/schemas/v1/` (pendiente)

---

## 🎉 MOTIVACIÓN

Cada tarea completada nos acerca a un sistema:
- ✨ Más automatizado (menos trabajo manual)
- 🚀 Más rápido (procesamiento optimizado)
- 🛡️ Más confiable (tests comprehensivos)
- 📈 Más escalable (fácil de extender)
- 🎯 Más mantenible (código limpio y documentado)

**¡Vamos por ello!** 💪

---

*Última actualización: 3 de Noviembre, 2025*
*Versión: 1.0*
*Autor: Senior Data Analytics Engineer*
