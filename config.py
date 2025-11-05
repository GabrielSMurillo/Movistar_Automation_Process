# config.py
"""
Configuración centralizada del pipeline de ventas Movistar.
Versión mejorada con integración del nuevo sistema de Settings.

Este archivo mantiene compatibilidad hacia atrás mientras integra
el nuevo sistema basado en Pydantic Settings.
"""

from pathlib import Path
from datetime import date, timedelta
from typing import Dict, Any, List, Tuple

# ============================================================================
# FUNCIONES PARA FECHAS A DÍA VENCIDO (Procesa mes anterior)
# ============================================================================

def get_previous_month_dates() -> tuple[date, date]:
    """
    Obtiene el primer y último día del mes anterior.
    
    Sistema diseñado para ejecutarse a día vencido:
    - Si hoy es 5 de febrero, procesa todo enero (1 al 31 de enero)
    - Si hoy es 1 de marzo, procesa todo febrero (1 al 28/29 de febrero)
    
    Returns:
        tuple[date, date]: (primer_dia_mes_anterior, ultimo_dia_mes_anterior)
    
    Example:
        >>> # Si hoy es 5 de febrero 2025
        >>> get_previous_month_dates()
        (date(2025, 1, 1), date(2025, 1, 31))
    """
    today = date.today()
    
    # Primer día del mes actual
    first_day_current_month = today.replace(day=1)
    
    # Último día del mes anterior (restar 1 día al primer día del mes actual)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    
    # Primer día del mes anterior
    first_day_previous_month = last_day_previous_month.replace(day=1)
    
    return first_day_previous_month, last_day_previous_month

# ============================================================================
# NUEVO SISTEMA DE CONFIGURACIÓN (Recomendado)
# ============================================================================

# Variables de fecha (necesarias para logging y otros usos)
TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)

try:
    from src.core.config import get_settings
    
    # Obtener settings desde el nuevo sistema
    _settings = get_settings()
    
    # Usar valores del nuevo sistema
    BASE_DIR = _settings.base_dir
    DATA_DIR = _settings.data_dir
    INPUT_DIR = _settings.input_dir
    OUTPUT_DIR = _settings.output_dir
    PROCESSED_DIR = _settings.processed_dir
    LOGS_DIR = _settings.logs_dir
    TRACKING_DIR = _settings.tracking_dir
    
    START_DATE = _settings.start_date
    END_DATE = _settings.end_date
    DATE_RANGE_STR = _settings.date_range_str
    DATE_RANGE_STR_SHORT = _settings.date_range_str_short
    
    # Crear directorios automáticamente
    _settings.create_directories()
    
except ImportError:
    # Fallback al sistema antiguo si el nuevo no está disponible
    BASE_DIR = Path(__file__).parent.resolve()
    DATA_DIR = BASE_DIR / "data"
    INPUT_DIR = DATA_DIR / "input"
    OUTPUT_DIR = DATA_DIR / "output"
    PROCESSED_DIR = DATA_DIR / "processed"
    LOGS_DIR = BASE_DIR / "logs"
    TRACKING_DIR = DATA_DIR / "tracking"
    
    # Crear directorios (sistema antiguo)
    for directory in [OUTPUT_DIR, PROCESSED_DIR, LOGS_DIR, TRACKING_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Obtener fechas del mes anterior automáticamente
    START_DATE, END_DATE = get_previous_month_dates()
    YESTERDAY = date.today() - timedelta(days=1)
    DATE_RANGE_STR = f"{START_DATE.strftime('%d')}_Al_{END_DATE.strftime('%d')}_{END_DATE.strftime('%b').upper()}_{END_DATE.year}"
    DATE_RANGE_STR_SHORT = f"{START_DATE.strftime('%d')}_A_{END_DATE.strftime('%d')}_{END_DATE.strftime('%b').upper()}"

# --- Configuración de Archivos CSV (Google Sheets) ---
CSV_READ_CONFIG: Dict[str, Any] = {
    'sep': ',',
    'decimal': ',',
    'thousands': '.',
    'encoding': 'utf-8-sig',
    'engine': 'python',
    'na_values': ['', 'N/A', 'NA', 'null', 'NULL', '#N/A', 'n/a'],
    'keep_default_na': True,
    'skipinitialspace': True,
    # low_memory is not supported with engine='python'
}

# --- Configuración de Archivos de Entrada ---
TIPIFICADOR_CONFIG = {
    'file_name': '_TIPIFICADOR DE VENTAS GENERAL - MES ACTUAL.csv',
    'sheet_name': None,
    'skiprows': 0,
}

DIGITAL_CONFIG = {
    'file_name': 'Reporte de ventas digitales MOVISTAR - Sheet1.csv',
    'sheet_name': None,
    'skiprows': 0,
}

HISTORICAL_SALES_CONFIG = {
    'dir': INPUT_DIR / 'historicos',
    'pattern': 'FORMATO_MOVISTAR_*.csv',
    'sheet_name': None,
}

# --- Nombres de Archivos de Salida ---
OUTPUT_FILES = {
    # Archivos para Movistar (5)
    'movistar_contact_log': f'Contact Log Movistar Asist_{DATE_RANGE_STR}.xlsx',
    'movistar_general': f'FORMATO MOVISTAR_{DATE_RANGE_STR}.xlsx',
    'movistar_svas_dig': f'SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_DIG_{DATE_RANGE_STR_SHORT}.xlsx',
    'movistar_svas_fija': f'SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_FIJA_{DATE_RANGE_STR_SHORT}.xlsx',
    'movistar_svas_mov': f'SVAS_MERCADEO_B2C_SUSCRIBIR_Asistencias_MOV_{DATE_RANGE_STR_SHORT}.xlsx',
    
    # Archivos para Diego (3)
    'internal_digital': f'FORMATO MOVISTAR_DIGITAL_{DATE_RANGE_STR}.xlsx',
    'internal_fija': f'FORMATO MOVISTAR_FIJA_{DATE_RANGE_STR}.xlsx',
    'internal_movil': f'FORMATO MOVISTAR_MOVIL_{DATE_RANGE_STR}.xlsx',
    
    # Reporte mensual (1)
    'monthly_exitosas': f'OCTUBRE_Exitosas_Movistar.xlsx',
    
    # Archivo de NOVEDADES (registros rechazados) (1)
    'novedades': f'NOVEDADES_{DATE_RANGE_STR}.xlsx',
    
    # Reportes de control (4)
    'quality_report': f'QUALITY_REPORT_{DATE_RANGE_STR}.xlsx',
    'duplicate_report': f'DUPLICATES_REPORT_{DATE_RANGE_STR}.xlsx',
    'referidos_report': f'REFERIDOS_REPORT_{DATE_RANGE_STR}.xlsx',
    'validation_errors': f'VALIDATION_ERRORS_{DATE_RANGE_STR}.xlsx',
}

# --- Constantes de Lógica de Negocio ---
REFERIDO_YES_VALUES = {'sí', 'si', 'yes', 's', 'y', '1', 'true'}
DUPLICATE_STATUS_ORIGINAL = 'original'
DUPLICATE_STATUS_DUPLICATE = 'duplicado'

# --- Prefijos Válidos para Teléfonos Móviles en Colombia ---
MOBILE_PREFIXES = {
    '300', '301', '302', '303', '304', '305', 
    '310', '311', '312', '313', '314', '315',
    '316', '317', '318', '319', '320', '321',
    '322', '323', '324', '350', '351', '352'
}

# --- Indicativos de Ciudades para Líneas Fijas ---
FIXED_LINE_CODES = {
    '601': 'Bogotá',
    '602': 'Cali',
    '604': 'Medellín',
    '605': 'Cartagena',
    '606': 'Pereira',
    '607': 'Bucaramanga',
    '608': 'Barranquilla',
}

# --- Códigos de Servicio por Tipo de Venta ---
SERVICE_CODE_MAPPING = {
    'patterns': [
        # (palabras_clave, código_movistar, código_digital, programa_movistar, programa_digital)
        # [WARNING] WARNING: These are MOVIL codes only! Does NOT differentiate MOVIL vs FIJA (CRITICAL BUG)
        # FIXED: Changed from wrong codes (2119/2120/2121) to correct MOVIL codes
        (['MASCOTA', 'MASCOTAS', 'PET'], '3823', '4046', 'TU MASCOTA', 'Mascotas'),  # Was 2119 (WRONG!)
        (['VEHICULO', 'VEHÍCULO', 'AUTO', 'CARRO'], '5002', '4045', 'TU VEHICULO', 'Vial'),  # Was 2120 (WRONG!)
        (['HOGAR', 'CASA', 'HOME'], '5000', '4047', 'TU HOGAR', 'Multiasistencia'),  # Was 2121 (WRONG!)
        (['BIENESTAR'], '2119', '4047', 'TU BIENESTAR', 'Multiasistencia'),
        (['VIAL', 'VIA'], '4045', '4045', 'VIAL', 'Vial'),
    ],
    'default': {
        'movistar': '3823',  # TU MASCOTA MOVIL (was 2119 - WRONG!)
        'digital': '4046',   # MASCOTAS DIGITAL (was 4045 - WRONG!)
        'programa_movistar': 'TU MASCOTA',
        'programa_digital': 'Mascotas'
    }
}

# [WARNING][WARNING][WARNING] CRITICAL WARNING [WARNING][WARNING][WARNING]
# This SERVICE_CODE_MAPPING is INCOMPLETE and should be DEPRECATED
# It does NOT differentiate between MOVIL (mobile) and FIJA (landline)
# 
# CORRECT CODES PER LINE TYPE:
# MOVIL: TU MASCOTA=3823, TU HOGAR=5000, TU VEHICULO=5002, TU BIENESTAR=2119
# FIJA:  TU MASCOTA=15639, TU HOGAR=15641, TU VEHICULO=15642, TU BIENESTAR=15640
# DIGITAL: MASCOTAS=4046, MULTIASISTENCIA=4047, VIAL=4045
#
# RECOMMENDED: Use ServiceCodeMapper from src.services instead:
#   from src.services import ServiceCodeMapper
#   mapper = ServiceCodeMapper()
#   code, program = mapper.get_code(tipo_venta, tipo_linea)  # Correct!

# --- Mapeo de Columnas del Tipificador ---
TIPIFICADOR_COLS_MAP = {
    'Marca temporal': 'marca_temporal',
    'Nombre del asesor': 'nombre_asesor',
    'BASE ASIGNADA': 'base_asignada',
    'Nombre del cliente': 'nombre_cliente',
    'TELEFONO DEL CLIENTE( DONDE SE VA CARGAR EL SERVICIO )': 'telefono_servicio',
    'TELEFONO DEL CLIENTE (DONDE SE VA CARGAR EL SERVICIO)': 'telefono_servicio',
    'Teléfono del cliente( donde se va cargar el servicio )': 'telefono_servicio',
    'TIPO DE VENTA': 'tipo_venta',
    'TIPO DE VENTA ': 'tipo_venta',  # Con espacio al final
    'Tipo de venta': 'tipo_venta',
    '¿LA VENTA PROVIENE DE UN REFERIDO?': 'es_referido',
    '¿La venta proviene de un referido?': 'es_referido',
    'TELEFONO DEL CLIENTE DONDE SE REALIZO LA VENTA (GRABACION)': 'telefono_grabacion',
    'Teléfono del cliente donde se realizó la venta (grabación)': 'telefono_grabacion',
    'Documento de identidad del cliente': 'documento_cliente',
    'LOGIN': 'login',
    'Correo electronico del cliente': 'email_cliente',
    'Correo electrónico del cliente': 'email_cliente',
    'OBSERVACION': 'observacion',
    'Observación': 'observacion',
    'costo plan': 'costo_plan',
    'Costo plan': 'costo_plan',
    'Dirección del cliente': 'direccion_cliente',
    'DirecciÃ³n del cliente': 'direccion_cliente',
    'DIRECCIÓN DEL CLIENTE (En este espacio deben completar la dirección actual o la modificación de la misma)': 'direccion_cliente',
    'DIRECCIÓN DEL CLIENTE': 'direccion_cliente',
    '¿El cliente es empleado de Movistar?': 'es_empleado_movistar',
    'SI LA VENTA ES VEHÍCULO, INGRESA LA PLACA': 'placa_vehiculo',
    'Dirección de correo electrónico': 'email_asesor',
}

# --- Mapeo de Columnas de Digital ---
DIGITAL_COLS_MAP = {
    'Num_Celular': 'telefono_servicio',
    'Num Celular': 'telefono_servicio',
    'cod_plantarif': 'cod_plan',
    'Codigo_Bono': 'cod_bono',
    'Cod_ciclo': 'cod_ciclo',
    'Fecha de venta': 'fecha_venta',
    'Nombre del cliente': 'nombre_cliente',
    'Plan': 'plan_desc',
}

# --- Nombres de Hojas para Reporte Mensual ---
MONTHLY_REPORT_SHEETS = {
    'digital': 'CARG DIGITAL',
    'fija': 'CARG FIJA',
    'movil': 'CARG MOVIL',
}

# --- Configuración de Contact Log ---
CONTACT_LOG_CONFIG = {
    'linea_base': 310200,  # Número base para secuencia
    'template_observacion': "Asesor de venta {asesor}. Fecha de venta {fecha} Hora de venta {hora} Cliente acepta SI.",
    'template_razon': "Activaciones Serv Suplementarios,Asistencias {cod_servicio}, ASISTENCIAS: Venta telefonica hecha por el proveedor Connect Assistance",
}

# --- Configuración de Validación de Datos ---
DATA_QUALITY_THRESHOLDS = {
    'max_null_rate': 0.30,
    'max_duplicate_rate': 0.15,
    'min_phone_length': 7,
    'max_phone_length': 10,
    'min_date': date(2024, 1, 1),
    'max_date': date(2026, 12, 31),
}

# --- Configuración de Logging ---
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': str(LOGS_DIR / f'pipeline_{TODAY.strftime("%Y%m%d")}.log'),
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf-8',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file'],
    },
}

# --- Archivo de Tracking de Duplicados ---
DUPLICATE_TRACKING_FILE = TRACKING_DIR / 'sent_sales_tracking.json'

# --- Funciones Helper ---
def get_service_code(tipo_venta: str, es_digital: bool = False) -> Tuple[str, str]:
    """
    Determina código de servicio y programa según tipo de venta.
    
    Args:
        tipo_venta: Tipo de venta del cliente
        es_digital: Si es True, usa códigos para archivos digitales
    
    Returns:
        (codigo_servicio, programa)
    
    Example:
        >>> get_service_code("TU MASCOTA", False)
        ('2119', 'TU MASCOTA')
        >>> get_service_code("VEHICULO", True)
        ('4046', 'Vehiculo')
    """
    tipo_venta_upper = str(tipo_venta).upper()
    
    for keywords, cod_movistar, cod_digital, prog_movistar, prog_digital in SERVICE_CODE_MAPPING['patterns']:
        if any(kw in tipo_venta_upper for kw in keywords):
            if es_digital:
                return cod_digital, prog_digital
            else:
                return cod_movistar, prog_movistar
    
    # Default
    defaults = SERVICE_CODE_MAPPING['default']
    if es_digital:
        return defaults['digital'], defaults['programa_digital']
    else:
        return defaults['movistar'], defaults['programa_movistar']

# ============================================================================
# FUNCIONES PARA CARPETAS CON FECHA Y RANGO
# ============================================================================

def create_output_folder_with_date() -> Path:
    """
    Crea carpeta de salida con formato:
    output/YYYY-MM-DD_Ejecutado_Periodo_DD-MM-YYYY_al_DD-MM-YYYY/
    
    Ejemplo:
    output/2025-02-05_Ejecutado_Periodo_01-01-2025_al_31-01-2025/
    
    La carpeta indica:
    - Fecha de ejecución: 2025-02-05 (día que se ejecutó el script)
    - Periodo procesado: 01-01-2025 al 31-01-2025 (datos procesados)
    
    Returns:
        Path: Ruta a la carpeta creada
    """
    # Fecha de ejecución (hoy)
    fecha_ejecucion = TODAY.strftime('%Y-%m-%d')
    
    # Periodo procesado
    inicio = START_DATE.strftime('%d-%m-%Y')
    fin = END_DATE.strftime('%d-%m-%Y')
    
    # Formato: YYYY-MM-DD_Ejecutado_Periodo_DD-MM-YYYY_al_DD-MM-YYYY
    nombre_carpeta = f"{fecha_ejecucion}_Ejecutado_Periodo_{inicio}_al_{fin}"
    carpeta_salida = OUTPUT_DIR / nombre_carpeta
    
    # Crear carpeta si no existe
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    return carpeta_salida

# Variable global para cachear la carpeta
_output_dir_cached = None

def get_output_dir() -> Path:
    """
    Obtiene o crea la carpeta de salida con fecha.
    Usa caché para evitar crear múltiples carpetas.
    
    Returns:
        Path: Ruta a la carpeta de salida
    """
    global _output_dir_cached
    
    if _output_dir_cached is None:
        _output_dir_cached = create_output_folder_with_date()
    
    return _output_dir_cached