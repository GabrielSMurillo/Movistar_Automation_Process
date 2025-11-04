# Movistar Automation Process

Sistema de automatización para el procesamiento de datos de ventas de Movistar.

## Descripción

Este proyecto automatiza el procesamiento de reportes de ventas para diferentes segmentos (Digital, Fija, Móvil) de Movistar, incluyendo validación de datos, eliminación de duplicados y generación de reportes consolidados.

## Estructura del Proyecto

```
Movistar_Automation_Process/
├── src/                    # Código fuente principal
│   ├── data_loader.py     # Carga de datos
│   ├── data_processor.py  # Procesamiento de datos
│   ├── duplicate_tracker.py # Seguimiento de duplicados
│   ├── eda.py             # Análisis exploratorio
│   ├── file_generator.py  # Generación de archivos
│   ├── output_validator.py # Validación de salidas
│   ├── utils.py           # Utilidades
│   └── validators.py      # Validadores
├── data/                  # Datos de entrada y salida
│   ├── input/            # Archivos de entrada
│   └── historico/        # Archivos históricos
├── tests/                # Tests unitarios
├── config.py             # Configuración del proyecto
├── main.py              # Punto de entrada principal
└── requirements.txt     # Dependencias

```

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/TU_USUARIO/Movistar_Automation_Process.git
cd Movistar_Automation_Process
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecutar el script principal:
```bash
python main.py
```

## Configuración

Editar el archivo `config.py` para personalizar rutas y parámetros del proceso.

## Testing

Ejecutar los tests:
```bash
pytest tests/
```

## Contribución

1. Fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit de cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir un Pull Request

## Licencia

Este proyecto es privado y de uso interno.

## Autor

Gabriel

---

**Nota**: Los archivos de datos históricos y archivos CSV de entrada no se incluyen en el repositorio por razones de confidencialidad.
