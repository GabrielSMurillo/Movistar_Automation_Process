"""
Data validation and processing stage.
"""

import logging
from datetime import date

from src.pipeline.orchestrator import PipelineStage, PipelineContext
from src.domain.processors import (
    TipificadorProcessor,
    DigitalProcessor,
    HistoricalSalesProcessor,
)

logger = logging.getLogger(__name__)


class ValidationStageImpl(PipelineStage):
    """
    Stage 2: Data Validation & Processing
    
    Responsibilities:
    - Validate data quality
    - Clean and normalize data
    - Separate valid from invalid records (novedades)
    - Apply business rules
    - Enrich data
    """
    
    def __init__(
        self,
        tipificador_cols_map: dict,
        digital_cols_map: dict,
        start_date: date,
        end_date: date
    ):
        """
        Initialize validation stage.
        
        Args:
            tipificador_cols_map: Column mapping for tipificador
            digital_cols_map: Column mapping for digital
            start_date: Processing start date
            end_date: Processing end date
        """
        super().__init__("Data Validation & Processing")
        self.tipificador_cols_map = tipificador_cols_map
        self.digital_cols_map = digital_cols_map
        self.start_date = start_date
        self.end_date = end_date
    
    def validate(self, context: PipelineContext) -> bool:
        """Validate that raw data is present."""
        if context.get_data('tipificador_raw') is None:
            context.add_error("Tipificador raw data not found in context")
            return False
        
        if context.get_data('digital_raw') is None:
            context.add_error("Digital raw data not found in context")
            return False
        
        return True
    
    def _execute(self, context: PipelineContext) -> PipelineContext:
        """Process and validate all data sources."""
        
        # 1. Process Tipificador
        logger.info("\n[1/3] Processing Tipificador...")
        df_tipificador_raw = context.get_data('tipificador_raw')
        
        df_ventas, df_referidos, metrics_tip = TipificadorProcessor.process(
            df_tipificador_raw,
            self.tipificador_cols_map,
            self.start_date,
            self.end_date
        )
        
        context.add_data('ventas_valid', df_ventas)
        context.add_data('referidos', df_referidos)
        context.add_data('tipificador_novedades', metrics_tip.get('df_novedades'))
        
        # Add metrics
        for key, value in metrics_tip.items():
            if key != 'df_novedades':  # Don't add DataFrame to metrics
                context.add_metric(f'tipificador_{key}', value)
        
        logger.info(f"✅ Tipificador processed: {metrics_tip['total_valid']} valid, {metrics_tip['total_novedades']} novedades")
        
        # 2. Process Digital
        logger.info("\n[2/3] Processing Digital sales...")
        df_digital_raw = context.get_data('digital_raw')
        
        df_digital, metrics_dig = DigitalProcessor.process(
            df_digital_raw,
            self.digital_cols_map,
            self.start_date,
            self.end_date
        )
        
        context.add_data('digital_valid', df_digital)
        context.add_data('digital_novedades', metrics_dig.get('df_novedades'))
        
        # Add metrics
        for key, value in metrics_dig.items():
            if key != 'df_novedades':
                context.add_metric(f'digital_{key}', value)
        
        logger.info(f"✅ Digital processed: {metrics_dig['total_valid']} valid, {metrics_dig['total_novedades']} novedades")
        
        # 3. Process Historical
        logger.info("\n[3/3] Processing Historical sales...")
        df_historical_raw = context.get_data('historical_raw')
        
        df_historical, metrics_hist = HistoricalSalesProcessor.process(df_historical_raw)
        
        context.add_data('historical_valid', df_historical)
        
        # Add metrics
        for key, value in metrics_hist.items():
            context.add_metric(f'historical_{key}', value)
        
        logger.info(f"✅ Historical processed: {metrics_hist['total_processed']} records")
        
        logger.info(f"\n✅ Validation & processing completed")
        
        return context
