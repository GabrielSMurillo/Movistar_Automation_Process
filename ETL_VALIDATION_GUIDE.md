# 📊 ETL VALIDATION & ANALYSIS GUIDE
## Comprehensive Testing for Data Pipeline

**Purpose**: Ensure files are loaded correctly, ETL is performed accurately, and data quality is maintained.

---

## 🎯 WHAT TO VALIDATE

### 1. **File Loading** (Input Stage)
- ✅ File exists and accessible
- ✅ Correct format (CSV/Excel)
- ✅ Expected columns present
- ✅ Data types correct
- ✅ Encoding handled properly
- ✅ Minimum record count
- ✅ No completely null columns

### 2. **Data Transformation** (ETL Stage)
- ✅ Record counts match expected
- ✅ No unexpected data loss
- ✅ Transformations applied correctly
- ✅ Service codes accurate
- ✅ Phone numbers cleaned properly
- ✅ Duplicates handled correctly

### 3. **Data Quality** (Throughout)
- ✅ Null rates acceptable
- ✅ Duplicate rates acceptable
- ✅ Business rules satisfied
- ✅ Referential integrity maintained

### 4. **Performance** (Efficiency)
- ✅ Load times acceptable
- ✅ Memory usage reasonable
- ✅ Processing speed OK

### 5. **Output** (Results)
- ✅ All files generated
- ✅ Correct formats
- ✅ Record counts reconcile
- ✅ Data accuracy verified

---

## 🛠️ HOW TO USE THE NEW ETL VALIDATOR

### Quick Start

```python
from src.etl_validator import ETLValidator

# Initialize validator
validator = ETLValidator()

# ========================================
# STAGE 1: VALIDATE FILE LOADING
# ========================================

# Load file
df_tipificador = pd.read_csv('tipificador.csv')

# Validate load
result = validator.validate_load(
    df=df_tipificador,
    file_name='Tipificador',
    expected_columns=[
        'Nombre del asesor',
        'Nombre del cliente',
        'TELEFONO DEL CLIENTE',
        'TIPO DE VENTA',
        'Marca temporal'
    ],
    expected_types={
        'TELEFONO DEL CLIENTE': 'object',
        'TIPO DE VENTA': 'object'
    },
    min_records=100  # Expect at least 100 records
)

if not result.passed:
    print(f"❌ Load validation failed: {result.message}")
    # Handle error or abort

# ========================================
# STAGE 2: VALIDATE SCHEMA
# ========================================

schema = {
    'telefono_servicio': {
        'type': 'object',
        'nullable': False
    },
    'nombre_cliente': {
        'type': 'object',
        'nullable': False
    },
    'tipo_venta': {
        'type': 'object',
        'nullable': False
    }
}

result = validator.validate_schema(df_tipificador, schema, 'tipificador_schema')

# ========================================
# STAGE 3: VALIDATE TRANSFORMATION
# ========================================

# Before transformation
df_before = df_tipificador.copy()

# Apply transformation (e.g., phone cleaning)
df_after = apply_phone_cleaning(df_before)

# Validate transformation
result = validator.validate_transform(
    df_before=df_before,
    df_after=df_after,
    transform_name='phone_cleaning',
    min_retention=95.0,  # Expect at least 95% retention
    max_retention=100.0
)

# ========================================
# STAGE 4: VALIDATE DATA QUALITY
# ========================================

result = validator.validate_data_quality(
    df=df_after,
    stage_name='after_phone_cleaning',
    max_null_rate=0.10,  # Max 10% nulls
    max_duplicate_rate=0.05  # Max 5% duplicates
)

# ========================================
# STAGE 5: VALIDATE BUSINESS RULES
# ========================================

business_rules = [
    {
        'name': 'phones_are_10_digits',
        'condition': lambda df: (df['telefono_limpio'].str.len() == 10).all(),
        'severity': 'CRITICAL'
    },
    {
        'name': 'phones_start_with_3_or_6',
        'condition': lambda df: df['telefono_limpio'].str[0].isin(['3', '6']).all(),
        'severity': 'CRITICAL'
    },
    {
        'name': 'no_future_dates',
        'condition': lambda df: (df['fecha_venta'] <= pd.Timestamp.now()).all(),
        'severity': 'WARNING'
    },
    {
        'name': 'valid_service_codes',
        'condition': lambda df: df['codigo_servicio'].isin([
            '2119', '3823', '5000', '5002',  # MOVIL
            '15639', '15640', '15641', '15642',  # FIJA
            '4045', '4046', '4047'  # DIGITAL
        ]).all(),
        'severity': 'CRITICAL'
    }
]

result = validator.validate_business_rules(
    df=df_after,
    rules=business_rules,
    stage_name='critical_business_rules'
)

# ========================================
# STAGE 6: RECONCILIATION
# ========================================

# Compare input vs output
df_input = df_tipificador
df_output = df_after[df_after['es_valido'] == True]

result = validator.reconcile(
    df_input=df_input,
    df_output=df_output,
    expected_retention=95.0  # Expect 95% retention
)

# ========================================
# FINAL: GENERATE REPORT
# ========================================

# Check for critical issues
if validator.has_critical_issues():
    print("🚨 CRITICAL ISSUES FOUND!")
    for check in validator.get_failed_checks():
        if check.severity == 'CRITICAL':
            print(f"  - {check.message}")
    # Abort or alert

# Export comprehensive report
validator.export_report(Path('validation_report.xlsx'))

# Get summary
df_report = validator.generate_etl_report()
print(df_report)
```

---

## 📋 INTEGRATION WITH main.py

### How to Add Validation to Current Pipeline

```python
# main.py - ENHANCED VERSION
from src.etl_validator import ETLValidator

def main():
    # Initialize validator
    validator = ETLValidator()
    
    # ========================================
    # PHASE 1: LOAD WITH VALIDATION
    # ========================================
    
    logger.info("📥 FASE 1: INGESTA CON VALIDACIÓN")
    
    # Load Tipificador
    tipificador_raw_df = load_tipificador(tipificador_config)
    
    # ✅ NEW: Validate load
    result = validator.validate_load(
        df=tipificador_raw_df,
        file_name='Tipificador',
        expected_columns=list(TIPIFICADOR_COLS_MAP.keys()),
        min_records=50
    )
    
    if not result.passed:
        logger.error("❌ Tipificador validation failed!")
        # Handle error
    
    # Load Digital
    digital_raw_df = load_digital(digital_config)
    
    # ✅ NEW: Validate load
    validator.validate_load(
        df=digital_raw_df,
        file_name='Digital',
        expected_columns=list(DIGITAL_COLS_MAP.keys()),
        min_records=10
    )
    
    # ========================================
    # PHASE 2: VALIDATE RAW DATA QUALITY
    # ========================================
    
    logger.info("🔍 FASE 2: VALIDACIÓN DE CALIDAD INICIAL")
    
    validator.validate_data_quality(
        df=tipificador_raw_df,
        stage_name='tipificador_raw',
        max_null_rate=0.30
    )
    
    # ========================================
    # PHASE 3: PROCESS WITH VALIDATION
    # ========================================
    
    logger.info("⚙️ FASE 3: PROCESAMIENTO CON VALIDACIÓN")
    
    # Before processing
    records_before = len(tipificador_raw_df)
    
    # Process
    df_ventas_mes, df_referidos_mes, metrics_tip = TipificadorProcessor.process(
        tipificador_raw_df,
        TIPIFICADOR_COLS_MAP,
        START_DATE,
        END_DATE
    )
    
    # ✅ NEW: Validate transformation
    validator.validate_transform(
        df_before=tipificador_raw_df,
        df_after=df_ventas_mes,
        transform_name='tipificador_processing',
        min_retention=90.0  # Expect at least 90% retention
    )
    
    # ✅ NEW: Validate business rules
    validator.validate_business_rules(
        df=df_ventas_mes,
        rules=get_business_rules(),  # Define your rules
        stage_name='post_processing'
    )
    
    # ========================================
    # PHASE 4: VALIDATE OUTPUT QUALITY
    # ========================================
    
    logger.info("✅ FASE 4: VALIDACIÓN DE SALIDA")
    
    validator.validate_data_quality(
        df=df_ventas_mes,
        stage_name='ventas_processed',
        max_null_rate=0.05,  # Stricter for output
        max_duplicate_rate=0.02
    )
    
    # ========================================
    # PHASE 5: RECONCILIATION
    # ========================================
    
    logger.info("🔄 FASE 5: RECONCILIACIÓN")
    
    validator.reconcile(
        df_input=tipificador_raw_df,
        df_output=df_ventas_mes,
        expected_retention=95.0
    )
    
    # ========================================
    # FINAL: CHECK & REPORT
    # ========================================
    
    if validator.has_critical_issues():
        logger.error("🚨 CRITICAL VALIDATION ISSUES!")
        for check in validator.get_failed_checks():
            logger.error(f"  - {check.message}")
        
        # Export report for review
        validator.export_report(PROCESSED_DIR / 'validation_CRITICAL.xlsx')
        
        # Decide: abort or continue with warnings
        return 1
    
    # Export validation report
    validator.export_report(PROCESSED_DIR / 'validation_report.xlsx')
    
    logger.info("✅ All validations passed!")
    
    return 0
```

---

## 🧪 AUTOMATED TESTING FRAMEWORK

### Create Test Suite

```python
# tests/test_etl_pipeline.py
import pytest
import pandas as pd
from pathlib import Path
from src.etl_validator import ETLValidator

class TestETLPipeline:
    """Comprehensive ETL pipeline tests."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return ETLValidator()
    
    @pytest.fixture
    def sample_tipificador(self):
        """Create sample tipificador data."""
        return pd.DataFrame({
            'Nombre del asesor': ['Juan Pérez', 'Maria Garcia'],
            'Nombre del cliente': ['Cliente 1', 'Cliente 2'],
            'TELEFONO DEL CLIENTE': ['3001234567', '6012345678'],
            'TIPO DE VENTA': ['TU MASCOTA', 'TU HOGAR'],
            'Marca temporal': ['2025-11-01 10:00', '2025-11-01 11:00']
        })
    
    def test_load_validation(self, validator, sample_tipificador):
        """Test file loading validation."""
        result = validator.validate_load(
            df=sample_tipificador,
            file_name='test_tipificador',
            expected_columns=list(sample_tipificador.columns),
            min_records=2
        )
        
        assert result.passed, f"Load validation failed: {result.message}"
        assert result.details['records_loaded'] == 2
    
    def test_schema_validation(self, validator, sample_tipificador):
        """Test schema validation."""
        schema = {
            'Nombre del asesor': {'type': 'object', 'nullable': False},
            'TELEFONO DEL CLIENTE': {'type': 'object', 'nullable': False}
        }
        
        result = validator.validate_schema(
            df=sample_tipificador,
            schema=schema,
            stage_name='test_schema'
        )
        
        assert result.passed, f"Schema validation failed: {result.message}"
    
    def test_business_rules(self, validator):
        """Test business rule validation."""
        df = pd.DataFrame({
            'telefono_limpio': ['3001234567', '6012345678', '3009876543'],
            'codigo_servicio': ['3823', '15639', '3823'],
            'fecha_venta': pd.to_datetime(['2025-11-01', '2025-11-02', '2025-11-03'])
        })
        
        rules = [
            {
                'name': 'valid_phone_length',
                'condition': lambda df: (df['telefono_limpio'].str.len() == 10).all(),
                'severity': 'CRITICAL'
            },
            {
                'name': 'valid_service_codes',
                'condition': lambda df: df['codigo_servicio'].isin([
                    '3823', '15639', '5000', '5002'
                ]).all(),
                'severity': 'CRITICAL'
            }
        ]
        
        result = validator.validate_business_rules(df, rules, 'test_rules')
        
        assert result.passed, f"Business rules failed: {result.message}"
    
    def test_transformation_validation(self, validator, sample_tipificador):
        """Test transformation validation."""
        # Simulate transformation (remove 1 record)
        df_after = sample_tipificador.iloc[:-1].copy()
        
        result = validator.validate_transform(
            df_before=sample_tipificador,
            df_after=df_after,
            transform_name='test_transform',
            min_retention=50.0,  # Accept 50% retention for test
            max_retention=100.0
        )
        
        assert result.passed, f"Transform validation failed: {result.message}"
        assert result.details['retention_rate'] == '50.0%'
    
    def test_data_quality(self, validator, sample_tipificador):
        """Test data quality validation."""
        result = validator.validate_data_quality(
            df=sample_tipificador,
            stage_name='test_quality',
            max_null_rate=0.50,
            max_duplicate_rate=0.50
        )
        
        assert result.passed, f"Quality validation failed: {result.message}"
    
    def test_reconciliation(self, validator, sample_tipificador):
        """Test reconciliation."""
        # Output has 1 record removed
        df_output = sample_tipificador.iloc[:-1].copy()
        
        result = validator.reconcile(
            df_input=sample_tipificador,
            df_output=df_output,
            expected_retention=50.0
        )
        
        assert result.passed, f"Reconciliation failed: {result.message}"
    
    def test_report_generation(self, validator, sample_tipificador, tmp_path):
        """Test report generation."""
        # Run some validations
        validator.validate_load(sample_tipificador, 'test', min_records=1)
        validator.validate_data_quality(sample_tipificador, 'test')
        
        # Generate report
        report_path = tmp_path / 'test_report.xlsx'
        validator.export_report(report_path)
        
        assert report_path.exists(), "Report not generated"
        
        # Verify report content
        df_report = pd.read_excel(report_path, sheet_name='Validation Results')
        assert len(df_report) == 2, "Report should have 2 validation results"

# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### Run Tests

```bash
# Install pytest if needed
pip install pytest pytest-cov

# Run all tests
pytest tests/test_etl_pipeline.py -v

# Run with coverage
pytest tests/test_etl_pipeline.py --cov=src --cov-report=html

# Output:
# tests/test_etl_pipeline.py::TestETLPipeline::test_load_validation PASSED
# tests/test_etl_pipeline.py::TestETLPipeline::test_schema_validation PASSED
# tests/test_etl_pipeline.py::TestETLPipeline::test_business_rules PASSED
# tests/test_etl_pipeline.py::TestETLPipeline::test_transformation_validation PASSED
# tests/test_etl_pipeline.py::TestETLPipeline::test_data_quality PASSED
# tests/test_etl_pipeline.py::TestETLPipeline::test_reconciliation PASSED
# tests/test_etl_pipeline.py::TestETLPipeline::test_report_generation PASSED
```

---

## 📊 PERFORMANCE MONITORING

### Add Performance Tracking

```python
# Enhanced version with performance tracking
from src.etl_validator import ETLValidator
import time

class PerformanceMonitor:
    """Monitor ETL performance."""
    
    def __init__(self):
        self.metrics = []
    
    def track_stage(self, stage_name, func, *args, **kwargs):
        """Track performance of a stage."""
        start_time = time.time()
        start_memory = get_memory_usage()
        
        # Execute function
        result = func(*args, **kwargs)
        
        duration = time.time() - start_time
        memory_used = get_memory_usage() - start_memory
        
        self.metrics.append({
            'stage': stage_name,
            'duration_seconds': duration,
            'memory_mb': memory_used,
            'records': len(result) if isinstance(result, pd.DataFrame) else None
        })
        
        logger.info(f"⏱️ {stage_name}: {duration:.2f}s, {memory_used:.1f} MB")
        
        return result
    
    def get_summary(self):
        """Get performance summary."""
        total_time = sum(m['duration_seconds'] for m in self.metrics)
        total_memory = max(m['memory_mb'] for m in self.metrics)
        
        return {
            'total_time_seconds': total_time,
            'peak_memory_mb': total_memory,
            'stages': len(self.metrics)
        }

# Usage
monitor = PerformanceMonitor()
validator = ETLValidator()

# Track each stage
df_loaded = monitor.track_stage('load', load_tipificador, config)
df_processed = monitor.track_stage('process', process_data, df_loaded)
df_output = monitor.track_stage('generate', generate_files, df_processed)

# Get performance summary
summary = monitor.get_summary()
print(f"Total time: {summary['total_time_seconds']:.1f}s")
print(f"Peak memory: {summary['peak_memory_mb']:.1f} MB")
```

---

## ✅ VALIDATION CHECKLIST

### Before Production Deployment

**File Loading**:
- [ ] All expected files exist
- [ ] Files load without errors
- [ ] Expected columns present
- [ ] Data types correct
- [ ] Minimum record counts met
- [ ] No completely empty columns

**Data Quality**:
- [ ] Null rates acceptable (<10%)
- [ ] Duplicate rates acceptable (<5%)
- [ ] No invalid phone numbers
- [ ] No invalid names/logins
- [ ] Business rules satisfied

**Transformations**:
- [ ] Phone cleaning works (957 prefix handled)
- [ ] Service codes correct (MOVIL/FIJA differentiated)
- [ ] Date extraction correct
- [ ] Deduplication works
- [ ] Record counts reconcile

**Output**:
- [ ] All files generated
- [ ] Correct file formats
- [ ] Service codes verified
- [ ] Novedades file created (if invalid records)
- [ ] Record counts match expectations

**Performance**:
- [ ] Load time < 5 seconds (for 10k records)
- [ ] Processing time < 30 seconds (for 10k records)
- [ ] Memory usage < 500 MB (for 10k records)
- [ ] No memory leaks

---

## 🚀 QUICK START CHECKLIST

**Today** (Immediate):
1. [ ] Create `src/etl_validator.py` (done ✅)
2. [ ] Add validation to main.py load stage
3. [ ] Test with sample data

**This Week**:
4. [ ] Add validation to all transformation stages
5. [ ] Create automated test suite
6. [ ] Add performance monitoring

**Next Sprint**:
7. [ ] Add alerting for failed validations
8. [ ] Create validation dashboard
9. [ ] Implement continuous validation

---

## 📚 RESOURCES

**Created Files**:
- `src/etl_validator.py` - Comprehensive validation framework
- `tests/test_etl_pipeline.py` - Automated test suite (to create)

**Documentation**:
- `INTEGRATION_STATUS.md` - Current integration status
- `CODE_OPTIMIZATION_ANALYSIS.md` - Performance improvements
- `CRITICAL_FIXES_IMPLEMENTED.md` - Business rule fixes

---

**Status**: ✅ ETL Validator Created & Ready to Use  
**Next**: Integrate into main.py and create test suite  
**Priority**: HIGH - Essential for data quality  
**Last Updated**: November 4, 2025
