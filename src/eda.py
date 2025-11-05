# src/eda.py
"""
Análisis Exploratorio de Datos (EDA) mejorado.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from typing import Optional

from src.validators import DataQualityValidator

logger = logging.getLogger(__name__)

# Configurar estilo de gráficos
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class EDAGenerator:
    """Generador de análisis exploratorio de datos."""
    
    @staticmethod
    def perform_full_eda(
        df: pd.DataFrame,
        df_name: str,
        output_dir: Path,
        generate_plots: bool = True
    ) -> None:
        """
        Realiza un EDA completo y guarda reportes.
        
        Args:
            df: DataFrame a analizar
            df_name: Nombre descriptivo
            output_dir: Directorio de salida
            generate_plots: Si True, genera gráficos
        """
        logger.info(f"📊 Iniciando EDA para: {df_name}")
        
        if df.empty:
            logger.warning(f"⚠️ DataFrame '{df_name}' vacío. Omitiendo EDA.")
            return
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Reporte de calidad
        logger.info("  → Generando reporte de calidad...")
        quality_report = DataQualityValidator.generate_quality_report(df, df_name)
        
        # 2. Estadísticas generales
        logger.info("  → Generando estadísticas descriptivas...")
        stats_report = EDAGenerator._generate_stats_report(df, df_name)
        
        # 3. Análisis de valores categóricos
        logger.info("  → Analizando variables categóricas...")
        categorical_report = EDAGenerator._analyze_categorical(df)
        
        # 4. Guardar reportes en Excel
        report_path = output_dir / f"EDA_{df_name.replace(' ', '_')}.xlsx"
        
        with pd.ExcelWriter(report_path, engine='xlsxwriter') as writer:
            quality_report.to_excel(writer, sheet_name='Calidad', index=False)
            stats_report.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            if not categorical_report.empty:
                categorical_report.to_excel(writer, sheet_name='Categóricas', index=False)
            
            # Agregar info general
            info_df = pd.DataFrame([{
                'Total Registros': len(df),
                'Total Columnas': len(df.columns),
                'Memoria (MB)': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}",
                'Duplicados Completos': df.duplicated().sum(),
            }])
            info_df.to_excel(writer, sheet_name='Resumen', index=False)
        
        logger.info(f"  ✅ Reporte guardado: {report_path.name}")
        
        # 5. Generar gráficos
        if generate_plots:
            logger.info("  → Generando visualizaciones...")
            EDAGenerator._generate_plots(df, df_name, output_dir)
        
        logger.info(f"✅ EDA completado para: {df_name}")
    
    @staticmethod
    def _generate_stats_report(df: pd.DataFrame, df_name: str) -> pd.DataFrame:
        """Genera estadísticas descriptivas."""
        
        stats_data = []
        
        for col in df.columns:
            col_stats = {
                'columna': col,
                'tipo': str(df[col].dtype),
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats.update({
                    'count': df[col].count(),
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'median': df[col].median(),
                })
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_stats.update({
                    'count': df[col].count(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'unique': df[col].nunique(),
                })
            else:
                col_stats.update({
                    'count': df[col].count(),
                    'unique': df[col].nunique(),
                    'top_value': df[col].mode()[0] if len(df[col].mode()) > 0 else None,
                    'top_freq': df[col].value_counts().iloc[0] if len(df[col]) > 0 else 0,
                })
            
            stats_data.append(col_stats)
        
        return pd.DataFrame(stats_data)
    
    @staticmethod
    def _analyze_categorical(df: pd.DataFrame) -> pd.DataFrame:
        """Analiza columnas categóricas."""
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        if len(categorical_cols) == 0:
            return pd.DataFrame()
        
        analysis_data = []
        
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            
            for value, count in value_counts.head(10).items():
                analysis_data.append({
                    'columna': col,
                    'valor': value,
                    'frecuencia': count,
                    'porcentaje': f"{count/len(df)*100:.2f}%",
                })
        
        return pd.DataFrame(analysis_data)
    
    @staticmethod
    def _generate_plots(df: pd.DataFrame, df_name: str, output_dir: Path) -> None:
        """Genera visualizaciones."""
        
        safe_name = df_name.replace(' ', '_').lower()
        
        # 1. Gráfico de valores nulos
        try:
            null_counts = df.isnull().sum()
            if null_counts.sum() > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                null_counts[null_counts > 0].sort_values(ascending=False).plot(
                    kind='barh', ax=ax
                )
                ax.set_title(f'Valores Nulos por Columna - {df_name}')
                ax.set_xlabel('Cantidad de Nulos')
                plt.tight_layout()
                plt.savefig(output_dir / f'{safe_name}_nulos.png', dpi=150)
                plt.close()
        except Exception as e:            
            logger.warning(f"No se pudo generar gráfico de nulos: {e}")
        
        # 2. Gráfico de ventas por día (si existe fecha_venta)
        if 'fecha_venta' in df.columns:
            try:
                df_temp = df.copy()
                df_temp['fecha_venta'] = pd.to_datetime(df_temp['fecha_venta'])
                
                sales_per_day = df_temp.groupby(
                    df_temp['fecha_venta'].dt.date
                ).size()
                
                fig, ax = plt.subplots(figsize=(14, 6))
                sales_per_day.plot(kind='bar', ax=ax, color='steelblue')
                ax.set_title(f'Ventas por Día - {df_name}')
                ax.set_xlabel('Fecha')
                ax.set_ylabel('Número de Ventas')
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.savefig(output_dir / f'{safe_name}_ventas_diarias.png', dpi=150)
                plt.close()
                
            except Exception as e:
                logger.warning(f"No se pudo generar gráfico de ventas diarias: {e}")
        
        # 3. Gráfico de distribución por tipo de venta
        if 'tipo_venta' in df.columns:
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                df['tipo_venta'].value_counts().plot(
                    kind='pie', 
                    ax=ax, 
                    autopct='%1.1f%%',
                    startangle=90
                )
                ax.set_title(f'Distribución por Tipo de Venta - {df_name}')
                ax.set_ylabel('')
                plt.tight_layout()
                plt.savefig(output_dir / f'{safe_name}_tipos_venta.png', dpi=150)
                plt.close()
                
            except Exception as e:
                logger.warning(f"No se pudo generar gráfico de tipos: {e}")
        
        # 4. Gráfico de ventas por asesor (top 10)
        if 'nombre_asesor' in df.columns:
            try:
                top_asesores = df['nombre_asesor'].value_counts().head(10)
                
                fig, ax = plt.subplots(figsize=(12, 6))
                top_asesores.plot(kind='barh', ax=ax, color='coral')
                ax.set_title(f'Top 10 Asesores - {df_name}')
                ax.set_xlabel('Número de Ventas')
                ax.set_ylabel('Asesor')
                ax.grid(axis='x', alpha=0.3)
                plt.tight_layout()
                plt.savefig(output_dir / f'{safe_name}_top_asesores.png', dpi=150)
                plt.close()
                
            except Exception as e:
                logger.warning(f"No se pudo generar gráfico de asesores: {e}")
        
        # 5. Heatmap de correlación (solo columnas numéricas)
        try:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 1:
                fig, ax = plt.subplots(figsize=(10, 8))
                correlation = df[numeric_cols].corr()
                sns.heatmap(
                    correlation,
                    annot=True,
                    fmt='.2f',
                    cmap='coolwarm',
                    center=0,
                    ax=ax
                )
                ax.set_title(f'Matriz de Correlación - {df_name}')
                plt.tight_layout()
                plt.savefig(output_dir / f'{safe_name}_correlacion.png', dpi=150)
                plt.close()
                
        except Exception as e:
            logger.warning(f"No se pudo generar heatmap: {e}")


def perform_eda(
    df: pd.DataFrame,
    df_name: str,
    output_dir: Path,
    generate_plots: bool = True
) -> None:
    """
    Función legacy para compatibilidad con código existente.
    """
    EDAGenerator.perform_full_eda(df, df_name, output_dir, generate_plots)