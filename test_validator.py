import pandas as pd
from src.services.phone_validator import EnhancedPhoneValidator

# Probar validador con números 957
validator = EnhancedPhoneValidator()

test_numbers = [
    '9573135538913',  # Del CSV
    '9573043649090',
    '3001234567',
    '6012345678'
]

print("=== PRUEBA DE VALIDADOR ===\n")
for num in test_numbers:
    result = validator.validate(num)
    print(f"Número: {num}")
    print(f"  Válido: {result.is_valid}")
    print(f"  Limpio: {result.cleaned_phone}")
    print(f"  Tipo: {result.tipo_linea}")
    print(f"  Razón: {result.reason}")
    print()
