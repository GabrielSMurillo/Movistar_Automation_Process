# 🚀 Implementation Guide - Refactored Architecture

**Quick Start Guide for Movistar Automation System Refactoring**

---

## 📋 Quick Reference

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **This File** | Quick start, how to run | 🟢 START HERE |
| `REFACTORING_SUMMARY.md` | What was done, summary | After running |
| `ARCHITECTURE_ANALYSIS.md` | Deep dive, full analysis | For understanding |

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Check Your Environment

```bash
# Verify Python version (3.10+)
python --version

# Check if dependencies are installed
pip list | grep pandas
pip list | grep pydantic

# If missing, install
pip install -r requirements.txt
```

### Step 2: Verify Input Files Exist

```bash
# Check input directory
ls data/input/

# You should see:
# ✅ _TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv
# ✅ Reporte de ventas digitales MOVISTAR - Sheet1.csv
```

If files are missing, export them from Google Sheets as CSV.

### Step 3: Run the Refactored System

```bash
# Run new architecture
python main_refactored.py
```

**Expected Output**:
```
================================================================================
🚀 MOVISTAR SALES AUTOMATION - REFACTORED ARCHITECTURE
================================================================================
📅 Period: 23/10/2024 → 31/10/2024
⏰ Start: 2025-11-04 15:30:00
📁 Output: 2025-11-04_Generado_Rango_23-10-2024_al_31-10-2024
================================================================================

🔧 Configuring pipeline...
✅ Pipeline configured with 4 stages

================================================================================
🚀 PIPELINE: Movistar Sales Automation Pipeline
================================================================================
📊 Stages: 4
⏰ Start time: 2025-11-04 15:30:00
================================================================================

[Stage 1/4] Starting: Data Ingestion
================================================================================
🔄 STAGE: Data Ingestion
================================================================================

[1/3] Loading Tipificador...
✅ Tipificador loaded: 365 records
... (more output)
```

### Step 4: Check Outputs

```bash
# Navigate to output directory
cd data/output/2025-11-04_Generado_Rango_23-10-2024_al_31-10-2024/

# List generated files
ls -la

# You should see ~12 files including:
# ✅ Contact Log Movistar Asist_*.xlsx
# ✅ FORMATO MOVISTAR_*.xlsx
# ✅ SVAS_*.xlsx (3 files)
# ✅ FORMATO MOVISTAR_DIGITAL/FIJA/MOVIL_*.xlsx (3 files)
# ✅ OCTUBRE_Exitosas_Movistar.xlsx
# ✅ Tipificador_Novedades_*.xlsx (if any invalid records)
# ✅ Digital_Novedades_*.xlsx (if any invalid records)
```

---

## 📊 System Architecture

### New Layered Architecture

```
┌────────────────────────────────────────────────────────┐
│              main_refactored.py                        │
│         (Entry point, configuration)                    │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│          src/pipeline/orchestrator.py                  │
│    (Pipeline coordinator, stage execution)             │
│                                                         │
│  Stage 1: Ingestion   → Load files                    │
│  Stage 2: Validation  → Validate, clean                │
│  Stage 3: Transform   → Consolidate                    │
│  Stage 4: Output      → Generate files                 │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│          src/domain/processors.py                      │
│    (Business logic, data processing)                   │
│                                                         │
│  • TipificadorProcessor                                │
│  • DigitalProcessor                                    │
│  • HistoricalSalesProcessor                            │
└────────────────────────────────────────────────────────┘
                        ↓
┌────────────────────────────────────────────────────────┐
│          src/services/                                 │
│    (Validators, mappers, business rules)               │
│                                                         │
│  • PhoneValidator                                      │
│  • FieldValidators                                     │
│  • ServiceCodeMapper                                   │
│  • NoveltyDetector                                     │
└────────────────────────────────────────────────────────┘
```

---

## 🔍 Understanding the Pipeline

### Stage 1: Data Ingestion

**Location**: `src/pipeline/stages/ingestion_stage.py`

**What it does**:
1. Loads Tipificador CSV
2. Loads Digital sales CSV
3. Loads Historical sales (if available)
4. Validates file existence and format
5. Stores raw data in pipeline context

**Output**: Raw DataFrames in context

---

### Stage 2: Validation & Processing

**Location**: `src/pipeline/stages/validation_stage_impl.py`

**What it does**:
1. Processes Tipificador data:
   - Validates phones (format, length, prefixes)
   - Validates fields (asesor, login, cliente)
   - Assigns service codes (correct by line type)
   - Separates valid from novedades (invalid)
   - Detects referrals

2. Processes Digital data:
   - Similar validation
   - Assigns digital service codes
   - Marks as DIGITAL channel

3. Processes Historical data:
   - Deduplicates
   - Validates dates

**Output**: 
- Valid records
- Novedades (invalid records)
- Referrals
- Metrics

---

### Stage 3: Transformation & Consolidation

**Location**: `src/pipeline/stages/transformation_stage.py`

**What it does**:
1. Consolidates data from all sources
2. Deduplicates (historical has priority)
3. Creates monthly report

**Priority Order**:
1. Historical (already sent)
2. Current month Tipificador
3. Current month Digital

**Output**: Consolidated monthly DataFrame

---

### Stage 4: Output Generation

**Location**: `src/pipeline/stages/output_stage.py`

**What it does**:
1. Generates Movistar files (5 files):
   - Contact Log
   - FORMATO MOVISTAR
   - 3 SVAS files (DIG/FIJA/MOV)

2. Generates internal files (3 files):
   - FORMATO MOVISTAR_DIGITAL
   - FORMATO MOVISTAR_FIJA
   - FORMATO MOVISTAR_MOVIL

3. Generates monthly report:
   - OCTUBRE_Exitosas_Movistar.xlsx

4. Generates novelty reports (if any):
   - Tipificador_Novedades_*.xlsx
   - Digital_Novedades_*.xlsx

**Output**: All Excel files in output directory

---

## 🛠️ Configuration

### Dates

Edit `config.py` lines 56-57:

```python
START_DATE = date(2024, 10, 23)  # Start date (inclusive)
END_DATE = date(2024, 10, 31)    # End date (inclusive)
```

### Input Files

Edit `config.py` lines 134-150:

```python
TIPIFICADOR_CONFIG = {
    'file_name': '_TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv',
    ...
}

DIGITAL_CONFIG = {
    'file_name': 'Reporte de ventas digitales MOVISTAR - Sheet1.csv',
    ...
}
```

### Output Format

Output files are named automatically based on date range:
- Format: `YYYY-MM-DD_Generado_Rango_DD-MM-YYYY_al_DD-MM-YYYY`
- Example: `2025-11-04_Generado_Rango_23-10-2024_al_31-10-2024`

---

## 📝 Common Tasks

### View Logs

```bash
# Logs are in logs/ directory
tail -f logs/pipeline_20251104.log

# Or view specific sections
grep "ERROR" logs/pipeline_20251104.log
grep "Stage" logs/pipeline_20251104.log
```

### Debug Pipeline

If pipeline fails at a stage, check:

1. **Stage 1 (Ingestion)** fails:
   - Check input files exist
   - Check file format (CSV)
   - Check file encoding (UTF-8)

2. **Stage 2 (Validation)** fails:
   - Check data quality
   - Check column names match expected
   - Review novelty reports

3. **Stage 3 (Transformation)** fails:
   - Check data types
   - Check for missing columns

4. **Stage 4 (Output)** fails:
   - Check output directory permissions
   - Check disk space

### Validate Service Codes

```bash
# Run validation script
python validate_codes.py

# Expected output
🎉 ¡TODOS LOS CÓDIGOS SON CORRECTOS!
```

---

## 🔄 Migration from Old System

### Comparison: Old vs New

| Aspect | Old `main.py` | New `main_refactored.py` |
|--------|---------------|--------------------------|
| **Lines of Code** | 463 | 150 |
| **Architecture** | Monolithic | Layered |
| **Error Handling** | Inconsistent | Standardized |
| **Testability** | Difficult | Easy |
| **Debugability** | Hard | Simple |
| **Maintainability** | Low | High |

### Side-by-Side Execution

Both versions can coexist:

```bash
# Old version (still works)
python main.py

# New version (recommended)
python main_refactored.py

# Compare outputs
diff -r data/output/old_output/ data/output/new_output/
```

### When to Switch

✅ **Switch when**:
- New version tested and validated
- Outputs match expectations
- Team is familiar with new architecture

⏳ **Keep old version while**:
- Testing new version
- Training team
- Building confidence

---

## 🧪 Testing

### Manual Testing

```bash
# 1. Test with sample data
python main_refactored.py

# 2. Check outputs exist
ls data/output/*/

# 3. Open files and verify format
# - Contact Log has correct columns
# - Service codes are correct
# - Novedades separated correctly

# 4. Check metrics in log
grep "Key Metrics" logs/pipeline_*.log
```

### Automated Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

---

## 📊 Key Metrics

After pipeline runs, check these metrics in logs:

```
📊 Key Metrics:
  • Valid ventas: 320         # From tipificador
  • Valid digital: 45         # From digital
  • Novedades: 18            # Invalid records
  • Monthly consolidated: 350 # Total unique
  • Contact log records: 320  # Generated
```

**What to watch**:
- ⚠️  High novedades (>10%) - Check data quality
- ⚠️  Low ventas - Check date range
- ⚠️  Missing files - Check stage logs

---

## 🚨 Troubleshooting

### Error: "Module not found"

```bash
# Solution: Ensure you're in project root
pwd  # Should show /workspace

# Or add to PYTHONPATH
export PYTHONPATH=/workspace:$PYTHONPATH
```

### Error: "File not found"

```bash
# Check input files exist
ls data/input/

# Check permissions
ls -la data/

# Create directories if needed
mkdir -p data/input data/output
```

### Error: "Invalid phone number"

This is expected for some records. They go to novedades file.

Check: `Tipificador_Novedades_*.xlsx`

### Pipeline Hangs

```bash
# Check for infinite loops in logs
tail -f logs/pipeline_*.log

# If stuck, kill and check logs
Ctrl+C
grep "ERROR" logs/pipeline_*.log
```

---

## 📚 Additional Resources

### Documentation Files

1. **ARCHITECTURE_ANALYSIS.md** - Full system analysis
2. **REFACTORING_SUMMARY.md** - What was done
3. **BUSINESS_RULES_IMPLEMENTATION.md** - Business rules
4. **SERVICE_CODE_FIX_SUMMARY.md** - Service code details

### Code Documentation

All modules have comprehensive docstrings:

```python
from src.domain.processors import TipificadorProcessor

# View documentation
help(TipificadorProcessor)
```

---

## ✅ Success Checklist

Before considering migration complete:

- [ ] ✅ Can run `main_refactored.py` without errors
- [ ] ✅ All expected files generated
- [ ] ✅ Service codes are correct (validate with `validate_codes.py`)
- [ ] ✅ Novedades file exists and makes sense
- [ ] ✅ Monthly report consolidated correctly
- [ ] ✅ Contact log has correct format
- [ ] ✅ Outputs match old system (or differences explained)
- [ ] ✅ Team understands new architecture
- [ ] ✅ Documentation reviewed

---

## 🎯 Next Steps

### This Week
1. Test `main_refactored.py` thoroughly
2. Compare with old system outputs
3. Report any issues
4. Build confidence

### Next Week
1. Use as primary system
2. Keep old as backup
3. Train team on new architecture

### Following Weeks
1. Complete remaining refactorings
2. Remove old code
3. Optimize performance

---

## 💡 Pro Tips

### Performance

```bash
# Time execution
time python main_refactored.py

# Monitor memory
python -m memory_profiler main_refactored.py
```

### Debugging

```python
# Add breakpoints in stages
import pdb; pdb.set_trace()

# Or use logging
logger.debug(f"DataFrame shape: {df.shape}")
```

### Data Inspection

```python
# Check data at any stage
# Add to stage:
df.to_csv('debug_output.csv', index=False)
print(df.head())
print(df.dtypes)
```

---

## 📞 Support

### Getting Help

1. Check logs first: `logs/pipeline_*.log`
2. Review documentation: This file + others
3. Check code comments and docstrings
4. Search for similar issues in git history

### Reporting Issues

Include:
- What you were trying to do
- Full error message
- Relevant log excerpts
- Steps to reproduce

---

## 🎉 You're Ready!

You now have:
- ✅ Clean, modern architecture
- ✅ Fixed critical issues
- ✅ Clear data pipeline
- ✅ Comprehensive documentation
- ✅ Path forward for improvements

**Next**: Run `python main_refactored.py` and see it in action! 🚀

---

**Created**: November 4, 2025  
**Version**: 1.0  
**Status**: Ready for Testing ✅
