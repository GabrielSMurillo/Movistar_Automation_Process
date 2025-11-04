"""
Pipeline orchestrator for the Movistar Automation System.

This module provides a high-level orchestration layer that coordinates
the execution of pipeline stages in the correct order.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, date
import pandas as pd

from src.core.config import get_settings
from src.core.models import ProcessingMetrics
from src.core.exceptions import ProcessingError, FileNotFoundError

logger = logging.getLogger(__name__)


class PipelineContext:
    """
    Context object that flows through pipeline stages.
    
    Contains all data, configuration, and state needed during processing.
    """
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize pipeline context."""
        self.config = config or get_settings()
        self.data: Dict[str, pd.DataFrame] = {}
        self.metrics: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            'start_time': datetime.now(),
            'pipeline_id': f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        }
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def add_data(self, key: str, df: pd.DataFrame) -> None:
        """Add a DataFrame to context."""
        self.data[key] = df
        logger.debug(f"Added data '{key}' to context: {len(df)} records")
    
    def get_data(self, key: str) -> Optional[pd.DataFrame]:
        """Get a DataFrame from context."""
        return self.data.get(key)
    
    def add_metric(self, key: str, value: Any) -> None:
        """Add a metric to context."""
        self.metrics[key] = value
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        logger.error(f"Pipeline error: {error}")
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
        logger.warning(f"Pipeline warning: {warning}")
    
    def has_errors(self) -> bool:
        """Check if context has errors."""
        return len(self.errors) > 0
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since pipeline start."""
        return (datetime.now() - self.metadata['start_time']).total_seconds()


class PipelineStage:
    """
    Base class for pipeline stages.
    
    Each stage is a step in the data processing pipeline with
    clear inputs, outputs, and responsibilities.
    """
    
    def __init__(self, name: str):
        """Initialize stage."""
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute this stage.
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context
        """
        self.logger.info(f"{'='*80}")
        self.logger.info(f"🔄 STAGE: {self.name}")
        self.logger.info(f"{'='*80}")
        
        start_time = datetime.now()
        
        try:
            # Validate preconditions
            if not self.validate(context):
                raise ProcessingError(
                    transformation=self.name,
                    reason="Stage validation failed"
                )
            
            # Execute stage logic
            context = self._execute(context)
            
            # Calculate stage metrics
            elapsed = (datetime.now() - start_time).total_seconds()
            context.add_metric(f"{self.name}_elapsed_seconds", elapsed)
            
            self.logger.info(f"✅ Stage '{self.name}' completed in {elapsed:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Stage '{self.name}' failed: {e}", exc_info=True)
            context.add_error(f"Stage '{self.name}' failed: {str(e)}")
            raise
        
        return context
    
    def validate(self, context: PipelineContext) -> bool:
        """
        Validate preconditions for this stage.
        
        Args:
            context: Pipeline context
        
        Returns:
            True if preconditions are met
        """
        return True
    
    def _execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute stage-specific logic.
        
        Subclasses must implement this method.
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context
        """
        raise NotImplementedError("Subclasses must implement _execute()")


class DataPipeline:
    """
    Main data processing pipeline.
    
    Coordinates execution of stages in sequence, manages state,
    and handles errors.
    """
    
    def __init__(
        self,
        name: str = "Movistar Sales Pipeline",
        config: Optional[Any] = None
    ):
        """
        Initialize pipeline.
        
        Args:
            name: Pipeline name
            config: Optional configuration object
        """
        self.name = name
        self.config = config or get_settings()
        self.stages: List[PipelineStage] = []
        self.logger = logging.getLogger(__name__)
    
    def add_stage(self, stage: PipelineStage) -> 'DataPipeline':
        """
        Add a stage to the pipeline.
        
        Args:
            stage: Pipeline stage to add
        
        Returns:
            Self for method chaining
        """
        self.stages.append(stage)
        self.logger.debug(f"Added stage: {stage.name}")
        return self
    
    def execute(self, initial_context: Optional[PipelineContext] = None) -> PipelineContext:
        """
        Execute the entire pipeline.
        
        Args:
            initial_context: Optional initial context
        
        Returns:
            Final context after all stages
        
        Raises:
            ProcessingError: If pipeline execution fails
        """
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🚀 PIPELINE: {self.name}")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"📊 Stages: {len(self.stages)}")
        self.logger.info(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"{'='*80}\n")
        
        # Initialize or use provided context
        context = initial_context or PipelineContext(self.config)
        
        try:
            # Execute each stage in sequence
            for i, stage in enumerate(self.stages, 1):
                self.logger.info(f"\n[Stage {i}/{len(self.stages)}] Starting: {stage.name}")
                
                context = stage.execute(context)
                
                # Check for errors after each stage
                if context.has_errors():
                    self.logger.error(
                        f"Pipeline stopped after stage '{stage.name}' due to errors"
                    )
                    break
            
            # Final summary
            self._log_summary(context)
            
            return context
            
        except KeyboardInterrupt:
            self.logger.warning("⚠️  Pipeline interrupted by user")
            context.add_error("Pipeline interrupted by user")
            raise
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            context.add_error(f"Pipeline failed: {str(e)}")
            raise ProcessingError(
                transformation="Pipeline",
                reason=str(e)
            ) from e
    
    def _log_summary(self, context: PipelineContext) -> None:
        """Log pipeline execution summary."""
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"📊 PIPELINE SUMMARY: {self.name}")
        self.logger.info(f"{'='*80}")
        
        # Timing
        elapsed = context.get_elapsed_time()
        self.logger.info(f"⏱️  Total execution time: {elapsed:.2f}s")
        
        # Data summary
        self.logger.info(f"\n📦 Data Objects:")
        for key, df in context.data.items():
            self.logger.info(f"  • {key}: {len(df):,} records")
        
        # Metrics
        if context.metrics:
            self.logger.info(f"\n📈 Metrics:")
            for key, value in context.metrics.items():
                if isinstance(value, float):
                    self.logger.info(f"  • {key}: {value:.2f}")
                else:
                    self.logger.info(f"  • {key}: {value}")
        
        # Errors and warnings
        if context.errors:
            self.logger.error(f"\n❌ Errors ({len(context.errors)}):")
            for error in context.errors:
                self.logger.error(f"  • {error}")
        
        if context.warnings:
            self.logger.warning(f"\n⚠️  Warnings ({len(context.warnings)}):")
            for warning in context.warnings:
                self.logger.warning(f"  • {warning}")
        
        # Status
        if context.has_errors():
            self.logger.error(f"\n{'='*80}")
            self.logger.error(f"❌ PIPELINE FAILED")
            self.logger.error(f"{'='*80}")
        else:
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"✅ PIPELINE COMPLETED SUCCESSFULLY")
            self.logger.info(f"{'='*80}")


# Export
__all__ = [
    "PipelineContext",
    "PipelineStage",
    "DataPipeline",
]
