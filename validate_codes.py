"""
Script de validación de códigos de servicio.
Verifica que todos los códigos sean correctos según las especificaciones.
"""

from src.services.service_code_mapper import ServiceCodeMapper

def main():
    print("=" * 80)
    print("🔍 VALIDACIÓN DE CÓDIGOS DE SERVICIO")
    print("=" * 80)
    
    mapper = ServiceCodeMapper()
    
    # ========================================
    # CÓDIGOS MOVIL
    # ========================================
    print("\n📱 CÓDIGOS MOVIL:")
    print("-" * 40)
    
    tests_movil = [
        ('TU BIENESTAR', 'MOVIL', '2119'),
        ('TU MASCOTA', 'MOVIL', '3823'),
        ('TU HOGAR', 'MOVIL', '5000'),
        ('TU VEHICULO', 'MOVIL', '5002'),
    ]
    
    passed = 0
    failed = 0
    
    for tipo_venta, tipo_linea, expected_code in tests_movil:
        code, program = mapper.get_code(tipo_venta, tipo_linea)
        
        if code == expected_code:
            print(f"✅ {tipo_venta:15} → {code} ({program})")
            passed += 1
        else:
            print(f"❌ {tipo_venta:15} → {code} (esperado: {expected_code})")
            failed += 1
    
    # ========================================
    # CÓDIGOS FIJA
    # ========================================
    print("\n📞 CÓDIGOS FIJA:")
    print("-" * 40)
    
    tests_fija = [
        ('TU BIENESTAR', 'FIJA', '15640'),
        ('TU MASCOTA', 'FIJA', '15639'),
        ('TU HOGAR', 'FIJA', '15641'),
        ('TU VEHICULO', 'FIJA', '15642'),
    ]
    
    for tipo_venta, tipo_linea, expected_code in tests_fija:
        code, program = mapper.get_code(tipo_venta, tipo_linea)
        
        if code == expected_code:
            print(f"✅ {tipo_venta:15} → {code} ({program})")
            passed += 1
        else:
            print(f"❌ {tipo_venta:15} → {code} (esperado: {expected_code})")
            failed += 1
    
    # ========================================
    # CÓDIGOS DIGITAL
    # ========================================
    print("\n💻 CÓDIGOS DIGITAL:")
    print("-" * 40)
    
    tests_digital = [
        ('MASCOTAS', 'DIGITAL', '4046'),
        ('MULTIASISTENCIA', 'DIGITAL', '4047'),
        ('VIAL', 'DIGITAL', '4045'),
        # También probar con nombres similares
        ('TU MASCOTA', 'DIGITAL', '4046'),  # Debe mapear a MASCOTAS
        ('TU HOGAR', 'DIGITAL', '4047'),    # Debe mapear a MULTIASISTENCIA
    ]
    
    for tipo_venta, tipo_linea, expected_code in tests_digital:
        code, program = mapper.get_code(tipo_venta, tipo_linea)
        
        if code == expected_code:
            print(f"✅ {tipo_venta:15} → {code} ({program})")
            passed += 1
        else:
            print(f"❌ {tipo_venta:15} → {code} (esperado: {expected_code})")
            failed += 1
    
    # ========================================
    # RESUMEN
    # ========================================
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 80)
    print(f"✅ Pasaron: {passed}")
    print(f"❌ Fallaron: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ¡TODOS LOS CÓDIGOS SON CORRECTOS!")
        return 0
    else:
        print(f"\n⚠️  HAY {failed} CÓDIGOS INCORRECTOS - REVISAR")
        return 1


if __name__ == '__main__':
    exit(main())
