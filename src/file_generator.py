# src/file_generator.py (VERSIÓN CORREGIDA)
"""
Generación de archivos con formatos EXACTOS según especificaciones Movistar.
"""

import pandas as pd
from pathlib import Path
import logging
from typing import Dict
from datetime import datetime

# Intentar importar decorators del nuevo sistema
try:
    from src.core.decorators import timing, retry, validate_file_exists
except ImportError:
    # Fallback: decorators no-op si el módulo no está disponible
    def timing(func):
        return func
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    def validate_file_exists(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# ✅ Import ServiceCodeMapper for CORRECT codes
try:
    from src.services.service_code_mapper import ServiceCodeMapper
    SERVICE_MAPPER_AVAILABLE = True
except ImportError:
    SERVICE_MAPPER_AVAILABLE = False

# ✅ Import Excel sanitizer for security
try:
    from src.utils.excel_sanitizer import sanitize_for_excel
    SANITIZER_AVAILABLE = True
except ImportError:
    SANITIZER_AVAILABLE = False
    logging.warning("Excel sanitizer not available - formula injection protection disabled")

logger = logging.getLogger(__name__)


def _safe_to_excel(df: pd.DataFrame, writer, sheet_name: str, **kwargs) -> None:
    """
    Safely export DataFrame to Excel with formula injection protection.
    
    Args:
        df: DataFrame to export
        writer: ExcelWriter object
        sheet_name: Name of sheet
        **kwargs: Additional arguments for to_excel
    """
    # Sanitize data before export
    if SANITIZER_AVAILABLE:
        df_safe = sanitize_for_excel(df, inplace=False)
    else:
        df_safe = df
    
    df_safe.to_excel(writer, sheet_name=sheet_name, **kwargs)


class MovistarFileGenerator:
    """Generador de archivos con formatos exactos de Movistar."""
    
    @staticmethod
    @timing
    @retry(max_attempts=3, delay=1.0)
    def generate_contact_log(
        df: pd.DataFrame,
        output_path: Path
    ) -> None:
        """
        Genera Contact Log con formato específico.
        
        Formato requerido:
        - Columna A: Linea (número secuencial empezando en 310200)
        - Columna B: Campo Observacion
        - Columna C: Campo Razon (estructura de 3 nodos)
        """
        logger.info("📝 Generando Contact Log...")
        
        if df.empty:
            logger.warning("⚠️ No hay datos para Contact Log")
            return
        
        # Preparar datos
        contact_data = []
        base_line = 310200  # Número base según imagen
        
        for idx, row in df.iterrows():
            # Campo Observación
            fecha_venta = row.get('fecha_venta', '')
            hora_venta = row.get('hora_venta', row.get('marca_temporal', ''))
            
            if isinstance(hora_venta, str) and ' ' in hora_venta:
                hora_venta = hora_venta.split(' ')[1] if len(hora_venta.split(' ')) > 1 else ''
            
            campo_observacion = (
                f"Asesor de venta {row.get('nombre_asesor', 'N/A')}. "
                f"Fecha de venta {fecha_venta} "
                f"Hora de venta {hora_venta} "
                f"Cliente acepta SI."
            )
            
            # Campo Razón (estructura de nodos)
            # ✅ Get correct service code from row (should already be assigned)
            cod_servicio = row.get('cod_servicio', None)
            
            # If not assigned, use ServiceCodeMapper
            if cod_servicio is None and SERVICE_MAPPER_AVAILABLE:
                mapper = ServiceCodeMapper()
                tipo_venta = str(row.get('tipo_venta', 'TU MASCOTA'))
                tipo_linea = str(row.get('tipo_linea', 'MOVIL'))
                cod_servicio, _ = mapper.get_code(tipo_venta, tipo_linea)
            elif cod_servicio is None:
                # Fallback
                cod_servicio = '3823'  # TU MASCOTA MOVIL
            
            campo_razon = (
                f"Activaciones Serv Suplementarios,Asistencias {cod_servicio}, "
                f"ASISTENCIAS: Venta telefonica hecha por el proveedor Connect Assistance"
            )
            
            contact_data.append({
                'Linea': base_line + idx,
                'Campo Observacion: Razon creada en contact log - EJEMPLO: "Prueba de contac log"': campo_observacion,
                'Campo Razon: "nodo 2" ,"nodo 3" ,"razon" - EJEMPLO "Posventa;Anulación de Ordenes Programadas,Cliente solicita anulacion"': campo_razon
            })
        
        df_contact = pd.DataFrame(contact_data)
        
        # Guardar con formato específico
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # ✅ SECURITY: Use safe export with sanitization
            _safe_to_excel(df_contact, writer, sheet_name='Sheet1', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Formato de encabezado (rojo según imagen)
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#FF0000',
                'font_color': 'white',
                'border': 1,
                'text_wrap': True
            })
            
            # Aplicar formato a encabezados
            for col_num, value in enumerate(df_contact.columns):
                worksheet.write(0, col_num, value, header_format)
            
            # Ajustar anchos
            worksheet.set_column('A:A', 12)  # Linea
            worksheet.set_column('B:B', 80)  # Campo Observacion
            worksheet.set_column('C:C', 100) # Campo Razon
        
        logger.info(f"✅ Contact Log generado: {len(df_contact)} registros")
    
    @staticmethod
    @timing
    @retry(max_attempts=3, delay=1.0)
    def generate_formato_movistar(
        df: pd.DataFrame,
        output_path: Path
    ) -> None:
        """
        Genera archivo FORMATO MOVISTAR principal.
        
        Columnas según imagen 2:
        - FECHA_ALTA
        - HORA_VENTA
        - NUM_CELULAR
        - PlanDesc
        - COD_PLAN
        - NOMBRE_TITULAR
        - ASESOR_VENTA
        - CC_AFILIADO
        - Tipo de Envio
        - Dato de envio
        - COD_SERVICIO
        - PROGRAMA
        - INACTIVAR O DESACTIVAR
        - Campo Observacion
        - Campo Razon
        - RTA
        - Contact_Log
        """
        logger.info("📝 Generando FORMATO MOVISTAR...")
        
        formato_data = []
        
        for _, row in df.iterrows():
            # Extraer fecha y hora
            marca_temporal = row.get('marca_temporal', '')
            if isinstance(marca_temporal, str):
                try:
                    dt = pd.to_datetime(marca_temporal)
                    fecha_alta = dt.strftime('%d/%m/%Y')
                    hora_venta = dt.strftime('%I:%M:%S %p')  # Formato 12h con AM/PM
                except:
                    fecha_alta = str(row.get('fecha_venta', ''))
                    hora_venta = ''
            else:
                fecha_alta = str(row.get('fecha_venta', ''))
                hora_venta = ''
            
            # ✅ Determinar código de servicio usando ServiceCodeMapper
            if SERVICE_MAPPER_AVAILABLE:
                mapper = ServiceCodeMapper()
                tipo_venta = str(row.get('tipo_venta', 'TU MASCOTA'))
                tipo_linea = str(row.get('tipo_linea', 'MOVIL'))
                cod_servicio, programa = mapper.get_code(tipo_venta, tipo_linea)
            else:
                # ❌ FALLBACK: Old method (MOVIL codes only)
                tipo_venta = str(row.get('tipo_venta', '')).upper()
                if 'MASCOTA' in tipo_venta:
                    cod_servicio = '3823'  # ✅ CORRECTED
                    programa = 'TU MASCOTA'
                elif 'VEHICULO' in tipo_venta or 'VEHÍCULO' in tipo_venta:
                    cod_servicio = '5002'  # ✅ CORRECTED
                    programa = 'TU VEHICULO'
                elif 'HOGAR' in tipo_venta:
                    cod_servicio = '5000'  # ✅ CORRECTED
                    programa = 'TU HOGAR'
                elif 'BIENESTAR' in tipo_venta:
                    cod_servicio = '2119'  # ✅ CORRECT
                    programa = 'TU BIENESTAR'
                else:
                    cod_servicio = '3823'  # ✅ CORRECTED
                    programa = 'TU MASCOTA'
            
            campo_observacion = (
                f"Asesor de venta {row.get('nombre_asesor', '')}. "
                f"Fecha de venta {fecha_alta} "
                f"Hora de venta {hora_venta} "
                f"Cliente acepta SI."
            )
            
            campo_razon = (
                f"Activaciones Serv Suplementarios,Asistencias {cod_servicio}, "
                f"ASISTENCIAS: Venta telefonica hecha por el proveedor Connect Assistance"
            )
            
            formato_data.append({
                'FECHA_ALTA': fecha_alta,
                'HORA_VENTA': hora_venta,
                'NUM_CELULAR': row.get('telefono_limpio', ''),
                'PlanDesc': row.get('plan_desc', ''),
                'COD_PLAN': '',
                'NOMBRE_TITULAR': row.get('nombre_cliente', ''),
                'ASESOR_VENTA': row.get('nombre_asesor', ''),
                'CC_AFILIADO': row.get('documento_cliente', ''),
                'Tipo de Envio': '',
                'Dato de envio': '',
                'COD_SERVICIO': cod_servicio,
                'PROGRAMA': programa,
                'INACTIVAR O DESACTIVAR': 'Activar',
                'Campo Observacion': campo_observacion,
                'Campo Razon': campo_razon,
                'RTA': '',
                'Contact_Log': ''
            })
        
        df_formato = pd.DataFrame(formato_data)
        
        # Guardar
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # ✅ SECURITY: Use safe export with sanitization
            _safe_to_excel(df_formato, writer, sheet_name='Sheet1', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Formato encabezado
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df_formato.columns):
                worksheet.write(0, col_num, value, header_format)
                # Auto-ajustar columnas
                max_len = max(
                    df_formato[value].astype(str).apply(len).max(),
                    len(str(value))
                )
                worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
        
        logger.info(f"✅ FORMATO MOVISTAR generado: {len(df_formato)} registros")
    
    @staticmethod
    @timing
    @retry(max_attempts=3, delay=1.0)
    def generate_svas(
        df: pd.DataFrame,
        tipo: str,  # 'DIG', 'FIJA', 'MOV'
        output_path: Path
    ) -> None:
        """
        Genera archivos SVAS con formato específico.
        
        Columnas según imagen 3:
        - Num_Celular
        - cod_plantarif
        - Codigo_Bono
        - Cod_ciclo
        - EMPLEADO
        """
        logger.info(f"📝 Generando SVAS {tipo}...")
        
        # Filtrar por tipo
        if tipo != 'DIG':
            df = df[df['tipo_linea'] == tipo].copy()
        
        if df.empty:
            logger.warning(f"⚠️ No hay datos para SVAS {tipo}")
            return
        
        svas_data = []
        
        for _, row in df.iterrows():
            svas_data.append({
                'Num_Celular': row.get('telefono_limpio', ''),
                'cod_plantarif': row.get('cod_plan', '6322'),  # Ejemplo de imagen
                'Codigo_Bono': row.get('cod_bono', '4046'),
                'Cod_ciclo': row.get('cod_ciclo', '20'),
                'EMPLEADO': 'No'  # Default según imagen
            })
        
        df_svas = pd.DataFrame(svas_data)
        
        # Guardar
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # ✅ SECURITY: Use safe export with sanitization
            _safe_to_excel(df_svas, writer, sheet_name='Sheet1', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Formato encabezado (verde según imagen)
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#70AD47',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df_svas.columns):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
        
        logger.info(f"✅ SVAS {tipo} generado: {len(df_svas)} registros")
    
    @staticmethod
    @timing
    @retry(max_attempts=3, delay=1.0)
    def generate_formato_digital_fija_movil(
        df: pd.DataFrame,
        tipo: str,  # 'DIGITAL', 'FIJA', 'MOVIL'
        output_path: Path
    ) -> None:
        """
        Genera archivos FORMATO MOVISTAR_DIGITAL/FIJA/MOVIL.
        
        Formato completo según especificación.
        """
        logger.info(f"📝 Generando FORMATO MOVISTAR_{tipo}...")
        
        formato_data = []
        
        for _, row in df.iterrows():
            # Extraer fecha y hora
            marca_temporal = row.get('marca_temporal', '')
            if isinstance(marca_temporal, str):
                try:
                    dt = pd.to_datetime(marca_temporal)
                    fecha_alta = dt.strftime('%Y-%m-%d')
                    hora_venta = dt.strftime('%H:%M:%S')
                except:
                    fecha_alta = str(row.get('fecha_venta', ''))
                    hora_venta = ''
            else:
                fecha_alta = str(row.get('fecha_venta', ''))
                hora_venta = ''
            
            # ✅ Determinar código de servicio usando ServiceCodeMapper
            if SERVICE_MAPPER_AVAILABLE:
                mapper = ServiceCodeMapper()
                tipo_venta = str(row.get('tipo_venta', '') or row.get('plan_desc', 'MASCOTAS'))
                # Use the 'tipo' parameter to determine line type
                cod_servicio, programa = mapper.get_code(tipo_venta, tipo)
            else:
                # ❌ FALLBACK: Use digital codes as default
                tipo_venta_raw = str(row.get('tipo_venta', '')).upper()
                if 'VIAL' in tipo_venta_raw:
                    cod_servicio = '4045'  # ✅ CORRECT
                    programa = 'Vial'
                elif 'MASCOTA' in tipo_venta_raw:
                    cod_servicio = '4046'  # ✅ CORRECT
                    programa = 'Mascotas'
                elif 'MULTIASISTENCIA' in tipo_venta_raw or 'HOGAR' in tipo_venta_raw:
                    cod_servicio = '4047'  # ✅ CORRECT
                    programa = 'Multiasistencia'
                else:
                    cod_servicio = '4046'  # Default to MASCOTAS
                    programa = 'Mascotas'
            
            asesor = tipo if tipo == 'Digital' else row.get('nombre_asesor', '')
            
            campo_observacion = (
                f"Asesor de venta {asesor}. "
                f"Fecha de venta {fecha_alta} "
                f"Hora de venta {hora_venta} "
                f"Cliente acepta SI."
            )
            
            campo_razon = (
                f"Activaciones Serv Suplementarios, Asistencias {cod_servicio}, "
                f"ASISTENCIAS: Venta telefónica hecha por el proveedor Connect Assistance"
            )
            
            formato_data.append({
                'FECHA_ALTA': fecha_alta,
                'HORA_VENTA': hora_venta,
                'NUM_CELULAR': row.get('telefono_limpio', ''),
                'PlanDesc': row.get('plan_desc', ''),
                'COD_PLAN': row.get('cod_plan', ''),
                'NOMBRE_TITULAR': row.get('nombre_cliente', ''),
                'ASESOR_VENTA': asesor,
                'CC_AFILIADO': row.get('documento_cliente', ''),
                'Tipo_de_Envio': '',
                'Dato_de_envio': '',
                'COD_SERVICIO': cod_servicio,
                'PROGRAMA': programa,
                'PROCESO': 'Activar',
                'Campo_Observacion': campo_observacion,
                'Campo_Razon': campo_razon,
                'RTA': '',
                'Contact_Log': ''
            })
        
        df_formato = pd.DataFrame(formato_data)
        
        # Guardar con formato
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # ✅ SECURITY: Use safe export with sanitization
            _safe_to_excel(df_formato, writer, sheet_name='Sheet1', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Formato según tipo
            if tipo == 'DIGITAL':
                bg_color = '#FFC000'  # Naranja
            elif tipo == 'FIJA':
                bg_color = '#4472C4'  # Azul
            else:
                bg_color = '#70AD47'  # Verde
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': bg_color,
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df_formato.columns):
                worksheet.write(0, col_num, value, header_format)
                max_len = max(
                    df_formato[value].astype(str).apply(len).max(),
                    len(str(value))
                )
                worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
        
        logger.info(f"✅ FORMATO MOVISTAR_{tipo} generado: {len(df_formato)} registros")
    
    @staticmethod
    @timing
    @retry(max_attempts=3, delay=1.0)
    def generate_octubre_exitosas(
        df_consolidated: pd.DataFrame,
        df_digital: pd.DataFrame,
        output_path: Path
    ) -> None:
        """
        Genera reporte mensual OCTUBRE_Exitosas_Movistar.
        
        Hojas:
        - CARG DIGITAL
        - CARG FIJA
        - CARG MOVIL
        
        Según imagen 4, debe incluir:
        - Source.Name
        - FECHA_ALTA
        - HORA_VENTA
        - NUM. CELULAR
        - ASESOR_VENTA
        - COD. SERVICIO
        - PROGRAMA
        - RTA
        - Contact_Log
        """
        logger.info("📝 Generando OCTUBRE_Exitosas_Movistar...")
        
        sheets = {}
        
        # 1. CARG DIGITAL
        digital_data = []
        for _, row in df_digital.iterrows():
            digital_data.append({
                'Source.Name': row.get('_archivo_origen', 'FORMATO MOVISTAR_DIGITAL'),
                'FECHA_ALTA': row.get('fecha_venta', ''),
                'HORA_VENTA': row.get('hora_venta', ''),
                'NUM. CELULAR': row.get('telefono_limpio', ''),
                'ASESOR_VENTA': 'Digital',
                'COD. SERVICIO': '4045',
                'PROGRAMA': 'Vial',
                'RTA': 'Exito',
                'Contact_Log': ''
            })
        
        sheets['CARG DIGITAL'] = pd.DataFrame(digital_data)
        
        # 2. CARG FIJA
        df_fija = df_consolidated[
            df_consolidated['tipo_linea'] == 'FIJA'
        ].copy()
        
        fija_data = []
        for _, row in df_fija.iterrows():
            fija_data.append({
                'Source.Name': row.get('_archivo_origen', ''),
                'FECHA_ALTA': row.get('fecha_venta', ''),
                'HORA_VENTA': row.get('hora_venta', ''),
                'NUM. CELULAR': row.get('telefono_limpio', ''),
                'ASESOR_VENTA': row.get('nombre_asesor', ''),
                'COD. SERVICIO': '4045',
                'PROGRAMA': 'Vial',
                'RTA': 'Exito',
                'Contact_Log': ''
            })
        
        sheets['CARG FIJA'] = pd.DataFrame(fija_data)
        
        # 3. CARG MOVIL
        df_movil = df_consolidated[
            df_consolidated['tipo_linea'] == 'MOVIL'
        ].copy()
        
        movil_data = []
        for _, row in df_movil.iterrows():
            movil_data.append({
                'Source.Name': row.get('_archivo_origen', ''),
                'FECHA_ALTA': row.get('fecha_venta', ''),
                'HORA_VENTA': row.get('hora_venta', ''),
                'NUM. CELULAR': row.get('telefono_limpio', ''),
                'ASESOR_VENTA': row.get('nombre_asesor', ''),
                'COD. SERVICIO': '4045',
                'PROGRAMA': 'Vial',
                'RTA': 'Exito',
                'Contact_Log': ''
            })
        
        sheets['CARG MOVIL'] = pd.DataFrame(movil_data)
        
        # Guardar archivo multi-hoja con formato según imagen 4
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            for sheet_name, df_sheet in sheets.items():
                # ✅ SECURITY: Use safe export with sanitization
                _safe_to_excel(df_sheet, writer, sheet_name=sheet_name, index=False)
                worksheet = writer.sheets[sheet_name]
                
                # Encabezado verde (según imagen 4)
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#70AD47',
                    'font_color': 'black',
                    'border': 1
                })
                
                for col_num, value in enumerate(df_sheet.columns):
                    worksheet.write(0, col_num, value, header_format)
                    max_len = max(
                        df_sheet[value].astype(str).apply(len).max(),
                        len(str(value))
                    )
                    worksheet.set_column(col_num, col_num, min(max_len + 2, 30))
                
                logger.info(f"  📄 Hoja '{sheet_name}': {len(df_sheet)} registros")
        
        logger.info(f"✅ OCTUBRE_Exitosas_Movistar generado")


# Funciones wrapper para compatibilidad
def generate_movistar_files(
    df_ventas: pd.DataFrame,
    output_files: Dict[str, str],
    output_dir: Path
) -> None:
    """Genera los 5 archivos para Movistar con formatos CORRECTOS."""
    
    logger.info("=" * 80)
    logger.info("📤 GENERANDO ARCHIVOS PARA MOVISTAR (FORMATOS REALES)")
    logger.info("=" * 80)
    
    gen = MovistarFileGenerator()
    
    # 1. Contact Log
    gen.generate_contact_log(
        df_ventas,
        output_dir / output_files['movistar_contact_log']
    )
    
    # 2. FORMATO MOVISTAR principal
    gen.generate_formato_movistar(
        df_ventas,
        output_dir / output_files['movistar_general']
    )
    
    # 3-5. SVAS DIG/FIJA/MOV
    for tipo, file_key in [('DIG', 'movistar_svas_dig'),
                            ('FIJA', 'movistar_svas_fija'),
                            ('MOV', 'movistar_svas_mov')]:
        gen.generate_svas(
            df_ventas if tipo == 'DIG' else df_ventas[df_ventas['tipo_linea'] == tipo],
            tipo,
            output_dir / output_files[file_key]
        )
    
    logger.info("✅ Archivos para Movistar generados")


def generate_internal_files(
    df_digital: pd.DataFrame,
    df_ventas: pd.DataFrame,
    output_files: Dict[str, str],
    output_dir: Path
) -> None:
    """Genera archivos internos FORMATO MOVISTAR_DIGITAL/FIJA/MOVIL."""
    
    logger.info("=" * 80)
    logger.info("📤 GENERANDO ARCHIVOS INTERNOS")
    logger.info("=" * 80)
    
    gen = MovistarFileGenerator()
    
    # 1. DIGITAL
    gen.generate_formato_digital_fija_movil(
        df_digital,
        'Digital',
        output_dir / output_files['internal_digital']
    )
    
    # 2. FIJA
    df_fija = df_ventas[df_ventas['tipo_linea'] == 'FIJA'].copy()
    gen.generate_formato_digital_fija_movil(
        df_fija,
        'FIJA',
        output_dir / output_files['internal_fija']
    )
    
    # 3. MOVIL
    df_movil = df_ventas[df_ventas['tipo_linea'] == 'MOVIL'].copy()
    gen.generate_formato_digital_fija_movil(
        df_movil,
        'MOVIL',
        output_dir / output_files['internal_movil']
    )
    
    logger.info("✅ Archivos internos generados")


def generate_monthly_report(
    df_monthly: pd.DataFrame,
    df_digital_processed: pd.DataFrame,
    output_files: Dict[str, str],
    output_dir: Path
) -> None:
    """Genera OCTUBRE_Exitosas_Movistar."""
    
    gen = MovistarFileGenerator()
    
    gen.generate_octubre_exitosas(
        df_monthly,
        df_digital_processed,
        output_dir / output_files['monthly_exitosas']
    )