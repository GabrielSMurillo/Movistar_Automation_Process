# 🚀 QUICK REFERENCE GUIDE
## Movistar System - Upgraded Version 2.0

**Quick Start**: Copy-paste code examples for immediate use

---

## 📞 1. PHONE VALIDATION (CRITICAL)

### Validate Single Phone
```python
from src.services import EnhancedPhoneValidator

validator = EnhancedPhoneValidator()

# Example: Handle 957 prefix
result = validator.validate('9573001234567')

if result.is_valid:
    print(f"✅ Valid: {result.cleaned_phone}")      # '3001234567'
    print(f"   Type: {result.tipo_linea}")          # 'MOVIL'
    if result.city_name:
        print(f"   City: {result.city_name}")       # For FIJA
else:
    print(f"❌ Invalid: {result.reason}")
```

### Validate DataFrame Column
```python
# Validate entire column
cleaned_phones, metadata = validator.validate_series(df['telefono'])

# Filter valid/invalid
df_valid = df[metadata['es_valido']]
df_invalid = df[~metadata['es_valido']]

# Show rejection stats
print(metadata['motivo_rechazo'].value_counts())
```

---

## 🎯 2. SERVICE CODE MAPPING (CRITICAL)

### Get Correct Code
```python
from src.services import ServiceCodeMapper

mapper = ServiceCodeMapper()

# CRITICAL: Code depends on line type
code, program = mapper.get_code(
    tipo_venta='TU MASCOTA',
    tipo_linea='MOVIL'  # or 'FIJA' or 'DIGITAL'
)

# Examples:
# mapper.get_code('TU MASCOTA', 'MOVIL')   → ('3823', 'TU MASCOTA')
# mapper.get_code('TU MASCOTA', 'FIJA')    → ('15639', 'TU MASCOTA')
# mapper.get_code('MASCOTAS', 'DIGITAL')   → ('4046', 'Mascotas')
```

### Apply to DataFrame
```python
# Apply correct codes to entire DataFrame
def assign_service_code(row):
    code, program = mapper.get_code(
        row['tipo_venta'],
        row['tipo_linea']
    )
    return pd.Series({'codigo_servicio': code, 'programa': program})

df[['codigo_servicio', 'programa']] = df.apply(assign_service_code, axis=1)
```

---

## ✅ 3. NAME & LOGIN VALIDATION

### Validate Names and Logins
```python
from src.services import FieldValidators

validators = FieldValidators()

# Validate asesor name
is_valid, reason = validators.validate_asesor_name('Juan Pérez')
if not is_valid:
    print(f"❌ Asesor: {reason}")

# Validate login
is_valid, reason = validators.validate_login('12345')
if not is_valid:
    print(f"❌ Login: {reason}")

# Validate cliente name
is_valid, reason = validators.validate_cliente_name('Maria Garcia')
if not is_valid:
    print(f"❌ Cliente: {reason}")
```

### Validate Entire Record
```python
# Validate all fields in a record
is_valid, flags, reasons = validators.validate_record(row)

if not is_valid:
    print(f"Invalid record: {'; '.join(reasons)}")
```

---

## 📝 4. GENERATE NOVEDADES FILE

### Create Novedades (Rejected Records)
```python
from src.generators import NovedadesGenerator

# After validation, generate novedades file
generator = NovedadesGenerator()

success = generator.generate(
    df_invalid,  # DataFrame with rejected records
    Path('OCTUBRE_NO_Exitosas_Movistar.xlsx')
)

if success:
    print("✅ Novedades file generated")
```

---

## 📊 5. DATA PROFILING & QUALITY

### Profile Data
```python
from src.analytics import DataProfiler

profiler = DataProfiler()
profile = profiler.profile_dataframe(df, 'Tipificador')

# Show summary
print(f"Quality Score: {profile.quality_score():.1f}/100")
print(f"Rows: {profile.row_count:,}")
print(f"Null Rate: {profile.avg_null_rate:.2%}")
print(f"Duplicates: {profile.duplicate_row_count:,}")

# Export detailed report
profile.export_report(Path('data_profile.xlsx'))
```

### Monitor Quality
```python
from src.analytics import QualityMonitor

monitor = QualityMonitor()
report = monitor.assess_quality(df, 'Tipificador')

# Check for issues
if report.has_critical_issues():
    print(f"🚨 {report.critical_count} critical issues found!")
    for issue in report.critical_issues:
        print(f"  • {issue.description}")
    
    # Export quality report
    report.export_report(Path('quality_report.xlsx'))
else:
    print("✅ No critical quality issues")
```

---

## 🏭 6. COMPLETE PROCESSING PIPELINE

### End-to-End Processing
```python
from src.services import ServiceCodeMapper, EnhancedPhoneValidator, FieldValidators
from src.generators import NovedadesGenerator, GeneratorFactory
from src.analytics import DataProfiler, QualityMonitor
import pandas as pd
from pathlib import Path

# 1. Load data
df = pd.read_excel('tipificador.xlsx')

# 2. Profile input data
profiler = DataProfiler()
input_profile = profiler.profile_dataframe(df, 'Input')
print(f"Input Quality: {input_profile.quality_score():.1f}/100")

# 3. Validate phones
phone_validator = EnhancedPhoneValidator()
cleaned_phones, phone_metadata = phone_validator.validate_series(df['telefono'])

# 4. Validate fields
field_validators = FieldValidators()
validation_results = []

for idx, row in df.iterrows():
    is_valid, flags, reasons = field_validators.validate_record(row, validate_phone=False)
    validation_results.append({
        'is_valid': is_valid and phone_metadata.loc[idx, 'es_valido'],
        'reasons': reasons + ([phone_metadata.loc[idx, 'motivo_rechazo']] if not phone_metadata.loc[idx, 'es_valido'] else [])
    })

df_validation = pd.DataFrame(validation_results)

# 5. Split valid/invalid
df_valid = df[df_validation['is_valid']].copy()
df_invalid = df[~df_validation['is_valid']].copy()
df_invalid['MOTIVO_RECHAZO'] = df_validation[~df_validation['is_valid']]['reasons'].apply(lambda x: '; '.join(x))

print(f"✅ Valid: {len(df_valid):,} ({len(df_valid)/len(df)*100:.1f}%)")
print(f"❌ Invalid: {len(df_invalid):,} ({len(df_invalid)/len(df)*100:.1f}%)")

# 6. Assign correct service codes
service_mapper = ServiceCodeMapper()

for idx, row in df_valid.iterrows():
    code, program = service_mapper.get_code(
        row['tipo_venta'],
        row['tipo_linea']
    )
    df_valid.at[idx, 'codigo_servicio'] = code
    df_valid.at[idx, 'programa'] = program

# 7. Generate client files (valid only)
factory = GeneratorFactory()

# Contact Log
contact_log = factory.create('contact_log')
contact_log.generate(df_valid, Path('output/Contact_Log.xlsx'))

# FORMATO MOVISTAR
formato = factory.create('formato_movistar')
formato.generate(df_valid, Path('output/FORMATO_MOVISTAR.xlsx'))

# SVAS files
svas = factory.create('svas')
svas.generate(df_valid, Path('output/SVAS'))

# 8. Generate novedades file (invalid)
novedades = NovedadesGenerator()
novedades.generate(df_invalid, Path('output/OCTUBRE_NO_Exitosas_Movistar.xlsx'))

# 9. Quality monitoring
monitor = QualityMonitor()
quality_report = monitor.assess_quality(df_valid, 'Validated Data')
quality_report.export_report(Path('output/quality_report.xlsx'))

print("\n✅ Processing complete!")
print(f"   Client files: {len(df_valid):,} records")
print(f"   Novedades: {len(df_invalid):,} records")
```

---

## 🔍 7. DATA LINEAGE & AUDIT

### Track Data Lineage
```python
from src.governance import LineageTracker

tracker = LineageTracker()

# Track load
tracker.track_load('tipificador.xlsx', records=1000)

# Track validation
tracker.track_validation(
    source='tipificador_raw',
    valid_target='tipificador_valid',
    invalid_target='tipificador_novedades',
    records_in=1000,
    valid_count=950,
    invalid_count=50
)

# Track transformation
tracker.track_transformation(
    source='tipificador_valid',
    target='tipificador_processed',
    operation='service_code_mapping',
    records_in=950,
    records_out=950
)

# Export lineage
tracker.export_lineage(Path('lineage/lineage.json'))

# Get summary
summary = tracker.summary()
print(f"Tracked {summary['total_entries']} operations")
```

### Audit Logging
```python
from src.governance import AuditLogger

logger = AuditLogger()

# Log user action
logger.log_user_action(
    action='file_uploaded',
    user='jperez',
    metadata={'filename': 'tipificador.xlsx', 'size_mb': 2.5}
)

# Log data change
logger.log_data_change(
    change_type='validation',
    details={'records_validated': 1000, 'rejected': 50}
)

# Log error
logger.log_error(
    error_type='validation_error',
    error_message='Invalid phone number',
    metadata={'phone': '12345', 'record_id': 123}
)

# Export audit log
logger.export_log(Path('audit_logs/audit.xlsx'))
logger.export_json(Path('audit_logs/audit.json'))

# Get summary
summary = logger.summary()
print(f"Total audit entries: {summary['total_entries']}")
```

---

## 🎯 VALIDATION RULES REFERENCE

### Phone Numbers
```
✅ Valid:
- 3001234567 (MOVIL)
- 6012345678 (FIJA - Bogotá)
- 9573001234567 → 3001234567 (957 prefix handled)

❌ Invalid:
- 12345678 (too short)
- 3991234567 (invalid prefix)
- 6091234567 (invalid city code)
```

### Service Codes
```
MOVIL:
- TU BIENESTAR  → 2119
- TU MASCOTA    → 3823
- TU HOGAR      → 5000
- TU VEHICULO   → 5002

FIJA:
- TU BIENESTAR  → 15640
- TU MASCOTA    → 15639
- TU HOGAR      → 15641
- TU VEHICULO   → 15642

DIGITAL:
- MASCOTAS           → 4046
- MULTIASISTENCIA    → 4047
- VIAL               → 4045
```

### Names & Logins
```
Asesor Name:
✅ Valid: "Juan Pérez", "Maria Garcia"
❌ Invalid: "#N/A", "Juan123", "12345", ""

Login:
✅ Valid: "12345", "987654"
❌ Invalid: "#N/A", "ABC123", "", "N/A"

Cliente Name:
✅ Valid: "Maria Garcia", "Empresa 123 S.A."
❌ Invalid: "#N/A", "", "N/A"
```

---

## 📁 OUTPUT FILES

### For Client (Valid Records Only)
```
output/
├── Contact_Log.xlsx              # All valid sales
├── FORMATO_MOVISTAR.xlsx         # With correct codes
├── SVAS/
│   ├── SVAS_DIG.xlsx            # Digital sales (code 4045/4046/4047)
│   ├── SVAS_FIJA.xlsx           # Landline sales (code 15639-15642)
│   └── SVAS_MOV.xlsx            # Mobile sales (code 2119/3823/5000/5002)
└── Monthly_Reports/
    └── [MES]_Consolidado.xlsx   # Monthly summary
```

### For Operations (Invalid Records)
```
output/
└── [MES]_NO_Exitosas_Movistar.xlsx  # Rejected records with reasons
```

### Quality & Governance
```
output/
├── data_profile.xlsx            # Data profiling report
├── quality_report.xlsx          # Quality assessment
├── lineage/
│   └── lineage.json            # Data lineage
└── audit_logs/
    ├── audit.xlsx              # Audit trail
    └── audit.json              # Audit (JSON)
```

---

## ⚠️ CRITICAL WARNINGS

### 1. ALWAYS Use ServiceCodeMapper
```python
# ❌ WRONG - Hardcoded codes
df['codigo'] = '2119'  # May be wrong for FIJA!

# ✅ CORRECT - Dynamic mapping
mapper = ServiceCodeMapper()
code, program = mapper.get_code(tipo_venta, tipo_linea)
```

### 2. ALWAYS Validate Phones
```python
# ❌ WRONG - No validation
df_valid = df  # May include invalid phones!

# ✅ CORRECT - Validate first
validator = EnhancedPhoneValidator()
cleaned, metadata = validator.validate_series(df['telefono'])
df_valid = df[metadata['es_valido']]
```

### 3. ALWAYS Generate Novedades
```python
# ❌ WRONG - Drop invalid records
df_valid = df[df['telefono'].str.len() == 10]  # Lost invalid!

# ✅ CORRECT - Track invalid
df_valid = df[metadata['es_valido']]
df_invalid = df[~metadata['es_valido']]
novedades_gen.generate(df_invalid, Path('novedades.xlsx'))
```

---

## 🚀 QUICK START COMMANDS

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run processing
python main.py \
    --tipificador data/tipificador.xlsx \
    --digital data/digital.xlsx \
    --output output/

# 3. Check outputs
ls -lh output/

# 4. Review novedades
python -c "
import pandas as pd
df = pd.read_excel('output/OCTUBRE_NO_Exitosas_Movistar.xlsx')
print(df['MOTIVO_RECHAZO'].value_counts())
"

# 5. Check quality
python -c "
from src.analytics import QualityMonitor
import pandas as pd
df = pd.read_excel('data/tipificador.xlsx')
monitor = QualityMonitor()
report = monitor.assess_quality(df)
print(f'Quality Issues: {report.total_issues}')
"
```

---

## 🎯 TESTING CHECKLIST

```python
# Test service codes
from src.services import ServiceCodeMapper
mapper = ServiceCodeMapper()

tests = [
    ('TU MASCOTA', 'MOVIL', '3823'),
    ('TU MASCOTA', 'FIJA', '15639'),
    ('MASCOTAS', 'DIGITAL', '4046'),
    ('TU HOGAR', 'MOVIL', '5000'),
    ('TU HOGAR', 'FIJA', '15641'),
]

for tipo_venta, tipo_linea, expected_code in tests:
    code, _ = mapper.get_code(tipo_venta, tipo_linea)
    assert code == expected_code, f"Failed: {tipo_venta} + {tipo_linea} = {code} (expected {expected_code})"
    print(f"✅ {tipo_venta} + {tipo_linea} = {code}")

print("\n✅ All service code tests passed!")
```

---

**Quick Reference Version**: 2.0  
**Last Updated**: November 4, 2025  
**Status**: Production-Ready
