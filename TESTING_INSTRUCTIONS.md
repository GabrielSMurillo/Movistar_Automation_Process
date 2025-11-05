# 🧪 Testing Instructions - Movistar ETL Pipeline

**Date**: November 5, 2025  
**Version**: 2.0 (Fixed)

---

## 📋 **PRE-TESTING SETUP**

### 1. Install Dependencies

```bash
cd /workspace

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python3 -c "import pandas; import pydantic; import openpyxl; print('✅ Dependencies installed')"
```

### 2. Verify Environment

```bash
# Check Python version (requires 3.10+)
python3 --version

# Verify directory structure
ls -la data/input/
ls -la data/output/
ls -la data/tracking/
```

---

## 🔍 **UNIT TESTS**

### Test 1: Phone Validator

```bash
python3 -c "
from src.services.phone_validator import EnhancedPhoneValidator

validator = EnhancedPhoneValidator()

# Test cases
tests = [
    ('3001234567', True, 'MOVIL'),      # Valid mobile
    ('6012345678', True, 'FIJA'),       # Valid landline (Bogotá)
    ('6032345678', True, 'FIJA'),       # Valid landline (Armenia) - NEW
    ('6192345678', True, 'FIJA'),       # Valid landline (Unknown city) - NEW
    ('9573001234567', True, 'MOVIL'),   # 957 prefix handling
    ('5551234567', False, 'INVALIDO'),  # Invalid (starts with 5)
    ('300123456', False, 'INVALIDO'),   # Too short
]

passed = 0
failed = 0

for phone, expected_valid, expected_type in tests:
    result = validator.validate(phone)
    if result.is_valid == expected_valid and result.tipo_linea == expected_type:
        print(f'✅ {phone} -> {result.tipo_linea}')
        passed += 1
    else:
        print(f'❌ {phone} -> Expected {expected_type}, got {result.tipo_linea}')
        failed += 1

print(f'\nResults: {passed}/{len(tests)} passed')
"
```

**Expected Output**:
```
✅ 3001234567 -> MOVIL
✅ 6012345678 -> FIJA
✅ 6032345678 -> FIJA
✅ 6192345678 -> FIJA
✅ 9573001234567 -> MOVIL
✅ 5551234567 -> INVALIDO
✅ 300123456 -> INVALIDO

Results: 7/7 passed
```

---

### Test 2: Service Code Mapper

```bash
python3 -c "
from src.services.service_code_mapper import ServiceCodeMapper

mapper = ServiceCodeMapper()

# Test cases: (tipo_venta, tipo_linea, expected_code)
tests = [
    ('TU MASCOTA', 'MOVIL', '3823'),
    ('TU MASCOTA', 'FIJA', '15639'),
    ('TU VEHICULO', 'MOVIL', '5002'),
    ('TU VEHICULO', 'FIJA', '15642'),
    ('TU HOGAR', 'MOVIL', '5000'),
    ('TU HOGAR', 'FIJA', '15641'),
    ('TU BIENESTAR', 'MOVIL', '2119'),
    ('TU BIENESTAR', 'FIJA', '15640'),
    ('MASCOTAS', 'DIGITAL', '4046'),
    ('VIAL', 'DIGITAL', '4045'),
]

passed = 0
failed = 0

for tipo_venta, tipo_linea, expected_code in tests:
    code, program = mapper.get_code(tipo_venta, tipo_linea)
    if code == expected_code:
        print(f'✅ {tipo_venta} + {tipo_linea} -> {code}')
        passed += 1
    else:
        print(f'❌ {tipo_venta} + {tipo_linea} -> Expected {expected_code}, got {code}')
        failed += 1

print(f'\nResults: {passed}/{len(tests)} passed')
"
```

**Expected Output**:
```
✅ TU MASCOTA + MOVIL -> 3823
✅ TU MASCOTA + FIJA -> 15639
✅ TU VEHICULO + MOVIL -> 5002
✅ TU VEHICULO + FIJA -> 15642
✅ TU HOGAR + MOVIL -> 5000
✅ TU HOGAR + FIJA -> 15641
✅ TU BIENESTAR + MOVIL -> 2119
✅ TU BIENESTAR + FIJA -> 15640
✅ MASCOTAS + DIGITAL -> 4046
✅ VIAL + DIGITAL -> 4045

Results: 10/10 passed
```

---

### Test 3: Excel Sanitizer

```bash
python3 -c "
from src.utils.excel_sanitizer import sanitize_value, is_potentially_dangerous

# Test sanitization
tests = [
    ('=1+1', \"'=1+1\", True),
    ('+cmd', \"'+cmd\", True),
    ('-test', \"'-test\", True),
    ('@ref', \"'@ref\", True),
    ('normal', 'normal', False),
    ('3001234567', '3001234567', False),
]

passed = 0
failed = 0

for input_val, expected_output, expected_dangerous in tests:
    output = sanitize_value(input_val)
    dangerous = is_potentially_dangerous(input_val)
    
    if output == expected_output and dangerous == expected_dangerous:
        print(f'✅ {repr(input_val):20} -> {repr(output):20} (dangerous={dangerous})')
        passed += 1
    else:
        print(f'❌ {repr(input_val)} failed')
        failed += 1

print(f'\nResults: {passed}/{len(tests)} passed')
"
```

**Expected Output**:
```
✅ '=1+1'              -> \"'=1+1\"             (dangerous=True)
✅ '+cmd'              -> \"'+cmd\"             (dangerous=True)
✅ '-test'             -> \"'-test\"            (dangerous=True)
✅ '@ref'              -> \"'@ref\"             (dangerous=True)
✅ 'normal'            -> 'normal'            (dangerous=False)
✅ '3001234567'        -> '3001234567'        (dangerous=False)

Results: 6/6 passed
```

---

### Test 4: Validation Caching

```bash
python3 -c "
from src.services.phone_validator import EnhancedPhoneValidator
import time

validator = EnhancedPhoneValidator(enable_cache=True)

# Simulate processing with duplicate phones
phones = ['3001234567', '3009876543', '6012345678'] * 100  # 300 total, 3 unique

# First pass
start = time.time()
for phone in phones:
    validator.validate(phone)
first_pass = time.time() - start

# Second pass (should hit cache)
start = time.time()
for phone in phones:
    validator.validate(phone)
second_pass = time.time() - start

stats = validator.get_cache_stats()

print(f'✅ Caching Performance Test')
print(f'   First pass:  {first_pass*1000:.2f}ms ({len(phones)} validations)')
print(f'   Second pass: {second_pass*1000:.2f}ms ({len(phones)} validations)')
print(f'   Speedup:     {first_pass/second_pass:.1f}x')
print(f'   Cache hits:  {stats[\"hits\"]:,}')
print(f'   Cache misses: {stats[\"misses\"]:,}')
print(f'   Hit rate:    {stats[\"hit_rate_pct\"]:.1f}%')
print(f'   Cache size:  {stats[\"cache_size\"]} unique phones')

# Verify speedup
if first_pass / second_pass > 2.0:
    print(f'\n✅ Cache working correctly (2x+ speedup achieved)')
else:
    print(f'\n⚠️  Cache speedup lower than expected')
"
```

**Expected Output**:
```
✅ Caching Performance Test
   First pass:  45.23ms (300 validations)
   Second pass: 8.12ms (300 validations)
   Speedup:     5.6x
   Cache hits:  297
   Cache misses: 3
   Hit rate:    99.0%
   Cache size:  3 unique phones

✅ Cache working correctly (2x+ speedup achieved)
```

---

## 🔬 **INTEGRATION TESTS**

### Test 5: Import Chain

```bash
python3 -c "
print('Testing import chain...')

# Test main imports
from src.domain.processors import (
    TipificadorProcessor,
    DigitalProcessor,
    HistoricalSalesProcessor,
    consolidate_monthly_report
)
print('✅ Processor imports successful')

# Test service imports
from src.services.phone_validator import EnhancedPhoneValidator
from src.services.service_code_mapper import ServiceCodeMapper
from src.services.field_validators import FieldValidators
from src.services.novelty_detector import NoveltyDetector
print('✅ Service imports successful')

# Test utility imports
from src.utils.excel_sanitizer import sanitize_for_excel
print('✅ Utility imports successful')

# Test generator imports
from src.generators.contact_log_generator import ContactLogGenerator
print('✅ Generator imports successful')

print('\n✅ All imports successful - no circular dependencies')
"
```

---

### Test 6: End-to-End Processor Test (Requires Sample Data)

```bash
python3 -c "
import pandas as pd
from datetime import date
from src.domain.processors import TipificadorProcessor

# Create minimal test data
test_data = {
    'Marca temporal': ['2025-11-01 10:00:00', '2025-11-01 11:00:00'],
    'Nombre del asesor': ['Juan Pérez', 'María García'],
    'BASE ASIGNADA': ['MOVIL', 'FIJA'],
    'Nombre del cliente': ['Cliente 1', 'Cliente 2'],
    'TELEFONO DEL CLIENTE( DONDE SE VA CARGAR EL SERVICIO )': ['3001234567', '6012345678'],
    'TIPO DE VENTA': ['TU MASCOTA', 'TU VEHICULO'],
    '¿LA VENTA PROVIENE DE UN REFERIDO?': ['No', 'No'],
    'LOGIN': ['12345', '67890'],
}

df_test = pd.DataFrame(test_data)

# Column mapping
cols_map = {
    'Marca temporal': 'marca_temporal',
    'Nombre del asesor': 'nombre_asesor',
    'BASE ASIGNADA': 'base_asignada',
    'Nombre del cliente': 'nombre_cliente',
    'TELEFONO DEL CLIENTE( DONDE SE VA CARGAR EL SERVICIO )': 'telefono_servicio',
    'TIPO DE VENTA': 'tipo_venta',
    '¿LA VENTA PROVIENE DE UN REFERIDO?': 'es_referido',
    'LOGIN': 'login',
}

# Process
start_date = date(2025, 11, 1)
end_date = date(2025, 11, 30)

df_ventas, df_referidos, metrics = TipificadorProcessor.process(
    df_test,
    cols_map,
    start_date,
    end_date
)

print(f'✅ Processing completed')
print(f'   Input records: {metrics[\"total_raw\"]}')
print(f'   Valid records: {metrics[\"total_valid\"]}')
print(f'   Novedad records: {metrics[\"total_novedades\"]}')
print(f'   MOVIL count: {metrics[\"movil_count\"]}')
print(f'   FIJA count: {metrics[\"fija_count\"]}')

# Verify data
if not df_ventas.empty:
    print(f'\n✅ Output DataFrame structure:')
    print(f'   Columns: {list(df_ventas.columns)}')
    print(f'   Shape: {df_ventas.shape}')
    
    # Check critical columns
    required_cols = ['telefono_limpio', 'tipo_linea', 'cod_servicio', 'programa']
    missing = [col for col in required_cols if col not in df_ventas.columns]
    
    if not missing:
        print(f'✅ All critical columns present')
        
        # Verify service codes
        for idx, row in df_ventas.iterrows():
            print(f'   Record {idx}: {row[\"tipo_linea\"]} -> code {row[\"cod_servicio\"]}')
    else:
        print(f'❌ Missing columns: {missing}')
else:
    print(f'⚠️  Warning: Output DataFrame is empty')
"
```

**Expected Output**:
```
✅ Processing completed
   Input records: 2
   Valid records: 2
   Novedad records: 0
   MOVIL count: 1
   FIJA count: 1

✅ Output DataFrame structure:
   Columns: ['telefono_limpio', 'tipo_linea', 'cod_servicio', 'programa', ...]
   Shape: (2, 25)
✅ All critical columns present
   Record 0: MOVIL -> code 3823
   Record 1: FIJA -> code 15642
```

---

## 🚀 **FULL PIPELINE TEST**

### Test 7: Run Complete Pipeline (Requires Real Data)

```bash
# Ensure input files exist
ls -la data/input/*.csv

# Run pipeline
python3 main.py

# Check outputs
ls -la data/output/*_Ejecutado_Periodo_*/
```

**Success Indicators**:
- ✅ Pipeline completes without errors
- ✅ ~11 Excel files generated
- ✅ Contact Log file created
- ✅ No critical validation errors
- ✅ Execution time <10 seconds for 3,700 records

---

## 📊 **PERFORMANCE BENCHMARKS**

### Expected Performance (3,700 records):

| Metric | Before Fixes | After Fixes | Target |
|--------|--------------|-------------|--------|
| Total Time | ~9 seconds | ~5-6 seconds | <5 seconds |
| Records/sec | 411 | 620-740 | >740 |
| Valid Records | ~70% | ~99% | >95% |
| Cache Hit Rate | N/A | 60-80% | >50% |
| Execution | ❌ Blocked | ✅ Works | ✅ Works |

---

## 🐛 **TROUBLESHOOTING**

### Issue: Import Errors
```bash
# Solution: Install dependencies
pip install pandas pydantic openpyxl xlsxwriter
```

### Issue: File Not Found
```bash
# Solution: Create required directories
mkdir -p data/input data/output data/processed data/tracking logs
```

### Issue: Column Mapping Errors
```bash
# Solution: Verify CSV column names match TIPIFICADOR_COLS_MAP in config.py
python3 -c "from config import TIPIFICADOR_COLS_MAP; print(TIPIFICADOR_COLS_MAP)"
```

### Issue: Low Cache Hit Rate
```bash
# Explanation: Normal if all phone numbers are unique
# High cache hit rate (60-80%) expected only with duplicate phones
```

---

## ✅ **TEST COMPLETION CHECKLIST**

- [ ] Dependencies installed
- [ ] Unit Test 1: Phone Validator (7/7 passed)
- [ ] Unit Test 2: Service Code Mapper (10/10 passed)
- [ ] Unit Test 3: Excel Sanitizer (6/6 passed)
- [ ] Unit Test 4: Validation Caching (speedup achieved)
- [ ] Integration Test 5: Import Chain (all successful)
- [ ] Integration Test 6: Processor Test (output valid)
- [ ] Full Pipeline Test 7: Complete execution (all files generated)

**When All Tests Pass**: ✅ Code is ready for production deployment

---

**Testing Guide Created**: November 5, 2025  
**For Version**: 2.0 (Fixed)  
**Next Update**: After production deployment
