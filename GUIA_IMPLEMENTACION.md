# 🚀 GUÍA DE IMPLEMENTACIÓN PASO A PASO

## Sistema Movistar - Refactorización Profesional

**Fecha:** 3 de Noviembre 2025  
**Tiempo estimado:** 2-4 horas para setup inicial  
**Nivel:** Intermediate/Advanced

---

## ⚠️ ANTES DE COMENZAR

### Pre-requisitos
- ✅ Python 3.10 o superior instalado
- ✅ Git configurado
- ✅ Editor de código (VS Code recomendado)
- ✅ PowerShell o terminal de Windows

### Backup Obligatorio
```powershell
# 1. Crear backup del sistema actual
git add .
git commit -m "chore: backup antes de refactorización"
git tag -a v1.0.0-pre-refactor -m "Estado antes de refactorización"
git push origin main --tags

# 2. Crear rama de refactorización
git checkout -b refactor/enterprise-architecture
```

---

## 📋 PASO 1: LIMPIEZA DE ARCHIVOS (15 minutos)

### 1.1 Aplicar Archivos Nuevos

```powershell
# En el root del proyecto

# Mover archivos de configuración
Move-Item -Force .gitignore_new .gitignore
Move-Item -Force requirements_new.txt requirements.txt
Move-Item -Force requirements-dev_new.txt requirements-dev.txt

# Verificar que se movieron correctamente
Test-Path .gitignore  # Debe retornar True
Test-Path requirements.txt  # Debe retornar True
```

### 1.2 Eliminar Scripts Temporales

```powershell
# Eliminar scripts de validación obsoletos
Remove-Item validate_system.py -ErrorAction SilentlyContinue
Remove-Item validate_sept_fast.py -ErrorAction SilentlyContinue
Remove-Item validate_september_simple.py -ErrorAction SilentlyContinue
Remove-Item validate_all_september_outputs.py -ErrorAction SilentlyContinue
Remove-Item test_september_pipeline.py -ErrorAction SilentlyContinue
Remove-Item test_full_pipeline_september.py -ErrorAction SilentlyContinue
Remove-Item deep_comparison_september.py -ErrorAction SilentlyContinue
Remove-Item analyze_historical_sept.py -ErrorAction SilentlyContinue
Remove-Item compare_contact_logs.py -ErrorAction SilentlyContinue
Remove-Item check_rta.py -ErrorAction SilentlyContinue
Remove-Item execution_summary.py -ErrorAction SilentlyContinue

# Verificar
Get-ChildItem *.py | Where-Object { $_.Name -match "validate_|test_september|deep_comparison|analyze_historical|compare_contact|check_rta|execution_summary" }
# No debe mostrar nada
```

### 1.3 Reorganizar Tests

```powershell
# Mover test_adapters.py a tests/ si existe
if (Test-Path "test_adapters.py") {
    Move-Item test_adapters.py tests/
}

# Verificar estructura de tests
Get-ChildItem tests/ -Recurse
```

---

## 📦 PASO 2: INSTALACIÓN DE DEPENDENCIAS (10 minutos)

### 2.1 Actualizar Entorno Virtual

```powershell
# Si ya tienes venv
.\venv\Scripts\Activate.ps1

# O crear nuevo
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2.2 Instalar Dependencies

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias principales
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Verificar instalación
pip list | Select-String "pydantic|click|pytest"
```

---

## ⚙️ PASO 3: CONFIGURACIÓN DEL ENTORNO (10 minutos)

### 3.1 Crear Archivo .env

```powershell
# Copiar template
Copy-Item .env.example .env

# Editar .env con tu configuración
notepad .env  # O usar tu editor preferido
```

**Configuración mínima en .env:**
```env
MOVISTAR_ENV=development
MOVISTAR_DEBUG=true
MOVISTAR_START_DATE=2025-10-01
MOVISTAR_END_DATE=2025-10-31
MOVISTAR_MAX_WORKERS=4
MOVISTAR_LOG_LEVEL=INFO
```

### 3.2 Verificar Configuración

```powershell
# Crear script de prueba temporal
@"
from src.core.config import get_settings
settings = get_settings()
print(f"✅ Config loaded successfully!")
print(f"   Environment: {settings.env}")
print(f"   Period: {settings.start_date} -> {settings.end_date}")
print(f"   Data dir: {settings.data_dir}")
"@ | python
```

---

## 🔨 PASO 4: CONFIGURAR HERRAMIENTAS DE DESARROLLO (15 minutos)

### 4.1 Configurar Pre-commit

```powershell
# Instalar pre-commit hooks
pre-commit install

# Ejecutar en todos los archivos (primera vez puede tardar)
pre-commit run --all-files

# Nota: Pueden fallar algunas validaciones - es normal
# Se arreglarán automáticamente en futuros commits
```

### 4.2 Configurar VS Code (Opcional pero Recomendado)

Crear `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

---

## 🧪 PASO 5: VERIFICAR INSTALACIÓN CON TESTS (10 minutos)

### 5.1 Crear Test de Integración Básico

```powershell
# Crear tests/test_core_integration.py
New-Item -Force tests/test_core_integration.py
```

Contenido:
```python
"""Integration tests for core components."""
import pytest
from src.core.config import get_settings, reset_settings
from src.core.exceptions import PhoneValidationError
from src.core.models import SaleRecord, TipoLinea
from datetime import datetime, date


def test_settings_loading():
    """Test settings load correctly."""
    settings = get_settings()
    assert settings is not None
    assert settings.env is not None
    assert settings.data_dir.exists()


def test_custom_exceptions():
    """Test custom exceptions work."""
    with pytest.raises(PhoneValidationError) as exc_info:
        raise PhoneValidationError(phone="123", reason="Too short")
    
    assert "123" in str(exc_info.value)
    assert "Too short" in str(exc_info.value)


def test_sale_record_validation():
    """Test SaleRecord validation."""
    # Valid record
    record = SaleRecord(
        telefono_servicio="3001234567",
        nombre_cliente="Juan Perez",
        tipo_venta="TU MASCOTA",
        fecha_venta=date.today(),
        marca_temporal=datetime.now(),
        nombre_asesor="Maria Lopez"
    )
    
    assert record.telefono_servicio == "3001234567"
    assert record.nombre_cliente == "Juan Perez"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 5.2 Ejecutar Tests

```powershell
# Correr tests
pytest tests/test_core_integration.py -v

# Si pasan, todo está bien configurado! ✅
```

---

## 🔗 PASO 6: INTEGRAR CORE EN SISTEMA EXISTENTE (30-60 minutos)

### 6.1 Actualizar main.py

Agregar al inicio de `main.py`:

```python
# Importar nuevo sistema de configuración
from src.core.config import get_settings
from src.core.exceptions import (
    ConfigurationError,
    FileNotFoundError,
    ProcessingError
)
from src.core.decorators import timing, retry, log_execution

# Obtener settings
settings = get_settings()

# Reemplazar constantes antiguas
INPUT_DIR = settings.input_dir
OUTPUT_DIR = settings.output_dir
START_DATE = settings.start_date
END_DATE = settings.end_date
```

### 6.2 Agregar Decorators a Funciones Críticas

Ejemplo en `src/data_loader.py`:

```python
from src.core.decorators import retry, timing

class CSVLoader:
    @staticmethod
    @retry(max_attempts=3)
    @timing
    def load_csv(file_path: Path, ...):
        # Código existente
        ...
```

### 6.3 Usar Custom Exceptions

Reemplazar en todo el código:

```python
# Antes
raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

# Después
from src.core.exceptions import FileNotFoundError
raise FileNotFoundError(file_path=str(file_path))
```

---

## ✅ PASO 7: VALIDACIÓN FINAL (10 minutos)

### 7.1 Ejecutar Pipeline Completo

```powershell
# Ejecutar main.py con datos de prueba
python main.py

# Debería ejecutarse sin errores
```

### 7.2 Verificar Outputs

```powershell
# Verificar que se generaron archivos
Get-ChildItem data/output/ | Select-Object Name, Length, LastWriteTime

# Verificar logs
Get-Content -Tail 50 logs/pipeline_*.log
```

### 7.3 Ejecutar Suite de Tests Completa

```powershell
# Todos los tests
pytest

# Con coverage
pytest --cov=src --cov-report=html

# Ver reporte
Invoke-Item htmlcov/index.html
```

---

## 📝 PASO 8: COMMIT Y DOCUMENTACIÓN (10 minutos)

### 8.1 Review de Cambios

```powershell
# Ver archivos modificados
git status

# Ver diff
git diff
```

### 8.2 Commit Estructurado

```powershell
# Stage changes
git add .

# Commit con mensaje descriptivo
git commit -m "refactor: implement enterprise-grade core architecture

- Add Pydantic Settings with environment variable support
- Implement custom exception hierarchy
- Create domain models with validation
- Add utility decorators (retry, timing, logging)
- Configure development tools (pytest, mypy, pre-commit)
- Clean up 10+ temporary validation scripts
- Update dependencies and requirements

BREAKING CHANGES:
- Configuration now uses Settings class instead of module-level constants
- FileNotFoundError now custom exception (not builtin)

See REFACTORIZACION_PROFESIONAL.md for detailed plan.
See RESUMEN_REFACTORIZACION.md for summary."

# Push a rama
git push origin refactor/enterprise-architecture
```

---

## 🎯 SIGUIENTE FASE: REFACTORIZACIÓN GRADUAL

### Semana 1-2: Consolidación
- [ ] Migrar todos los imports a usar nuevo core
- [ ] Agregar decorators a funciones existentes
- [ ] Escribir tests para módulos críticos

### Semana 3-4: Repository Pattern
- [ ] Implementar src/infrastructure/repositories/
- [ ] Migrar data_loader a usar repositories
- [ ] Crear adapters reutilizables

### Semana 5-6: Use Cases
- [ ] Implementar src/application/use_cases/
- [ ] Refactorizar data_processor
- [ ] Agregar dependency injection

---

## 🆘 TROUBLESHOOTING

### Error: "Module not found: pydantic_settings"
```powershell
pip install pydantic-settings
```

### Error: "Pre-commit hooks failing"
```powershell
# Desactivar temporalmente
git commit --no-verify -m "..."

# O actualizar hooks
pre-commit autoupdate
```

### Error: "Tests failing"
```powershell
# Ver detalles
pytest -vv --tb=long

# Ejecutar test específico
pytest tests/test_core_integration.py::test_settings_loading -v
```

### Error: "Import errors"
```powershell
# Verificar PYTHONPATH
$env:PYTHONPATH = (Get-Location).Path
python -c "import sys; print('\n'.join(sys.path))"
```

---

## 📊 CHECKLIST FINAL

### Setup Inicial
- [ ] ✅ Backup creado (commit + tag)
- [ ] ✅ Rama de refactorización creada
- [ ] ✅ Archivos de config aplicados (.gitignore, requirements)
- [ ] ✅ Scripts temporales eliminados
- [ ] ✅ Dependencies instaladas

### Configuración
- [ ] ✅ .env creado y configurado
- [ ] ✅ Pre-commit hooks instalados
- [ ] ✅ VS Code configurado (opcional)
- [ ] ✅ Tests ejecutándose

### Integración
- [ ] ✅ main.py actualizado con nuevo config
- [ ] ✅ Decorators agregados a funciones críticas
- [ ] ✅ Custom exceptions en uso
- [ ] ✅ Pipeline ejecutándose correctamente

### Validación
- [ ] ✅ Tests pasando
- [ ] ✅ Coverage reportado
- [ ] ✅ Archivos de output generados
- [ ] ✅ Logs sin errores

### Documentación
- [ ] ✅ Cambios commiteados
- [ ] ✅ Documentación actualizada
- [ ] ✅ Team informado

---

## 🎓 RECURSOS ADICIONALES

### Documentación Creada
1. `REFACTORIZACION_PROFESIONAL.md` - Plan completo
2. `RESUMEN_REFACTORIZACION.md` - Resumen ejecutivo
3. Este archivo - Guía de implementación

### Archivos Core
- `src/core/config.py` - Settings
- `src/core/exceptions.py` - Exceptions
- `src/core/models.py` - Models
- `src/core/decorators.py` - Decorators

### Referencias Externas
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- Pytest: https://docs.pytest.org/
- Pre-commit: https://pre-commit.com/

---

## ✉️ SOPORTE

Si encuentras problemas:
1. Revisa la sección Troubleshooting arriba
2. Consulta `REFACTORIZACION_PROFESIONAL.md`
3. Revisa logs en `logs/`
4. Crea un issue en el repositorio

---

**¡Felicitaciones! 🎉**

Has completado el setup inicial de la refactorización enterprise-grade del Sistema Movistar.

El sistema ahora tiene:
- ✅ Configuración profesional con Pydantic
- ✅ Manejo de errores robusto
- ✅ Modelos validados
- ✅ Decorators útiles
- ✅ Testing framework configurado
- ✅ Code quality tools activos

**Próximo paso:** Comenzar la integración gradual siguiendo el plan en `REFACTORIZACION_PROFESIONAL.md`

---

_Guía creada el 3 de Noviembre 2025_  
_Por: Senior Data Analytics Engineer_
