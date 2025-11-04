# execution_summary.py
"""
Sistema de checklist y resumen de ejecución.
"""

from dataclasses import dataclass
from typing import List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """Estados posibles de un check."""
    PENDING = "⏳"
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    SKIPPED = "⊘"


@dataclass
class CheckItem:
    """Item individual de checklist."""
    name: str
    status: CheckStatus
    message: str = ""
    details: dict = None


class ExecutionChecklist:
    """Checklist interactivo para validar ejecución del pipeline."""
    
    def __init__(self):
        self.checks: List[CheckItem] = []
    
    def add_check(
        self, 
        name: str, 
        status: CheckStatus, 
        message: str = "",
        details: dict = None
    ):
        """Agrega un check al listado."""
        self.checks.append(CheckItem(name, status, message, details))
    
    def print_summary(self) -> bool:
        """
        Imprime resumen completo de ejecución.
        
        Returns:
            True si todos los checks críticos pasaron
        """
        print("\n" + "=" * 80)
        print("📋 RESUMEN DE EJECUCIÓN DEL PIPELINE")
        print("=" * 80)
        
        # Agrupar por sección
        sections = {
            'Pre-ejecución': [],
            'Ingesta': [],
            'Procesamiento': [],
            'Generación': [],
            'Validación': []
        }
        
        for check in self.checks:
            # Clasificar por nombre
            if 'archivo' in check.name.lower() or 'input' in check.name.lower():
                sections['Pre-ejecución'].append(check)
            elif 'cargad' in check.name.lower() or 'ingesta' in check.name.lower():
                sections['Ingesta'].append(check)
            elif 'procesad' in check.name.lower() or 'validación de datos' in check.name.lower():
                sections['Procesamiento'].append(check)
            elif any(x in check.name.lower() for x in ['.xlsx', 'generado', 'reporte']):
                sections['Generación'].append(check)
            elif 'validación final' in check.name.lower():
                sections['Validación'].append(check)
            else:
                sections['Procesamiento'].append(check)
        
        # Imprimir por sección
        for section, items in sections.items():
            if not items:
                continue
            
            print(f"\n{section}:")
            print("-" * 80)
            
            for check in items:
                status_icon = check.status.value
                msg = f" - {check.message}" if check.message else ""
                print(f"  {status_icon} {check.name}{msg}")
                
                # Mostrar detalles si existen
                if check.details:
                    for key, value in check.details.items():
                        print(f"      • {key}: {value}")
        
        # Contar por estado
        success_count = sum(1 for c in self.checks if c.status == CheckStatus.SUCCESS)
        error_count = sum(1 for c in self.checks if c.status == CheckStatus.ERROR)
        warning_count = sum(1 for c in self.checks if c.status == CheckStatus.WARNING)
        skipped_count = sum(1 for c in self.checks if c.status == CheckStatus.SKIPPED)
        
        print("\n" + "=" * 80)
        print("📊 ESTADÍSTICAS FINALES")
        print("=" * 80)
        print(f"  ✅ Exitosos:    {success_count:>3}")
        print(f"  ⚠️  Advertencias: {warning_count:>3}")
        print(f"  ❌ Errores:     {error_count:>3}")
        print(f"  ⊘  Omitidos:    {skipped_count:>3}")
        print(f"  📝 Total:       {len(self.checks):>3}")
        print("=" * 80)
        
        # Determinar éxito general
        has_errors = error_count > 0
        
        if not has_errors:
            print("\n🎉 PIPELINE EJECUTADO EXITOSAMENTE")
        else:
            print("\n⚠️  PIPELINE COMPLETADO CON ERRORES")
        
        print("=" * 80 + "\n")
        
        return not has_errors
    
    def get_summary_dict(self) -> dict:
        """Retorna resumen como diccionario (útil para logs JSON)."""
        return {
            'total_checks': len(self.checks),
            'success': sum(1 for c in self.checks if c.status == CheckStatus.SUCCESS),
            'warnings': sum(1 for c in self.checks if c.status == CheckStatus.WARNING),
            'errors': sum(1 for c in self.checks if c.status == CheckStatus.ERROR),
            'skipped': sum(1 for c in self.checks if c.status == CheckStatus.SKIPPED),
            'checks': [
                {
                    'name': c.name,
                    'status': c.status.name,
                    'message': c.message,
                    'details': c.details
                }
                for c in self.checks
            ]
        }