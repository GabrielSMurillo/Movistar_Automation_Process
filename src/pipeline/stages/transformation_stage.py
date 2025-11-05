"""
Data transformation and consolidation stage.
"""

import logging

from src.pipeline.orchestrator import PipelineStage, PipelineContext
from src.domain.processors import consolidate_monthly_report

logger = logging.getLogger(__name__)


class TransformationStage(PipelineStage):
    """
    Stage 3: Data Transformation & Consolidation
    
    Responsibilities:
    - Consolidate data from multiple sources
    - Apply final transformations
    - Deduplicate records
    - Prepare data for output
    """
    
    def __init__(self):
        """Initialize transformation stage."""
        super().__init__("Data Transformation & Consolidation")
    
    def validate(self, context: PipelineContext) -> bool:
        """Validate that validated data is present."""
        if context.get_data('ventas_valid') is None:
            context.add_error("Valid ventas data not found in context")
            return False
        
        if context.get_data('digital_valid') is None:
            context.add_error("Valid digital data not found in context")
            return False
        
        return True
    
    def _execute(self, context: PipelineContext) -> PipelineContext:
        """Consolidate and transform data."""
        
        logger.info("\nConsolidating monthly report...")
        
        # Get data from context
        df_ventas = context.get_data('ventas_valid')
        df_digital = context.get_data('digital_valid')
        df_historical = context.get_data('historical_valid')
        
        # Consolidate
        df_monthly, metrics_monthly = consolidate_monthly_report(
            df_ventas,
            df_digital,
            df_historical
        )
        
        # Store consolidated data
        context.add_data('monthly_consolidated', df_monthly)
        
        # Add metrics
        for key, value in metrics_monthly.items():
            context.add_metric(f'monthly_{key}', value)
        
        logger.info(f"✅ Monthly consolidation completed: {len(df_monthly):,} unique records")
        
        return context
