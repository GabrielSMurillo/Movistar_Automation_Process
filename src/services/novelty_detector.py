"""
Novelty Detector - Detect and separate invalid records for reporting.

Identifies records that DO NOT meet submission criteria:
1. Invalid phone numbers (wrong prefix, wrong length, missing city code)
2. Invalid asesor names (numbers, #N/A, empty)
3. Invalid logins (#N/A, empty, non-numeric)
4. Invalid cliente names (#N/A, empty)

These records are EXCLUDED from client deliverables and reported in
a separate "Novedades" (Novelties) file for operations to review.

Example:
    >>> detector = NoveltyDetector()
    >>> df_valid, df_novelties = detector.separate_valid_and_novelties(df)
    >>> print(f"Valid: {len(df_valid)}, Novelties: {len(df_novelties)}")
"""

from typing import Tuple
import pandas as pd
import logging
from dataclasses import dataclass

from src.services.phone_validator import EnhancedPhoneValidator
from src.services.field_validators import FieldValidators
from src.services.service_code_mapper import ServiceCodeMapper

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Detailed validation report for a record."""
    is_valid: bool
    telefono_valido: bool
    asesor_valido: bool
    login_valido: bool
    cliente_valido: bool
    codigo_servicio_valido: bool
    rejection_reasons: list[str]


class NoveltyDetector:
    """
    Detects and separates invalid records (novelties) from valid records.
    
    Valid records go to client deliverables.
    Invalid records (novelties) go to internal reporting for ops review.
    """
    
    def __init__(self):
        """Initialize novelty detector with validators."""
        self.phone_validator = EnhancedPhoneValidator()
        self.field_validators = FieldValidators()
        self.service_mapper = ServiceCodeMapper()
        self.logger = logging.getLogger(f"{__name__}.NoveltyDetector")
    
    def validate_record(self, row: pd.Series) -> ValidationReport:
        """
        Validate a single record against all business rules.
        
        Args:
            row: Data row to validate
        
        Returns:
            ValidationReport with detailed validation results
        """
        rejection_reasons = []
        
        # 1. Validate phone
        telefono_valido = False
        if 'telefono_limpio' in row and pd.notna(row['telefono_limpio']):
            # Check phone is 10 digits
            phone = str(row['telefono_limpio'])
            if len(phone) == 10:
                # Check prefix
                if phone.startswith('3'):
                    # Valid mobile
                    telefono_valido = True
                elif phone.startswith('6'):
                    # Valid landline - MUST have city code (601-608)
                    city_code = phone[:3]
                    if city_code in ['601', '602', '604', '605', '606', '607', '608']:
                        telefono_valido = True
                    else:
                        rejection_reasons.append(
                            f'Fijo sin código de ciudad válido: {city_code} '
                            f'(debe ser 601-608)'
                        )
                else:
                    rejection_reasons.append(
                        f'Teléfono no inicia con 3 (móvil) ni 6 (fijo): {phone[0]}'
                    )
            else:
                rejection_reasons.append(
                    f'Teléfono no tiene 10 dígitos: {len(phone)}'
                )
        else:
            telefono_valido = False
            rejection_reasons.append('Teléfono vacío o faltante')
        
        # 2. Validate asesor
        asesor_valido = False
        if 'nombre_asesor' in row:
            asesor_valido, reason = self.field_validators.validate_asesor_name(
                row['nombre_asesor']
            )
            if not asesor_valido:
                rejection_reasons.append(f'Asesor: {reason}')
        else:
            rejection_reasons.append('Campo nombre_asesor faltante')
        
        # 3. Validate login (if present)
        login_valido = True  # Optional field
        if 'login_asesor' in row and pd.notna(row['login_asesor']):
            login_valido, reason = self.field_validators.validate_login(
                row['login_asesor']
            )
            if not login_valido:
                rejection_reasons.append(f'Login: {reason}')
        
        # 4. Validate cliente
        cliente_valido = False
        if 'nombre_cliente' in row:
            cliente_valido, reason = self.field_validators.validate_cliente_name(
                row['nombre_cliente']
            )
            if not cliente_valido:
                rejection_reasons.append(f'Cliente: {reason}')
        else:
            rejection_reasons.append('Campo nombre_cliente faltante')
        
        # 5. Validate service code matches line type
        codigo_servicio_valido = False
        if 'cod_servicio' in row and 'tipo_linea' in row:
            codigo_servicio_valido = self.service_mapper.validate_code(
                str(row['cod_servicio']),
                str(row['tipo_linea'])
            )
            if not codigo_servicio_valido:
                rejection_reasons.append(
                    f'Código de servicio {row["cod_servicio"]} no válido para '
                    f'{row["tipo_linea"]}'
                )
        
        # Overall validation
        is_valid = all([
            telefono_valido,
            asesor_valido,
            login_valido,
            cliente_valido,
            codigo_servicio_valido
        ])
        
        return ValidationReport(
            is_valid=is_valid,
            telefono_valido=telefono_valido,
            asesor_valido=asesor_valido,
            login_valido=login_valido,
            cliente_valido=cliente_valido,
            codigo_servicio_valido=codigo_servicio_valido,
            rejection_reasons=rejection_reasons
        )
    
    def separate_valid_and_novelties(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Separate valid records from novelties (invalid records).
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Tuple of:
            - df_valid: Records that pass all validations (go to client)
            - df_novelties: Records with validation errors (internal review)
        
        Example:
            >>> detector = NoveltyDetector()
            >>> df_valid, df_novelties = detector.separate_valid_and_novelties(df)
        """
        self.logger.info("=" * 80)
        self.logger.info("🔍 DETECTANDO NOVEDADES (REGISTROS INVÁLIDOS)")
        self.logger.info("=" * 80)
        
        if df.empty:
            self.logger.warning("⚠️ DataFrame vacío, no hay registros para validar")
            return df.copy(), pd.DataFrame()
        
        # Validate all records
        validation_results = df.apply(self.validate_record, axis=1)
        
        # Extract validation flags
        df_working = df.copy()
        df_working['_es_valido'] = validation_results.apply(lambda x: x.is_valid)
        df_working['_telefono_valido'] = validation_results.apply(lambda x: x.telefono_valido)
        df_working['_asesor_valido'] = validation_results.apply(lambda x: x.asesor_valido)
        df_working['_login_valido'] = validation_results.apply(lambda x: x.login_valido)
        df_working['_cliente_valido'] = validation_results.apply(lambda x: x.cliente_valido)
        df_working['_codigo_valido'] = validation_results.apply(lambda x: x.codigo_servicio_valido)
        df_working['_motivos_rechazo'] = validation_results.apply(
            lambda x: ' | '.join(x.rejection_reasons) if x.rejection_reasons else ''
        )
        
        # Separate valid from novelties
        df_valid = df_working[df_working['_es_valido']].copy()
        df_novelties = df_working[~df_working['_es_valido']].copy()
        
        # Clean up validation flags from valid records (keep in novelties for debugging)
        for col in ['_es_valido', '_telefono_valido', '_asesor_valido', 
                    '_login_valido', '_cliente_valido', '_codigo_valido', '_motivos_rechazo']:
            if col in df_valid.columns:
                df_valid = df_valid.drop(columns=[col])
        
        # Log statistics
        total = len(df)
        valid_count = len(df_valid)
        novelty_count = len(df_novelties)
        
        self.logger.info(f"📊 Total registros procesados: {total:,}")
        self.logger.info(f"✅ Registros válidos: {valid_count:,} ({valid_count/total*100:.1f}%)")
        self.logger.info(f"❌ Novedades detectadas: {novelty_count:,} ({novelty_count/total*100:.1f}%)")
        
        if novelty_count > 0:
            self.logger.info("\n📋 DISTRIBUCIÓN DE NOVEDADES:")
            
            # Count by rejection type
            invalid_phone = (~df_novelties['_telefono_valido']).sum()
            invalid_asesor = (~df_novelties['_asesor_valido']).sum()
            invalid_login = (~df_novelties['_login_valido']).sum()
            invalid_cliente = (~df_novelties['_cliente_valido']).sum()
            invalid_code = (~df_novelties['_codigo_valido']).sum()
            
            self.logger.info(f"  📞 Teléfonos inválidos: {invalid_phone:,}")
            self.logger.info(f"  👤 Asesores inválidos: {invalid_asesor:,}")
            self.logger.info(f"  🔑 Logins inválidos: {invalid_login:,}")
            self.logger.info(f"  🧑 Clientes inválidos: {invalid_cliente:,}")
            self.logger.info(f"  🏷️  Códigos inválidos: {invalid_code:,}")
            
            # Sample rejection reasons
            self.logger.info("\n📝 EJEMPLOS DE MOTIVOS DE RECHAZO:")
            sample_reasons = df_novelties['_motivos_rechazo'].head(5)
            for idx, reason in enumerate(sample_reasons, 1):
                self.logger.info(f"  {idx}. {reason}")
        
        self.logger.info("=" * 80)
        
        return df_valid, df_novelties
    
    def generate_novelty_report(
        self,
        df_novelties: pd.DataFrame,
        output_path: str
    ) -> bool:
        """
        Generate Excel report of novelties for operations review.
        
        Args:
            df_novelties: DataFrame with invalid records
            output_path: Path to save report
        
        Returns:
            True if report generated successfully
        """
        if df_novelties.empty:
            self.logger.info("✅ No hay novedades para reportar")
            return True
        
        try:
            # Select important columns for review
            report_columns = [
                'telefono_servicio', 'telefono_limpio', 'tipo_linea',
                'nombre_cliente', 'nombre_asesor', 'login_asesor',
                'tipo_venta', 'cod_servicio', 'programa',
                'fecha_venta', 'marca_temporal',
                '_telefono_valido', '_asesor_valido', '_login_valido',
                '_cliente_valido', '_codigo_valido', '_motivos_rechazo'
            ]
            
            # Keep only columns that exist
            available_columns = [col for col in report_columns if col in df_novelties.columns]
            df_report = df_novelties[available_columns].copy()
            
            # Rename validation columns for clarity
            rename_map = {
                '_telefono_valido': 'Teléfono Válido',
                '_asesor_valido': 'Asesor Válido',
                '_login_valido': 'Login Válido',
                '_cliente_valido': 'Cliente Válido',
                '_codigo_valido': 'Código Válido',
                '_motivos_rechazo': 'Motivos de Rechazo'
            }
            df_report = df_report.rename(columns=rename_map)
            
            # Export to Excel
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                df_report.to_excel(writer, sheet_name='Novedades', index=False)
                
                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Novedades']
                
                # Format header
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D7E4BD',
                    'border': 1
                })
                
                for col_num, value in enumerate(df_report.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Auto-fit columns
                for i, col in enumerate(df_report.columns):
                    max_len = max(
                        df_report[col].astype(str).apply(len).max(),
                        len(col)
                    ) + 2
                    worksheet.set_column(i, i, min(max_len, 50))
            
            self.logger.info(f"✅ Reporte de novedades generado: {output_path}")
            self.logger.info(f"   Total novedades: {len(df_novelties):,}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error generando reporte de novedades: {e}", exc_info=True)
            return False


# Export
__all__ = ['NoveltyDetector', 'ValidationReport']
