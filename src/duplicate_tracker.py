# src/duplicate_tracker.py
"""
Sistema de tracking de duplicados entre cortes.
Previene que se envíen ventas duplicadas en diferentes cortes.
"""

import json
from pathlib import Path
from typing import Set
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DuplicateTracker:
    """Rastrea ventas ya enviadas para evitar duplicados entre cortes."""
    
    def __init__(self, tracking_file: Path):
        """
        Inicializa el tracker.
        
        Args:
            tracking_file: Ruta al archivo JSON de tracking
        """
        self.tracking_file = tracking_file
        self.sent_sales: Set[str] = self._load_tracking()
    
    def _load_tracking(self) -> Set[str]:
        """Carga registro de ventas ya enviadas."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sent = set(data.get('sent_sales', []))
                    logger.info(f"📋 Cargadas {len(sent):,} ventas previamente enviadas")
                    return sent
            except Exception as e:
                logger.error(f"Error cargando tracking: {e}")
                return set()
        
        logger.info("📋 Nuevo archivo de tracking - sin ventas previas")
        return set()
    
    def _save_tracking(self):
        """Guarda registro actualizado."""
        try:
            self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'sent_sales': list(self.sent_sales),
                    'last_update': datetime.now().isoformat(),
                    'total_tracked': len(self.sent_sales)
                }, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"💾 Tracking guardado: {len(self.sent_sales):,} ventas")
        except Exception as e:
            logger.error(f"Error guardando tracking: {e}")
    
    def _create_key(self, row: pd.Series) -> str:
        """
        Crea llave única para identificar una venta.
        
        Formato: telefono_tipo_fecha
        """
        telefono = row.get('telefono_limpio', '')
        tipo = row.get('tipo_venta', '')
        fecha = row.get('fecha_venta', '')
        
        return f"{telefono}_{tipo}_{fecha}"
    
    def mark_as_sent(self, df: pd.DataFrame) -> None:
        """
        Marca ventas como enviadas usando llave única.
        
        Args:
            df: DataFrame con ventas a marcar como enviadas
        """
        if df.empty:
            logger.warning("⚠️ DataFrame vacío - nada que marcar")
            return
        
        # Crear llaves únicas
        keys = df.apply(self._create_key, axis=1)
        
        # Agregar a registro
        new_keys = set(keys) - self.sent_sales
        self.sent_sales.update(new_keys)
        
        # Guardar
        self._save_tracking()
        
        logger.info(f"✅ Registradas {len(new_keys):,} ventas nuevas como enviadas")
    
    def filter_already_sent(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra ventas que ya fueron enviadas previamente.
        
        Args:
            df: DataFrame con ventas a filtrar
        
        Returns:
            DataFrame solo con ventas no enviadas
        """
        if df.empty:
            return df
        
        # Crear llaves
        keys = df.apply(self._create_key, axis=1)
        
        # Filtrar
        mask = ~keys.isin(self.sent_sales)
        already_sent = (~mask).sum()
        
        if already_sent > 0:
            logger.warning(
                f"⚠️ Filtradas {already_sent:,} ventas ya enviadas previamente "
                f"({already_sent/len(df)*100:.1f}%)"
            )
            
            # Guardar reporte de duplicados filtrados
            df_duplicates = df[~mask].copy()
            logger.debug(
                f"   Duplicados por fecha: {df_duplicates['fecha_venta'].value_counts().to_dict()}"
            )
        else:
            logger.info("✅ No se encontraron ventas previamente enviadas")
        
        return df[mask].copy()
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del tracking."""
        return {
            'total_ventas_enviadas': len(self.sent_sales),
            'archivo_tracking': str(self.tracking_file),
            'existe_archivo': self.tracking_file.exists()
        }
    
    def reset(self) -> None:
        """Resetea el tracking (usar con cuidado)."""
        logger.warning("⚠️ RESETEANDO tracking de ventas enviadas")
        self.sent_sales = set()
        self._save_tracking()