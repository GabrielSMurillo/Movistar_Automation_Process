"""
Domain models for the Movistar Automation System.

This module defines the core business entities using Pydantic for
runtime validation and type safety.

Models:
 - SaleRecord: Individual sale record
 - ProcessingMetrics: Processing statistics
 - ValidationResult: Validation result
"""

from pydantic import BaseModel, Field, field_validator, computed_field
from datetime import datetime, date
from typing import Optional
from enum import Enum

# ============================================================================
# ENUMERATIONS
# ============================================================================

class TipoLinea(str, Enum):
 """Phone line type."""
 MOVIL = "MOVIL"
 FIJA = "FIJA"
 INVALIDO = "INVALIDO"

class TipoVenta(str, Enum):
 """Sales type/product."""
 MASCOTA = "TU MASCOTA"
 VEHICULO = "TU VEHICULO"
 HOGAR = "TU HOGAR"
 VIAL = "VIAL"
 BIENESTAR = "TU BIENESTAR"

class DuplicateStatus(str, Enum):
 """Duplicate detection status."""
 ORIGINAL = "original"
 DUPLICATE = "duplicado"

class BaseAsignada(str, Enum):
 """Assigned base/channel."""
 DIGITAL = "DIGITAL"
 FIJA = "FIJA"
 MOVIL = "MOVIL"

class EstadoRegistro(str, Enum):
 """Record processing status."""
 VALIDO = "válido"
 INVALIDO = "inválido"
 RECHAZADO = "rechazado"
 PENDIENTE = "pendiente"

# ============================================================================
# CORE MODELS
# ============================================================================

class SaleRecord(BaseModel):
 """
 Core sales record model with validation.
 
 Represents a single validated sale record with all required
 fields and business logic.
 
 Attributes:
 telefono_servicio: Original phone number
 telefono_limpio: Cleaned phone number (10 digits)
 nombre_cliente: Customer name
 documento_cliente: Customer ID document
 tipo_venta: Type of sale/product
 fecha_venta: Sale date
 hora_venta: Sale time
 marca_temporal: Original timestamp
 nombre_asesor: Sales agent name
 login_asesor: Sales agent login ID
 base_asignada: Assigned base/channel
 tipo_linea: Line type (MOVIL/FIJA)
 cod_servicio: Service code
 programa: Program name
 costo_plan: Plan cost
 direccion_cliente: Customer address
 es_referido: Is from referral
 duplicate_status: Duplicate detection status
 is_empaquetado: Is bundled sale
 cantidad_planes: Number of plans
 """
 
 # ===== IDENTIFICADORES =====
 telefono_servicio: str = Field(..., min_length=7, max_length=15)
 telefono_limpio: Optional[str] = Field(default=None, pattern=r'^\d{7,10}$')
 
 # ===== CLIENTE =====
 nombre_cliente: str = Field(..., min_length=1, max_length=200)
 documento_cliente: Optional[str] = Field(default=None, max_length=20)
 direccion_cliente: Optional[str] = Field(default=None)
 correo_cliente: Optional[str] = Field(default=None)
 
 # ===== VENTA =====
 tipo_venta: str # Puede ser TipoVenta enum o string
 fecha_venta: date
 hora_venta: Optional[str] = Field(default=None)
 marca_temporal: datetime
 
 # ===== ASESOR =====
 nombre_asesor: str = Field(..., min_length=1)
 login_asesor: Optional[int] = Field(default=None, ge=1)
 base_asignada: Optional[str] = Field(default=None)
 
 # ===== CLASIFICACIÓN =====
 tipo_linea: Optional[TipoLinea] = Field(default=None)
 cod_servicio: Optional[str] = Field(default=None)
 programa: Optional[str] = Field(default=None)
 
 # ===== FINANCIERO =====
 costo_plan: Optional[str] = Field(default=None)
 
 # ===== CONTROL =====
 duplicate_status: DuplicateStatus = Field(default=DuplicateStatus.ORIGINAL)
 is_empaquetado: bool = Field(default=False)
 cantidad_planes: int = Field(default=1, ge=1)
 is_referido: bool = Field(default=False)
 telefono_referido: Optional[str] = Field(default=None)
 estado: EstadoRegistro = Field(default=EstadoRegistro.VALIDO)
 
 # ===== METADATA =====
 archivo_origen: Optional[str] = Field(default=None)
 fecha_procesamiento: Optional[datetime] = Field(default_factory=datetime.now)
 
 @field_validator('telefono_servicio')
 @classmethod
 def validate_phone_service(cls, v: str) -> str:
 """Validate phone service number."""
 cleaned = ''.join(filter(str.isdigit, v))
 if len(cleaned) not in {7, 10}:
 from src.core.exceptions import PhoneValidationError
 raise PhoneValidationError(
 phone=v,
 reason=f"Invalid length: {len(cleaned)} digits"
 )
 return v
 
 @field_validator('nombre_asesor')
 @classmethod
 def validate_asesor(cls, v: str) -> str:
 """Validate sales agent name."""
 v = v.strip()
 
 if not v or v.lower() in {'n/a', 'na', '#n/a', 'null'}:
 from src.core.exceptions import DataValidationError
 raise DataValidationError(
 message="Invalid agent name",
 details={"name": v}
 )
 
 # Check for numbers in name
 if any(char.isdigit() for char in v):
 from src.core.exceptions import DataValidationError
 raise DataValidationError(
 message="Agent name contains numbers",
 details={"name": v}
 )
 
 return v
 
 @computed_field
 @property
 def is_mobile(self) -> bool:
 """Check if line is mobile."""
 return self.tipo_linea == TipoLinea.MOVIL
 
 @computed_field
 @property
 def is_fixed(self) -> bool:
 """Check if line is fixed."""
 return self.tipo_linea == TipoLinea.FIJA
 
 @computed_field
 @property
 def is_duplicate(self) -> bool:
 """Check if record is duplicate."""
 return self.duplicate_status == DuplicateStatus.DUPLICATE
 
 @computed_field
 @property
 def is_valid(self) -> bool:
 """Check if record is valid."""
 return self.estado == EstadoRegistro.VALIDO
 
 class Config:
 """Pydantic config."""
 use_enum_values = True
 validate_assignment = True
 arbitrary_types_allowed = True

class ProcessingMetrics(BaseModel):
 """
 Metrics for processing results.
 
 Tracks counts and statistics for a processing run.
 """
 
 # ===== COUNTS =====
 total_records: int = Field(..., ge=0)
 valid_records: int = Field(..., ge=0)
 invalid_records: int = Field(default=0, ge=0)
 duplicate_records: int = Field(default=0, ge=0)
 empaquetado_records: int = Field(default=0, ge=0)
 referido_records: int = Field(default=0, ge=0)
 
 # ===== PHONE STATS =====
 movil_count: int = Field(default=0, ge=0)
 fija_count: int = Field(default=0, ge=0)
 invalid_phone_count: int = Field(default=0, ge=0)
 
 # ===== QUALITY METRICS =====
 null_rate: float = Field(default=0.0, ge=0.0, le=1.0)
 duplicate_rate: float = Field(default=0.0, ge=0.0, le=1.0)
 
 # ===== TIMING =====
 processing_time_seconds: Optional[float] = Field(default=None)
 records_per_second: Optional[float] = Field(default=None)
 
 # ===== METADATA =====
 processing_date: datetime = Field(default_factory=datetime.now)
 module_name: Optional[str] = Field(default=None)
 
 @computed_field
 @property
 def rejection_rate(self) -> float:
 """Calculate rejection rate."""
 if self.total_records == 0:
 return 0.0
 return self.invalid_records / self.total_records
 
 @computed_field
 @property
 def success_rate(self) -> float:
 """Calculate success rate."""
 if self.total_records == 0:
 return 0.0
 return self.valid_records / self.total_records
 
 def to_dict(self) -> dict:
 """Convert to dictionary."""
 return self.model_dump()

class ValidationResult(BaseModel):
 """
 Result of a validation operation.
 
 Contains validation status, errors, and warnings.
 """
 
 is_valid: bool
 errors: list[str] = Field(default_factory=list)
 warnings: list[str] = Field(default_factory=list)
 details: dict = Field(default_factory=dict)
 
 def add_error(self, error: str) -> None:
 """Add an error."""
 self.errors.append(error)
 self.is_valid = False
 
 def add_warning(self, warning: str) -> None:
 """Add a warning."""
 self.warnings.append(warning)
 
 @computed_field
 @property
 def has_errors(self) -> bool:
 """Check if has errors."""
 return len(self.errors) > 0
 
 @computed_field
 @property
 def has_warnings(self) -> bool:
 """Check if has warnings."""
 return len(self.warnings) > 0
 
 @computed_field
 @property
 def error_count(self) -> int:
 """Get error count."""
 return len(self.errors)
 
 @computed_field
 @property
 def warning_count(self) -> int:
 """Get warning count."""
 return len(self.warnings)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
 # Enums
 "TipoLinea",
 "TipoVenta",
 "DuplicateStatus",
 "BaseAsignada",
 "EstadoRegistro",
 # Models
 "SaleRecord",
 "ProcessingMetrics",
 "ValidationResult",
]
