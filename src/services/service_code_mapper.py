"""
Service Code Mapper - CRITICAL COMPONENT

Maps product types to correct service codes based on line type.
CRITICAL: Codes are DIFFERENT for MOVIL vs FIJA vs DIGITAL.

Service Codes (MUST BE EXACT):

MOVIL (Cellphone - starts with 3):
    TU BIENESTAR  → 2119
    TU MASCOTA    → 3823
    TU HOGAR      → 5000
    TU VEHICULO   → 5002

FIJA (Landline - starts with 6):
    TU BIENESTAR  → 15640
    TU MASCOTA    → 15639
    TU HOGAR      → 15641
    TU VEHICULO   → 15642

DIGITAL (Online sales):
    MASCOTAS           → 4046
    MULTIASISTENCIA    → 4047
    VIAL               → 4045

Example:
    >>> mapper = ServiceCodeMapper()
    >>> code, program = mapper.get_code('TU MASCOTA', 'MOVIL')
    >>> print(code, program)
    ('3823', 'TU MASCOTA')
    
    >>> code, program = mapper.get_code('TU MASCOTA', 'FIJA')
    >>> print(code, program)
    ('15639', 'TU MASCOTA')
"""

from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class ServiceCodeMapper:
    """
    Maps product types to correct service codes.
    
    CRITICAL: Service codes differ by line type (MOVIL/FIJA/DIGITAL).
    Using wrong codes will cause client rejection of data.
    """
    
    # Service code mappings - CRITICAL: DO NOT MODIFY WITHOUT APPROVAL
    MOVIL_CODES = {
        'TU BIENESTAR': ('2119', 'TU BIENESTAR'),
        'TU MASCOTA': ('3823', 'TU MASCOTA'),
        'TU HOGAR': ('5000', 'TU HOGAR'),
        'TU VEHICULO': ('5002', 'TU VEHICULO'),
    }
    
    FIJA_CODES = {
        'TU BIENESTAR': ('15640', 'TU BIENESTAR'),
        'TU MASCOTA': ('15639', 'TU MASCOTA'),
        'TU HOGAR': ('15641', 'TU HOGAR'),
        'TU VEHICULO': ('15642', 'TU VEHICULO'),
    }
    
    DIGITAL_CODES = {
        'MASCOTAS': ('4046', 'Mascotas'),
        'MULTIASISTENCIA': ('4047', 'Multiasistencia'),
        'VIAL': ('4045', 'Vial'),
    }
    
    # Product keyword mapping
    PRODUCT_KEYWORDS = {
        'TU BIENESTAR': ['BIENESTAR'],
        'TU MASCOTA': ['MASCOTA', 'MASCOTAS', 'PET'],
        'TU HOGAR': ['HOGAR', 'CASA', 'HOME'],
        'TU VEHICULO': ['VEHICULO', 'VEHÍCULO', 'AUTO', 'CARRO', 'VEHICLE'],
    }
    
    def __init__(self):
        """Initialize service code mapper."""
        self.logger = logging.getLogger(f"{__name__}.ServiceCodeMapper")
    
    def get_code(
        self,
        tipo_venta: str,
        tipo_linea: str
    ) -> Tuple[str, str]:
        """
        Get correct service code based on product AND line type.
        
        Args:
            tipo_venta: Product type from Tipificador (e.g., "TU MASCOTA")
            tipo_linea: Line type (MOVIL, FIJA, DIGITAL)
        
        Returns:
            Tuple of (codigo, programa)
            
        Example:
            >>> mapper = ServiceCodeMapper()
            >>> mapper.get_code('TU MASCOTA', 'MOVIL')
            ('3823', 'TU MASCOTA')
            >>> mapper.get_code('TU MASCOTA', 'FIJA')
            ('15639', 'TU MASCOTA')
        """
        if not tipo_venta or not tipo_linea:
            self.logger.warning(f"Missing tipo_venta or tipo_linea: {tipo_venta}, {tipo_linea}")
            return self._get_default_code(tipo_linea)
        
        tipo_venta_upper = str(tipo_venta).upper().strip()
        tipo_linea_upper = str(tipo_linea).upper().strip()
        
        # Normalize product type
        product = self._normalize_product(tipo_venta_upper)
        
        # Get code based on line type
        if tipo_linea_upper == 'MOVIL':
            return self._get_movil_code(product)
        elif tipo_linea_upper == 'FIJA':
            return self._get_fija_code(product)
        elif tipo_linea_upper == 'DIGITAL':
            return self._get_digital_code(tipo_venta_upper)
        else:
            self.logger.error(f"Unknown line type: {tipo_linea}")
            return self._get_default_code('MOVIL')
    
    def _normalize_product(self, tipo_venta: str) -> str:
        """
        Normalize product type to standard name.
        
        Args:
            tipo_venta: Raw product type string
        
        Returns:
            Standardized product name (TU MASCOTA, TU VEHICULO, etc.)
        """
        for product, keywords in self.PRODUCT_KEYWORDS.items():
            if any(keyword in tipo_venta for keyword in keywords):
                return product
        
        # Default to TU MASCOTA
        self.logger.warning(f"Unknown product type: {tipo_venta}, defaulting to TU MASCOTA")
        return 'TU MASCOTA'
    
    def _get_movil_code(self, product: str) -> Tuple[str, str]:
        """Get MOVIL service code."""
        code_info = self.MOVIL_CODES.get(product)
        if code_info:
            self.logger.debug(f"MOVIL: {product} → {code_info[0]}")
            return code_info
        else:
            # Default to TU MASCOTA
            self.logger.warning(f"Product not found in MOVIL codes: {product}, using TU MASCOTA")
            return self.MOVIL_CODES['TU MASCOTA']
    
    def _get_fija_code(self, product: str) -> Tuple[str, str]:
        """Get FIJA service code."""
        code_info = self.FIJA_CODES.get(product)
        if code_info:
            self.logger.debug(f"FIJA: {product} → {code_info[0]}")
            return code_info
        else:
            # Default to TU MASCOTA
            self.logger.warning(f"Product not found in FIJA codes: {product}, using TU MASCOTA")
            return self.FIJA_CODES['TU MASCOTA']
    
    def _get_digital_code(self, tipo_venta: str) -> Tuple[str, str]:
        """
        Get DIGITAL service code.
        
        Digital has different product names (Mascotas, not TU MASCOTA).
        """
        # Map to digital product names
        if 'MASCOTA' in tipo_venta:
            return self.DIGITAL_CODES['MASCOTAS']
        elif 'VIAL' in tipo_venta:
            return self.DIGITAL_CODES['VIAL']
        elif 'HOGAR' in tipo_venta or 'BIENESTAR' in tipo_venta or 'MULTIASISTENCIA' in tipo_venta:
            return self.DIGITAL_CODES['MULTIASISTENCIA']
        else:
            # Default to MASCOTAS
            self.logger.warning(f"Unknown digital product: {tipo_venta}, using MASCOTAS")
            return self.DIGITAL_CODES['MASCOTAS']
    
    def _get_default_code(self, tipo_linea: str) -> Tuple[str, str]:
        """Get default code for line type."""
        if tipo_linea == 'FIJA':
            return self.FIJA_CODES['TU MASCOTA']
        elif tipo_linea == 'DIGITAL':
            return self.DIGITAL_CODES['MASCOTAS']
        else:
            return self.MOVIL_CODES['TU MASCOTA']
    
    def validate_code(self, code: str, tipo_linea: str) -> bool:
        """
        Validate that a code is correct for the line type.
        
        Args:
            code: Service code to validate
            tipo_linea: Line type
        
        Returns:
            True if code is valid for line type
        """
        tipo_linea_upper = str(tipo_linea).upper()
        
        if tipo_linea_upper == 'MOVIL':
            valid_codes = {code for code, _ in self.MOVIL_CODES.values()}
        elif tipo_linea_upper == 'FIJA':
            valid_codes = {code for code, _ in self.FIJA_CODES.values()}
        elif tipo_linea_upper == 'DIGITAL':
            valid_codes = {code for code, _ in self.DIGITAL_CODES.values()}
        else:
            return False
        
        return code in valid_codes
    
    def get_all_codes(self) -> Dict[str, Dict[str, Tuple[str, str]]]:
        """
        Get all service codes for reference.
        
        Returns:
            Dictionary with all codes by line type
        """
        return {
            'MOVIL': self.MOVIL_CODES.copy(),
            'FIJA': self.FIJA_CODES.copy(),
            'DIGITAL': self.DIGITAL_CODES.copy(),
        }


# Export
__all__ = ['ServiceCodeMapper']
