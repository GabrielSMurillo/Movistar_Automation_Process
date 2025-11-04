# 🚨 CRITICAL BUSINESS RULES ANALYSIS
## Movistar System - Actual vs Expected Behavior

**Date**: November 4, 2025  
**Priority**: 🔴 CRITICAL - System produces INCORRECT outputs  
**Status**: Issues identified, fixes being implemented

---

## ❌ CRITICAL ISSUE #1: INCORRECT SERVICE CODES

### Current Implementation (WRONG ❌)

```python
# In config.py and file_generator.py - HARDCODED WRONG CODES
SERVICE_CODE_MAPPING = {
    'patterns': [
        (['MASCOTA'], '2119', '4045', 'TU MASCOTA', 'Mascotas'),  # ❌ WRONG!
        (['VEHICULO'], '2120', '4046', 'TU VEHICULO', 'Vehiculo'),  # ❌ WRONG!
        (['HOGAR'], '2121', '4047', 'TU HOGAR', 'Hogar'),  # ❌ WRONG!
    ]
}
```

### Correct Business Rules (REQUIRED ✅)

Service codes are **DIFFERENT** for MOVIL vs FIJA vs DIGITAL:

#### MOVIL (Cellphone - starts with 3)
```
PLAN             CODIGO
TU BIENESTAR     2119
TU MASCOTA       3823
TU HOGAR         5000
TU VEHICULO      5002
```

#### FIJA (Landline - starts with 6)
```
PLAN             CODIGO
TU BIENESTAR     15640
TU HOGAR         15641
TU MASCOTA       15639
TU VEHICULO      15642
```

#### DIGITAL (Online sales)
```
PLAN                CODIGO
MASCOTAS            4046
MULTIASISTENCIA     4047
VIAL                4045
```

### Impact
🚨 **ALL OUTPUT FILES HAVE WRONG SERVICE CODES** - This is sending incorrect data to client!

---

## ❌ CRITICAL ISSUE #2: INCOMPLETE PHONE VALIDATION

### Current Implementation (INCOMPLETE ❌)

```python
# Only checks basic 10 digits
if len(phone) == 10 and phone[0] == '3':
    return 'MOVIL'
```

### Required Validation Rules (COMPLETE ✅)

1. **Handle 957 prefix**: 
   - If number starts with "957", take 10 digits from RIGHT
   - Example: "9573001234567" → "3001234567"

2. **Validate classification**:
   - MOVIL: Starts with 3, exactly 10 digits
   - FIJA: Starts with 6, exactly 10 digits
   - INVALID: Anything else → goes to NOVEDADES

3. **Landline prefix requirement**:
   - If classified as FIJA, MUST have city code prefix
   - Example: "6012345678" (601 = Bogotá)

### Impact
🚨 **Invalid phone numbers are being processed** - Should go to novedades file!

---

## ❌ CRITICAL ISSUE #3: MISSING NOVEDADES FILE

### Current Situation (MISSING ❌)

**No novedades file is generated!**

Invalid records are either:
- Silently dropped
- Incorrectly processed
- Mixed with valid records

### Required Novedades File (NEEDED ✅)

**File**: `[MES]_NO_Exitosas_Movistar.xlsx`

**Structure**: Same as Tipificador + additional columns:
```
- All original Tipificador columns
+ MOTIVO_RECHAZO: String explaining why rejected
+ FECHA_PROCESAMIENTO: When processed
+ ESTADO: "RECHAZADO"
+ VALIDACION_TELEFONO: bool
+ VALIDACION_ASESOR: bool
+ VALIDACION_LOGIN: bool
```

**Rejection Reasons**:
1. Invalid phone number (not 10 digits, wrong prefix)
2. Invalid asesor name (numbers, #N/A, N/A, empty)
3. Invalid login (numbers, #N/A, N/A, empty)
4. Missing required fields

### Impact
🚨 **No visibility into rejected records** - Operations cannot fix issues!

---

## ❌ CRITICAL ISSUE #4: INCOMPLETE NAME/LOGIN VALIDATION

### Current Implementation (BASIC ❌)

```python
# Only checks for numbers in name
if any(char.isdigit() for char in name):
    raise error
```

### Required Validation (COMPLETE ✅)

#### Asesor Name Validation:
```python
INVALID_VALUES = {'#N/A', 'N/A', 'NA', 'n/a', 'na', '', ' '}

def validate_asesor_name(name: str) -> tuple[bool, str]:
    if not name or name.strip() in INVALID_VALUES:
        return False, "Nombre vacío o N/A"
    
    if any(char.isdigit() for char in name):
        return False, "Nombre contiene números"
    
    if len(name.strip()) < 3:
        return False, "Nombre demasiado corto"
    
    return True, ""
```

#### Login Validation:
```python
def validate_login(login: str) -> tuple[bool, str]:
    if not login or str(login).strip() in INVALID_VALUES:
        return False, "Login vacío o N/A"
    
    # Login debe ser numérico
    if not str(login).isdigit():
        return False, "Login no es numérico"
    
    return True, ""
```

### Impact
🚨 **Invalid records being sent to client** - Quality issues!

---

## 📊 CORRECT DATA FLOW

### Expected Flow (REQUIRED)

```
┌─────────────────────────────────────────────────────────────┐
│                      INPUT FILES                             │
├─────────────────────────────────────────────────────────────┤
│  1. Tipificador de Ventas                                   │
│  2. Reporte de Ventas Digitales                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  VALIDATION LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  ✓ Phone validation (3=mobile, 6=landline, 10 digits)      │
│  ✓ Handle 957 prefix (take 10 from right)                  │
│  ✓ Name validation (no numbers, no #N/A)                   │
│  ✓ Login validation (numeric, no #N/A)                     │
│  ✓ Required fields present                                  │
│                                                              │
│  → SPLIT:                                                    │
│     • VALID records → Continue processing                   │
│     • INVALID records → NOVEDADES FILE                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              CLASSIFICATION LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Classify by phone number:                                  │
│  • MOVIL: Starts with 3                                     │
│  • FIJA: Starts with 6                                      │
│  • DIGITAL: From digital file                               │
│                                                              │
│  Assign CORRECT service code based on:                      │
│  • Line type (MOVIL/FIJA/DIGITAL)                          │
│  • Product type (MASCOTA/VEHICULO/HOGAR/BIENESTAR)         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              DEDUPLICATION LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  • Remove duplicates                                         │
│  • Keep only original records                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT FILES                               │
├─────────────────────────────────────────────────────────────┤
│  FOR CLIENT (Valid records only):                           │
│  • Contact Log                                               │
│  • FORMATO MOVISTAR                                          │
│  • SVAS files (DIG, FIJA, MOV)                             │
│  • Monthly reports                                           │
│                                                              │
│  FOR OPERATIONS (Invalid records):                           │
│  • [MES]_NO_Exitosas_Movistar.xlsx (NOVEDADES)             │
│    → Contains all rejected records with reasons             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 REQUIRED FIXES

### Fix 1: Correct Service Code Mapping

**New configuration** (to replace current):

```yaml
# config/service_codes.yaml
service_codes:
  movil:
    TU BIENESTAR:
      code: "2119"
      program: "TU BIENESTAR"
    TU MASCOTA:
      code: "3823"
      program: "TU MASCOTA"
    TU HOGAR:
      code: "5000"
      program: "TU HOGAR"
    TU VEHICULO:
      code: "5002"
      program: "TU VEHICULO"
  
  fija:
    TU BIENESTAR:
      code: "15640"
      program: "TU BIENESTAR"
    TU MASCOTA:
      code: "15639"
      program: "TU MASCOTA"
    TU HOGAR:
      code: "15641"
      program: "TU HOGAR"
    TU VEHICULO:
      code: "15642"
      program: "TU VEHICULO"
  
  digital:
    MASCOTAS:
      code: "4046"
      program: "Mascotas"
    MULTIASISTENCIA:
      code: "4047"
      program: "Multiasistencia"
    VIAL:
      code: "4045"
      program: "Vial"
```

**Python implementation**:

```python
def get_service_code(tipo_venta: str, tipo_linea: str) -> tuple[str, str]:
    """
    Get correct service code based on product AND line type.
    
    Args:
        tipo_venta: Product type (TU MASCOTA, TU VEHICULO, etc.)
        tipo_linea: Line type (MOVIL, FIJA, DIGITAL)
    
    Returns:
        (codigo, programa)
    """
    tipo_venta_upper = tipo_venta.upper()
    tipo_linea_upper = tipo_linea.upper()
    
    # Map product keywords to standard names
    if 'MASCOTA' in tipo_venta_upper:
        product = 'TU MASCOTA'
    elif 'VEHICULO' in tipo_venta_upper or 'VEHÍCULO' in tipo_venta_upper:
        product = 'TU VEHICULO'
    elif 'HOGAR' in tipo_venta_upper:
        product = 'TU HOGAR'
    elif 'BIENESTAR' in tipo_venta_upper:
        product = 'TU BIENESTAR'
    elif 'VIAL' in tipo_venta_upper:
        # VIAL only exists in DIGITAL
        return ('4045', 'Vial')
    elif 'MULTIASISTENCIA' in tipo_venta_upper:
        # MULTIASISTENCIA only in DIGITAL
        return ('4047', 'Multiasistencia')
    else:
        # Default to MASCOTA
        product = 'TU MASCOTA'
    
    # Get code based on line type
    if tipo_linea_upper == 'MOVIL':
        codes = {
            'TU BIENESTAR': ('2119', 'TU BIENESTAR'),
            'TU MASCOTA': ('3823', 'TU MASCOTA'),
            'TU HOGAR': ('5000', 'TU HOGAR'),
            'TU VEHICULO': ('5002', 'TU VEHICULO'),
        }
        return codes.get(product, ('3823', 'TU MASCOTA'))  # Default
    
    elif tipo_linea_upper == 'FIJA':
        codes = {
            'TU BIENESTAR': ('15640', 'TU BIENESTAR'),
            'TU MASCOTA': ('15639', 'TU MASCOTA'),
            'TU HOGAR': ('15641', 'TU HOGAR'),
            'TU VEHICULO': ('15642', 'TU VEHICULO'),
        }
        return codes.get(product, ('15639', 'TU MASCOTA'))  # Default
    
    elif tipo_linea_upper == 'DIGITAL':
        # Map to digital codes
        if 'MASCOTA' in product:
            return ('4046', 'Mascotas')
        elif 'HOGAR' in product:
            return ('4047', 'Multiasistencia')
        elif 'BIENESTAR' in product:
            return ('4047', 'Multiasistencia')
        else:
            return ('4046', 'Mascotas')  # Default
    
    else:
        # Unknown line type
        return ('3823', 'TU MASCOTA')  # Safe default
```

### Fix 2: Enhanced Phone Validation

```python
def validate_and_clean_phone(phone: str) -> tuple[bool, str, str, str]:
    """
    Validate and clean phone number with complete business rules.
    
    Args:
        phone: Raw phone number
    
    Returns:
        (is_valid, cleaned_phone, tipo_linea, rejection_reason)
    """
    if pd.isna(phone) or not phone:
        return False, None, 'INVALIDO', 'Número vacío'
    
    # Clean phone
    cleaned = ''.join(filter(str.isdigit, str(phone)))
    
    # Handle 957 prefix
    if cleaned.startswith('957'):
        # Take 10 digits from RIGHT
        if len(cleaned) > 10:
            cleaned = cleaned[-10:]
        else:
            return False, None, 'INVALIDO', f'Número con 957 inválido: {len(cleaned)} dígitos'
    
    # Validate length
    if len(cleaned) != 10:
        return False, None, 'INVALIDO', f'Longitud incorrecta: {len(cleaned)} dígitos (se requieren 10)'
    
    # Classify and validate
    first_digit = cleaned[0]
    
    if first_digit == '3':
        # MOVIL
        # Validate against known mobile prefixes
        prefix = cleaned[:3]
        valid_mobile_prefixes = {
            '300', '301', '302', '303', '304', '305',
            '310', '311', '312', '313', '314', '315',
            '316', '317', '318', '319', '320', '321',
            '322', '323', '324', '350', '351', '352'
        }
        
        if prefix not in valid_mobile_prefixes:
            return False, None, 'INVALIDO', f'Prefijo móvil no válido: {prefix}'
        
        return True, cleaned, 'MOVIL', ''
    
    elif first_digit == '6':
        # FIJA - landline must have city code
        city_code = cleaned[:3]
        valid_city_codes = {
            '601': 'Bogotá',
            '602': 'Cali',
            '604': 'Medellín',
            '605': 'Cartagena',
            '606': 'Pereira',
            '607': 'Bucaramanga',
            '608': 'Barranquilla',
        }
        
        if city_code not in valid_city_codes:
            return False, None, 'INVALIDO', f'Código de ciudad no válido: {city_code}'
        
        return True, cleaned, 'FIJA', ''
    
    else:
        return False, None, 'INVALIDO', f'Número debe iniciar con 3 (móvil) o 6 (fijo), inicia con: {first_digit}'
```

### Fix 3: Name and Login Validation

```python
INVALID_TEXT_VALUES = {
    '#N/A', '#N/D', '#¡VALOR!', '#¡REF!', '#¡DIV/0!',
    'N/A', 'NA', 'n/a', 'na', 'N.A.', 'n.a.',
    '', ' ', 'null', 'NULL', 'None', 'NONE'
}

def validate_asesor_name(name: str) -> tuple[bool, str]:
    """
    Validate asesor name.
    
    Returns:
        (is_valid, rejection_reason)
    """
    if not name:
        return False, 'Nombre vacío'
    
    name_clean = str(name).strip()
    
    # Check for invalid values
    if name_clean.upper() in {v.upper() for v in INVALID_TEXT_VALUES}:
        return False, f'Nombre inválido: {name}'
    
    # Check for numbers
    if any(char.isdigit() for char in name_clean):
        return False, f'Nombre contiene números: {name}'
    
    # Check minimum length
    if len(name_clean) < 3:
        return False, f'Nombre demasiado corto: {name}'
    
    return True, ''


def validate_login(login: any) -> tuple[bool, str]:
    """
    Validate login (must be numeric).
    
    Returns:
        (is_valid, rejection_reason)
    """
    if pd.isna(login):
        return False, 'Login vacío'
    
    login_str = str(login).strip()
    
    # Check for invalid values
    if login_str.upper() in {v.upper() for v in INVALID_TEXT_VALUES}:
        return False, f'Login inválido: {login}'
    
    # Must be numeric
    if not login_str.isdigit():
        return False, f'Login no numérico: {login}'
    
    # Check reasonable length
    if len(login_str) < 3:
        return False, f'Login demasiado corto: {login}'
    
    return True, ''
```

### Fix 4: Novedades File Generator

```python
class NovedadesGenerator:
    """
    Generator for novedades (rejected records) file.
    
    Creates file with same structure as Tipificador plus rejection info.
    """
    
    def generate(
        self,
        df_rejected: pd.DataFrame,
        output_path: Path
    ) -> bool:
        """
        Generate novedades file.
        
        Args:
            df_rejected: DataFrame with rejected records
            output_path: Output file path
        
        Returns:
            True if successful
        """
        if df_rejected.empty:
            logger.info("No hay registros rechazados - no se genera archivo de novedades")
            return True
        
        # Add rejection metadata
        df_novedades = df_rejected.copy()
        
        # Add/update status columns
        df_novedades['ESTADO'] = 'RECHAZADO'
        df_novedades['FECHA_PROCESAMIENTO'] = datetime.now()
        
        # Ensure rejection reason column exists
        if 'MOTIVO_RECHAZO' not in df_novedades.columns:
            df_novedades['MOTIVO_RECHAZO'] = 'Error no especificado'
        
        # Ensure validation columns exist
        for col in ['VALIDACION_TELEFONO', 'VALIDACION_ASESOR', 'VALIDACION_LOGIN']:
            if col not in df_novedades.columns:
                df_novedades[col] = False
        
        # Save file
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df_novedades.to_excel(writer, sheet_name='Novedades', index=False)
            
            # Format with red header
            workbook = writer.book
            worksheet = writer.sheets['Novedades']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FF0000',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df_novedades.columns):
                worksheet.write(0, col_num, value, header_format)
                max_len = max(
                    df_novedades[value].astype(str).apply(len).max(),
                    len(str(value))
                )
                worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
        
        logger.info(f"✅ Archivo de novedades generado: {len(df_novedades):,} registros rechazados")
        return True
```

---

## 📋 VALIDATION CHECKLIST

For EACH record, validate:

- [ ] ✅ Phone number:
  - [ ] Exactly 10 digits
  - [ ] Starts with 3 (mobile) or 6 (landline)
  - [ ] Valid prefix (300-324, 350-352 for mobile; 601-608 for landline)
  - [ ] Handle 957 prefix correctly

- [ ] ✅ Asesor name:
  - [ ] Not empty
  - [ ] Not #N/A or similar
  - [ ] No numbers
  - [ ] At least 3 characters

- [ ] ✅ Login:
  - [ ] Not empty
  - [ ] Not #N/A or similar
  - [ ] Numeric only
  - [ ] At least 3 digits

- [ ] ✅ Required fields present:
  - [ ] nombre_cliente
  - [ ] tipo_venta
  - [ ] fecha_venta

- [ ] ✅ Service code assignment:
  - [ ] Correct code for MOVIL/FIJA/DIGITAL
  - [ ] Matches tipo_venta exactly
  - [ ] CRITICAL: Do NOT use hardcoded wrong codes!

---

## 🎯 IMMEDIATE ACTIONS REQUIRED

### Priority 1: FIX SERVICE CODES (CRITICAL)
1. Create new service code mapping file
2. Update all generators to use correct codes
3. Test with sample data
4. Validate against actual requirements

### Priority 2: IMPLEMENT COMPLETE VALIDATION
1. Update phone validator
2. Add name/login validators
3. Create validation pipeline stage
4. Split valid/invalid records

### Priority 3: CREATE NOVEDADES FILE
1. Implement NovedadesGenerator
2. Add to output pipeline
3. Test with invalid data
4. Verify format matches Tipificador

### Priority 4: END-TO-END TESTING
1. Test with real Tipificador data
2. Verify service codes are correct
3. Verify novedades file is generated
4. Verify only valid records go to client

---

## 📊 EXPECTED RESULTS AFTER FIX

### Input Files
- Tipificador: 1,000 records
- Digital: 200 records

### After Validation
- Valid: 950 records (95%)
- Invalid (to novedades): 50 records (5%)

### Output Files (Valid Only)
- Contact Log: 950 records
- FORMATO MOVISTAR: 950 records (with CORRECT codes)
- SVAS MOV: 700 records (mobile, code 3823/5000/5002/2119)
- SVAS FIJA: 250 records (landline, code 15639/15641/15642/15640)

### Novedades File (Invalid)
- 50 records with reasons:
  - 20: Invalid phone (wrong prefix, length)
  - 15: Invalid asesor name (#N/A, numbers)
  - 10: Invalid login (#N/A, non-numeric)
  - 5: Missing required fields

---

**Status**: 🔴 CRITICAL FIXES REQUIRED  
**Next**: Implement fixes immediately  
**Testing**: Required before production use
