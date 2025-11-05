"""
Generators package for file generation.

This package provides specialized generators for creating Movistar-formatted
output files. All generators implement the BaseGenerator interface and are
registered with the GeneratorFactory for dynamic instantiation.

Available Generators:
 - ContactLogGenerator: Contact log files
 - FormatoMovistarGenerator: Main Movistar format files
 - SVASGenerator: SVAS files (Digital, Fija, Movil)
 - MonthlyReportGenerator: Monthly consolidated reports

Usage:
 >>> from src.generators import GeneratorFactory
 >>> generator = GeneratorFactory.create('contact_log')
 >>> success = generator.generate(df, output_path)
"""

# Import base classes
from src.generators.base_generator import (
 BaseGenerator,
 GeneratorFactory,
 GeneratorRegistry
)

# Import concrete generators (auto-registers with GeneratorRegistry)
from src.generators.contact_log_generator import ContactLogGenerator
from src.generators.formato_movistar_generator import FormatoMovistarGenerator
from src.generators.svas_generator import SVASGenerator
from src.generators.monthly_report_generator import MonthlyReportGenerator

# Export public API
__all__ = [
 # Base classes
 'BaseGenerator',
 'GeneratorFactory',
 'GeneratorRegistry',
 # Concrete generators
 'ContactLogGenerator',
 'FormatoMovistarGenerator',
 'SVASGenerator',
 'MonthlyReportGenerator',
]
