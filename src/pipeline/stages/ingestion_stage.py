"""
Data ingestion stage - loads raw data from input sources.
"""

import logging
from pathlib import Path
import pandas as pd

from src.pipeline.orchestrator import PipelineStage, PipelineContext
from src.data_loader import load_tipificador, load_digital, load_historical_sales
from src.core.exceptions import FileNotFoundError, FileFormatError

logger = logging.getLogger(__name__)


class IngestionStage(PipelineStage):
    """
    Stage 1: Data Ingestion
    
    Responsibilities:
    - Load raw data from input files
    - Validate file existence and format
    - Create data manifest
    - Store raw data in context
    """
    
    def __init__(
        self,
        tipificador_config: dict,
        digital_config: dict,
        historical_config: dict
    ):
        """
        Initialize ingestion stage.
        
        Args:
            tipificador_config: Tipificador file configuration
            digital_config: Digital file configuration
            historical_config: Historical files configuration
        """
        super().__init__("Data Ingestion")
        self.tipificador_config = tipificador_config
        self.digital_config = digital_config
        self.historical_config = historical_config
    
    def validate(self, context: PipelineContext) -> bool:
        """Validate that input files exist."""
        # Check tipificador file
        tipificador_path = Path(self.tipificador_config.get('file_path'))
        if not tipificador_path.exists():
            context.add_error(f"Tipificador file not found: {tipificador_path}")
            return False
        
        # Check digital file
        digital_path = Path(self.digital_config.get('file_path'))
        if not digital_path.exists():
            context.add_error(f"Digital file not found: {digital_path}")
            return False
        
        # Historical files are optional
        historical_dir = self.historical_config.get('dir')
        if historical_dir and not Path(historical_dir).exists():
            context.add_warning(f"Historical directory not found: {historical_dir}")
        
        return True
    
    def _execute(self, context: PipelineContext) -> PipelineContext:
        """Load all input files."""
        
        # 1. Load Tipificador
        logger.info("\n[1/3] Loading Tipificador...")
        try:
            df_tipificador = load_tipificador(self.tipificador_config)
            context.add_data('tipificador_raw', df_tipificador)
            logger.info(f"✅ Tipificador loaded: {len(df_tipificador):,} records")
        except Exception as e:
            raise FileFormatError(
                file_path=str(self.tipificador_config.get('file_path')),
                expected_format='CSV'
            ) from e
        
        # 2. Load Digital
        logger.info("\n[2/3] Loading Digital sales...")
        try:
            df_digital = load_digital(self.digital_config)
            context.add_data('digital_raw', df_digital)
            logger.info(f"✅ Digital loaded: {len(df_digital):,} records")
        except Exception as e:
            raise FileFormatError(
                file_path=str(self.digital_config.get('file_path')),
                expected_format='CSV'
            ) from e
        
        # 3. Load Historical (optional)
        logger.info("\n[3/3] Loading Historical sales...")
        try:
            df_historical = load_historical_sales(self.historical_config)
            if not df_historical.empty:
                context.add_data('historical_raw', df_historical)
                logger.info(f"✅ Historical loaded: {len(df_historical):,} records")
            else:
                logger.info("ℹ️  No historical data found")
                context.add_data('historical_raw', pd.DataFrame())
        except Exception as e:
            logger.warning(f"⚠️  Could not load historical data: {e}")
            context.add_data('historical_raw', pd.DataFrame())
        
        # Add ingestion metrics
        context.add_metric('tipificador_raw_count', len(df_tipificador))
        context.add_metric('digital_raw_count', len(df_digital))
        context.add_metric('historical_raw_count', len(context.get_data('historical_raw')))
        
        logger.info(f"\n✅ Data ingestion completed")
        
        return context
