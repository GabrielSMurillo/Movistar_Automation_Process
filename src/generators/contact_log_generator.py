"""
Generador de archivos Contact Log para Movistar.

Este módulo implementa la generación automatizada de archivos Contact Log,
que anteriormente se creaban manualmente.

Formato del archivo:
- Columna 1: Linea (número de teléfono del cliente)
- Columna 2: Campo Observacion (metadata de la venta)
- Columna 3: Campo Razon (estructura de 3 nodos)

Ejemplo:
    >>> generator = ContactLogGenerator()
    >>> success = generator.generate(df_ventas, Path("contact_log.xlsx"))
    >>> if success:
    ...     print("Contact Log generado exitosamente")
"""

from pathlib import Path
import pandas as pd
import logging
from typing import List, Dict, Optional
from datetime import datetime

# ✅ Import ServiceCodeMapper for CORRECT codes
try:
    from src.services.service_code_mapper import ServiceCodeMapper
    SERVICE_MAPPER_AVAILABLE = True
except ImportError:
    SERVICE_MAPPER_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContactLogGenerator:
    """
    Generador de archivos Contact Log para Movistar.
    
    Attributes:
        COLUMN_NAMES: Nombres de las 3 columnas del Contact Log
        OBSERVACION_TEMPLATE: Template para Campo Observacion
        RAZON_TEMPLATE: Template para Campo Razon
        records_processed: Contador de registros procesados
        records_skipped: Contador de registros omitidos
    """
    
    # Nombres exactos de columnas según formato Movistar
    COLUMN_NAMES = [
        'Linea',
        'Campo Observacion: Razon creada en contact log - EJEMPLO: "Prueba de contac log"',
        ' Campo Razon:"nodo 2","nodo 3","razon" -  EJEMPLO "Posventa,Anulación de Ordenes Programadas,Cliente solicita anulacion de baja"'
    ]
    
    # Template para Campo Observacion
    OBSERVACION_TEMPLATE = (
        "Asesor de venta {asesor} "
        "Fecha de venta {fecha} "
        "Hora de venta {hora} "
        "Cliente acepta SI"
    )
    
    # Template para Campo Razon (estructura de 3 nodos)
    RAZON_TEMPLATE = (
        "Activaciones Serv Suplementarios,"
        "Asistencias {cod_servicio}, "
        "ASISTENCIAS: Venta telefonica hecha por el proveedor Connect Assistance"
    )
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa el generador.
        
        Args:
            config: Configuración opcional con templates personalizados
        """
        self.config = config or {}
        self.records_processed = 0
        self.records_skipped = 0
        self._reset_counters()
    
    def _reset_counters(self) -> None:
        """Reinicia contadores de estadísticas."""
        self.records_processed = 0
        self.records_skipped = 0
    
    def generate(
        self,
        df: pd.DataFrame,
        output_path: Path,
        validate: bool = True
    ) -> bool:
        """
        Genera archivo Contact Log.
        
        Args:
            df: DataFrame con ventas procesadas
            output_path: Ruta del archivo de salida (.xlsx)
            validate: Si True, valida el archivo generado
            
        Returns:
            True si generación exitosa, False en caso contrario
            
        Raises:
            ValueError: Si el DataFrame está vacío
            IOError: Si hay error al guardar el archivo
        """
        self._reset_counters()
        
        logger.info("=" * 80)
        logger.info("📝 GENERANDO CONTACT LOG")
        logger.info("=" * 80)
        
        if df.empty:
            logger.warning("⚠️  DataFrame vacío, no se genera Contact Log")
            return False
        
        try:
            # 1. Filtrar ventas válidas
            df_valid = self._filter_valid_sales(df)
            logger.info(
                f"📊 Ventas válidas para Contact Log: {len(df_valid):,} / {len(df):,}"
            )
            
            if df_valid.empty:
                logger.warning("⚠️  No hay ventas válidas después del filtrado")
                return False
            
            # 2. Construir registros
            contact_records = self._build_contact_records(df_valid)
            logger.info(f"📝 Registros construidos: {len(contact_records):,}")
            
            # 3. Crear DataFrame
            df_contact = pd.DataFrame(contact_records, columns=self.COLUMN_NAMES)
            
            # 4. Ordenar por teléfono (Linea)
            df_contact = df_contact.sort_values(by=self.COLUMN_NAMES[0])
            
            # 5. Guardar archivo
            self._save_excel(df_contact, output_path)
            
            # 6. Validar output (si se solicita)
            if validate:
                validation_ok = self.validate_output(output_path)
                if not validation_ok:
                    logger.error("❌ Validación de Contact Log falló")
                    return False
            
            # 7. Log de éxito
            logger.info("=" * 80)
            logger.info("✅ CONTACT LOG GENERADO EXITOSAMENTE")
            logger.info("=" * 80)
            logger.info(f"   📁 Archivo: {output_path.name}")
            logger.info(f"   📊 Total registros: {len(df_contact):,}")
            logger.info(f"   ✓ Procesados: {self.records_processed:,}")
            logger.info(f"   ⊘ Omitidos: {self.records_skipped:,}")
            logger.info(f"   💾 Tamaño: {output_path.stat().st_size / 1024:.2f} KB")
            logger.info("=" * 80)
            
            return True
                
        except Exception as e:
            logger.error(f"❌ Error generando Contact Log: {e}", exc_info=True)
            return False
    
    def _filter_valid_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra ventas válidas para Contact Log.
        
        Criterios de filtrado:
        - Teléfono válido (10 dígitos)
        - No es duplicado
        - No está rechazado
        - Tiene nombre de asesor
        
        Args:
            df: DataFrame con todas las ventas
            
        Returns:
            DataFrame filtrado con ventas válidas
        """
        df_filtered = df.copy()
        initial_count = len(df_filtered)
        
        # 1. Filtrar duplicados
        if 'duplicate_status' in df_filtered.columns:
            before = len(df_filtered)
            df_filtered = df_filtered[
                df_filtered['duplicate_status'] != 'duplicado'
            ]
            logger.debug(
                f"   Filtro duplicados: {before:,} → {len(df_filtered):,}"
            )
        
        # 2. Filtrar teléfonos inválidos
        if 'telefono_limpio' in df_filtered.columns:
            before = len(df_filtered)
            df_filtered = df_filtered[
                df_filtered['telefono_limpio'].notna() &
                (df_filtered['telefono_limpio'].str.len() == 10) &
                (df_filtered['telefono_limpio'].str.match(r'^\d{10}$'))
            ]
            logger.debug(
                f"   Filtro teléfonos: {before:,} → {len(df_filtered):,}"
            )
        
        # 3. Filtrar rechazados
        if 'estado' in df_filtered.columns:
            before = len(df_filtered)
            df_filtered = df_filtered[
                df_filtered['estado'] != 'rechazado'
            ]
            logger.debug(
                f"   Filtro rechazados: {before:,} → {len(df_filtered):,}"
            )
        
        # 4. Filtrar sin asesor
        if 'nombre_asesor' in df_filtered.columns:
            before = len(df_filtered)
            df_filtered = df_filtered[
                df_filtered['nombre_asesor'].notna() &
                (df_filtered['nombre_asesor'] != '') &
                (df_filtered['nombre_asesor'] != 'N/A')
            ]
            logger.debug(
                f"   Filtro asesor: {before:,} → {len(df_filtered):,}"
            )
        
        removed = initial_count - len(df_filtered)
        if removed > 0:
            logger.info(f"   🗑️  Registros filtrados: {removed:,}")
        
        return df_filtered
    
    def _build_contact_records(self, df: pd.DataFrame) -> List[List[str]]:
        """
        Construye lista de registros para Contact Log.
        
        Cada registro es una lista de 3 elementos:
        [linea, campo_observacion, campo_razon]
        
        Args:
            df: DataFrame con ventas válidas
            
        Returns:
            Lista de registros (cada registro es una lista de 3 strings)
        """
        records = []
        
        for idx, row in df.iterrows():
            try:
                # 1. Linea (teléfono)
                linea = self._get_phone(row)
                
                # 2. Campo Observacion
                campo_observacion = self._build_observacion(row)
                
                # 3. Campo Razon
                campo_razon = self._build_razon(row)
                
                # Agregar registro
                records.append([linea, campo_observacion, campo_razon])
                self.records_processed += 1
                
            except Exception as e:
                logger.warning(
                    f"⚠️  Error procesando registro (índice {idx}): {e}"
                )
                self.records_skipped += 1
                continue
        
        return records
    
    def _get_phone(self, row: pd.Series) -> str:
        """
        Extrae número de teléfono del registro.
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            Número de teléfono limpio (10 dígitos)
        """
        # Prioridad: telefono_limpio > telefono_servicio
        phone = row.get('telefono_limpio', row.get('telefono_servicio', ''))
        return str(phone).strip()
    
    def _build_observacion(self, row: pd.Series) -> str:
        """
        Construye Campo Observacion.
        
        Formato:
        "Asesor de venta {asesor} Fecha de venta {fecha} Hora de venta {hora} Cliente acepta SI"
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            String con Campo Observacion formateado
        """
        # 1. Asesor
        asesor = row.get('nombre_asesor', 'N/A')
        
        # 2. Fecha
        fecha_venta = row.get('fecha_venta', row.get('fecha_alta', ''))
        if pd.isna(fecha_venta):
            fecha = 'N/A'
        elif isinstance(fecha_venta, (pd.Timestamp, datetime)):
            fecha = fecha_venta.strftime('%Y-%m-%d')
        else:
            fecha = str(fecha_venta)
        
        # 3. Hora
        hora_venta = row.get('hora_venta', row.get('hora_24h', ''))
        if pd.isna(hora_venta):
            hora = 'N/A'
        elif isinstance(hora_venta, str):
            # Si viene como "YYYY-MM-DD HH:MM:SS", extraer solo hora
            if ' ' in hora_venta:
                parts = hora_venta.split(' ')
                hora = parts[1] if len(parts) > 1 else hora_venta
            else:
                hora = hora_venta
        else:
            hora = str(hora_venta)
        
        return self.OBSERVACION_TEMPLATE.format(
            asesor=asesor,
            fecha=fecha,
            hora=hora
        )
    
    def _build_razon(self, row: pd.Series) -> str:
        """
        Construye el campo "Campo Razon" con formato de 3 nodos.
        
        Formato:
        "Activaciones Serv Suplementarios,Asistencias {cod_servicio}, ASISTENCIAS: Venta..."
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            String con Campo Razon formateado (3 nodos separados por comas)
        """
        # ✅ Obtener código de servicio (should already be in row)
        cod_servicio = row.get('cod_servicio', None)
        
        # If not present, use ServiceCodeMapper
        if cod_servicio is None and SERVICE_MAPPER_AVAILABLE:
            mapper = ServiceCodeMapper()
            tipo_venta = str(row.get('tipo_venta', 'TU MASCOTA'))
            tipo_linea = str(row.get('tipo_linea', 'MOVIL'))
            cod_servicio, _ = mapper.get_code(tipo_venta, tipo_linea)
            self.logger.debug(
                f"ServiceCodeMapper: {tipo_venta} + {tipo_linea} → {cod_servicio}"
            )
        elif cod_servicio is None:
            # Fallback: TU MASCOTA MOVIL
            cod_servicio = '3823'
            self.logger.warning(
                "⚠️ cod_servicio not in row and ServiceCodeMapper unavailable, "
                f"using fallback: {cod_servicio}"
            )
        
        return self.RAZON_TEMPLATE.format(cod_servicio=cod_servicio)
    
    def _save_excel(self, df: pd.DataFrame, output_path: Path) -> None:
        """
        Guarda DataFrame como Excel con formato específico de Movistar.
        
        Formato aplicado:
        - Encabezado: fondo rojo, texto blanco, bold
        - Columnas ajustadas automáticamente
        - Sin índice
        
        Args:
            df: DataFrame a guardar
            output_path: Ruta del archivo de salida
            
        Raises:
            IOError: Si hay error al guardar el archivo
        """
        logger.debug(f"💾 Guardando Excel: {output_path}")
        
        # Crear directorio si no existe
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # Escribir DataFrame
            df.to_excel(writer, sheet_name='Sheet1', index=False)
            
            # Obtener objetos de formato
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Formato de encabezado (rojo según especificación Movistar)
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FF0000',
                'font_color': 'white',
                'border': 1,
                'text_wrap': True,
                'align': 'center',
                'valign': 'vcenter'
            })
            
            # Aplicar formato a encabezados
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustar anchos de columna
            worksheet.set_column('A:A', 15)   # Linea (teléfono)
            worksheet.set_column('B:B', 80)   # Campo Observacion
            worksheet.set_column('C:C', 100)  # Campo Razon
            
            # Ajustar altura de fila de encabezado
            worksheet.set_row(0, 30)
        
        logger.debug(f"   ✓ Excel guardado exitosamente")
    
    def validate_output(self, file_path: Path) -> bool:
        """
        Valida archivo Contact Log generado.
        
        Verificaciones:
        - Archivo existe
        - Tiene las 3 columnas correctas
        - No está vacío
        - Teléfonos tienen formato válido (10 dígitos numéricos)
        
        Args:
            file_path: Ruta al archivo a validar
            
        Returns:
            True si todas las validaciones pasan, False en caso contrario
        """
        logger.debug(f"🔍 Validando Contact Log: {file_path.name}")
        
        # 1. Verificar existencia
        if not file_path.exists():
            logger.error(f"❌ Archivo no existe: {file_path}")
            return False
        
        try:
            # 2. Cargar archivo
            df = pd.read_excel(file_path)
            
            # 3. Verificar número de columnas
            if len(df.columns) != 3:
                logger.error(
                    f"❌ Número incorrecto de columnas: "
                    f"esperadas 3, encontradas {len(df.columns)}"
                )
                return False
            
            # 4. Verificar no vacío
            if df.empty:
                logger.warning("⚠️  Archivo vacío (pero válido estructuralmente)")
                return True
            
            # 5. Verificar teléfonos en columna 1 (Linea)
            first_col = df.columns[0]
            phones = df[first_col].astype(str)
            
            # Deben ser numéricos y de 10 dígitos
            invalid_phones = phones[~phones.str.match(r'^\d{10}$')]
            
            if len(invalid_phones) > 0:
                logger.warning(
                    f"⚠️  {len(invalid_phones)} teléfonos con formato inválido"
                )
                logger.debug(f"   Ejemplos: {invalid_phones.head(3).tolist()}")
                # No falla la validación, solo advierte
            
            # 6. Verificar Campo Observacion no vacío
            second_col = df.columns[1]
            empty_obs = df[second_col].isna() | (df[second_col] == '')
            if empty_obs.any():
                logger.warning(
                    f"⚠️  {empty_obs.sum()} registros con Campo Observacion vacío"
                )
            
            # 7. Verificar Campo Razon no vacío
            third_col = df.columns[2]
            empty_razon = df[third_col].isna() | (df[third_col] == '')
            if empty_razon.any():
                logger.warning(
                    f"⚠️  {empty_razon.sum()} registros con Campo Razon vacío"
                )
            
            logger.debug("✅ Validación de Contact Log: APROBADA")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validando Contact Log: {e}", exc_info=True)
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de la última generación.
        
        Returns:
            Diccionario con estadísticas:
            - records_processed: Registros procesados exitosamente
            - records_skipped: Registros omitidos por errores
        """
        return {
            'records_processed': self.records_processed,
            'records_skipped': self.records_skipped,
        }


def generate_quality_reports(
    metrics: Dict,
    output_dir: Path,
    output_files: Dict
) -> None:
    """
    Genera reportes de calidad incluyendo Contact Log.
    
    Esta función es un wrapper para compatibilidad con el código existente.
    
    Args:
        metrics: Diccionario con métricas de procesamiento
        output_dir: Directorio de salida
        output_files: Diccionario con nombres de archivos
    """
    logger.info("\n" + "=" * 80)
    logger.info("📊 GENERANDO REPORTES DE CALIDAD")
    logger.info("=" * 80)
    
    # Crear DataFrame con resumen de métricas
    summary_data = []
    
    for module, module_metrics in metrics.items():
        if isinstance(module_metrics, dict):
            for key, value in module_metrics.items():
                summary_data.append({
                    'Módulo': module,
                    'Métrica': key,
                    'Valor': value
                })
    
    df_summary = pd.DataFrame(summary_data)
    
    # Guardar reporte
    report_path = output_dir / output_files.get(
        'quality_report',
        f'QUALITY_REPORT_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )
    
    with pd.ExcelWriter(report_path, engine='xlsxwriter') as writer:
        df_summary.to_excel(writer, sheet_name='Resumen', index=False)
        
        # Formatear
        workbook = writer.book
        worksheet = writer.sheets['Resumen']
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(df_summary.columns):
            worksheet.write(0, col_num, value, header_format)
            max_len = max(
                df_summary[value].astype(str).apply(len).max(),
                len(str(value))
            )
            worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
    
    logger.info(f"✅ Reporte de calidad generado: {report_path.name}")
    logger.info("=" * 80)
