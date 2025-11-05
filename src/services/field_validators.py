"""
Field Validators for business rules.

Validates:
- Asesor names (no numbers, no #N/A)
- Logins (numeric, no #N/A)
- Required fields presence

Example:
 >>> validators = FieldValidators()
 >>> is_valid, reason = validators.validate_asesor_name('Juan Pérez')
 >>> print(is_valid) # True
 >>> is_valid, reason = validators.validate_asesor_name('#N/A')
 >>> print(is_valid, reason) # False, 'Nombre inválido: #N/A'
"""

from typing import Tuple, Set
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class FieldValidators:
 """
 Validators for business fields.
 
 Validates names, logins, and required fields according to
 business rules.
 """
 
 # Invalid text values (Excel errors, placeholders)
 INVALID_TEXT_VALUES: Set[str] = {
 '#N/A', '#N/D', '#¡VALOR!', '#¡REF!', '#¡DIV/0!', '#NULL!',
 'N/A', 'NA', 'n/a', 'na', 'N.A.', 'n.a.',
 '', ' ', ' ', 'null', 'NULL', 'None', 'NONE', 'none',
 '#NAME?', '#VALUE!', '#REF!', '#DIV/0!',
 }
 
 def __init__(self):
 """Initialize field validators."""
 self.logger = logging.getLogger(f"{__name__}.FieldValidators")
 
 def validate_asesor_name(self, name: any) -> Tuple[bool, str]:
 """
 Validate asesor (agent) name.
 
 Rules:
 - Not empty
 - Not #N/A or similar invalid values
 - No numbers in name
 - At least 3 characters
 
 Args:
 name: Asesor name to validate
 
 Returns:
 Tuple of (is_valid, rejection_reason)
 
 Example:
 >>> validators = FieldValidators()
 >>> validators.validate_asesor_name('Juan Pérez')
 (True, '')
 >>> validators.validate_asesor_name('#N/A')
 (False, 'Nombre inválido: #N/A')
 >>> validators.validate_asesor_name('Juan123')
 (False, 'Nombre contiene números: Juan123')
 """
 if pd.isna(name):
 return False, 'Nombre vacío (NaN)'
 
 name_str = str(name).strip()
 
 # Check if empty
 if not name_str:
 return False, 'Nombre vacío'
 
 # Check for invalid values
 if name_str in self.INVALID_TEXT_VALUES:
 return False, f'Nombre inválido: {name_str}'
 
 # Check case-insensitive
 if name_str.upper() in {v.upper() for v in self.INVALID_TEXT_VALUES}:
 return False, f'Nombre inválido: {name_str}'
 
 # Check for numbers
 if any(char.isdigit() for char in name_str):
 return False, f'Nombre contiene números: {name_str}'
 
 # Check minimum length
 if len(name_str) < 3:
 return False, f'Nombre demasiado corto ({len(name_str)} caracteres): {name_str}'
 
 # Check if mostly special characters
 alpha_count = sum(c.isalpha() for c in name_str)
 if alpha_count < 2:
 return False, f'Nombre no tiene suficientes letras: {name_str}'
 
 return True, ''
 
 def validate_login(self, login: any) -> Tuple[bool, str]:
 """
 Validate login/ID.
 
 Rules:
 - Not empty
 - Not #N/A or similar invalid values
 - Must be numeric
 - At least 3 digits
 
 Args:
 login: Login/ID to validate
 
 Returns:
 Tuple of (is_valid, rejection_reason)
 
 Example:
 >>> validators = FieldValidators()
 >>> validators.validate_login('12345')
 (True, '')
 >>> validators.validate_login('#N/A')
 (False, 'Login inválido: #N/A')
 >>> validators.validate_login('ABC123')
 (False, 'Login no es numérico: ABC123')
 """
 if pd.isna(login):
 return False, 'Login vacío (NaN)'
 
 login_str = str(login).strip()
 
 # Check if empty
 if not login_str:
 return False, 'Login vacío'
 
 # Check for invalid values
 if login_str in self.INVALID_TEXT_VALUES:
 return False, f'Login inválido: {login_str}'
 
 if login_str.upper() in {v.upper() for v in self.INVALID_TEXT_VALUES}:
 return False, f'Login inválido: {login_str}'
 
 # Must be numeric
 if not login_str.replace('.', '').replace(',', '').isdigit():
 return False, f'Login no es numérico: {login_str}'
 
 # Remove decimal points if present (e.g., "12345.0" -> "12345")
 login_clean = login_str.replace('.0', '').replace(',', '')
 
 # Check minimum length
 if len(login_clean) < 3:
 return False, f'Login demasiado corto ({len(login_clean)} dígitos): {login_str}'
 
 return True, ''
 
 def validate_cliente_name(self, name: any) -> Tuple[bool, str]:
 """
 Validate cliente (customer) name.
 
 Similar to asesor validation but allows numbers (for company names).
 
 Args:
 name: Cliente name to validate
 
 Returns:
 Tuple of (is_valid, rejection_reason)
 """
 if pd.isna(name):
 return False, 'Nombre de cliente vacío (NaN)'
 
 name_str = str(name).strip()
 
 # Check if empty
 if not name_str:
 return False, 'Nombre de cliente vacío'
 
 # Check for invalid values
 if name_str in self.INVALID_TEXT_VALUES:
 return False, f'Nombre de cliente inválido: {name_str}'
 
 if name_str.upper() in {v.upper() for v in self.INVALID_TEXT_VALUES}:
 return False, f'Nombre de cliente inválido: {name_str}'
 
 # Check minimum length
 if len(name_str) < 2:
 return False, f'Nombre de cliente demasiado corto: {name_str}'
 
 # Check if has at least some letters
 alpha_count = sum(c.isalpha() for c in name_str)
 if alpha_count < 1:
 return False, f'Nombre de cliente sin letras: {name_str}'
 
 return True, ''
 
 def validate_required_fields(
 self,
 row: pd.Series,
 required_fields: list[str]
 ) -> Tuple[bool, str]:
 """
 Validate that required fields are present and not empty.
 
 Args:
 row: Data row
 required_fields: List of required field names
 
 Returns:
 Tuple of (is_valid, rejection_reason)
 """
 missing_fields = []
 
 for field in required_fields:
 if field not in row:
 missing_fields.append(field)
 continue
 
 value = row[field]
 
 # Check if empty
 if pd.isna(value) or str(value).strip() == '':
 missing_fields.append(field)
 
 if missing_fields:
 return False, f'Campos requeridos faltantes: {", ".join(missing_fields)}'
 
 return True, ''
 
 def validate_record(
 self,
 row: pd.Series,
 validate_phone: bool = True,
 validate_asesor: bool = True,
 validate_login: bool = True,
 validate_cliente: bool = True
 ) -> Tuple[bool, dict[str, bool], list[str]]:
 """
 Validate an entire record.
 
 Args:
 row: Data row to validate
 validate_phone: Include phone validation
 validate_asesor: Include asesor validation
 validate_login: Include login validation
 validate_cliente: Include cliente validation
 
 Returns:
 Tuple of:
 - is_valid: Overall validity
 - validation_flags: Dict of individual validations
 - rejection_reasons: List of rejection reasons
 
 Example:
 >>> validators = FieldValidators()
 >>> row = pd.Series({
 ... 'nombre_asesor': 'Juan Pérez',
 ... 'login_asesor': '12345',
 ... 'nombre_cliente': 'Maria Garcia'
 ... })
 >>> is_valid, flags, reasons = validators.validate_record(row)
 """
 validation_flags = {
 'telefono_valido': True,
 'asesor_valido': True,
 'login_valido': True,
 'cliente_valido': True,
 }
 rejection_reasons = []
 
 # Validate asesor
 if validate_asesor and 'nombre_asesor' in row:
 is_valid, reason = self.validate_asesor_name(row['nombre_asesor'])
 validation_flags['asesor_valido'] = is_valid
 if not is_valid:
 rejection_reasons.append(f"Asesor: {reason}")
 
 # Validate login
 if validate_login and 'login_asesor' in row:
 is_valid, reason = self.validate_login(row['login_asesor'])
 validation_flags['login_valido'] = is_valid
 if not is_valid:
 rejection_reasons.append(f"Login: {reason}")
 
 # Validate cliente
 if validate_cliente and 'nombre_cliente' in row:
 is_valid, reason = self.validate_cliente_name(row['nombre_cliente'])
 validation_flags['cliente_valido'] = is_valid
 if not is_valid:
 rejection_reasons.append(f"Cliente: {reason}")
 
 # Overall validity
 is_valid = all(validation_flags.values())
 
 return is_valid, validation_flags, rejection_reasons

# Export
__all__ = ['FieldValidators']
