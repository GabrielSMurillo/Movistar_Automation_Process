"""
Base classes for pipeline framework.

Defines the core abstractions for building data processing pipelines:
- PipelineContext: Data container passed between stages
- PipelineStage: Abstract base for pipeline stages
- Pipeline: Orchestrates stage execution
- PipelineConfig: Configuration management
- PipelineResult: Final result with metrics

Example:
    >>> class MyStage(PipelineStage):
    ...     def execute(self, context: PipelineContext) -> PipelineContext:
    ...         # Process data
    ...         return context
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & TYPES
# ============================================================================

class StageStatus(str, Enum):
    """Status of a pipeline stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStatus(str, Enum):
    """Overall pipeline status."""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PipelineContext:
    """
    Context passed between pipeline stages.
    
    Contains all data, metadata, metrics, and errors accumulated
    during pipeline execution.
    
    Attributes:
        data: Dictionary of DataFrames (keyed by source name)
        metadata: Pipeline-level metadata
        metrics: Collected metrics from stages
        errors: List of error messages
        warnings: List of warning messages
        stage_results: Results from each stage
    """
    
    # Data containers
    data: Dict[str, pd.DataFrame] = field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Stage tracking
    stage_results: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if any warnings occurred."""
        return len(self.warnings) > 0
    
    def add_error(self, error: str, stage: Optional[str] = None) -> None:
        """Add an error message."""
        if stage:
            error = f"[{stage}] {error}"
        self.errors.append(error)
    
    def add_warning(self, warning: str, stage: Optional[str] = None) -> None:
        """Add a warning message."""
        if stage:
            warning = f"[{stage}] {warning}"
        self.warnings.append(warning)
    
    def add_dataframe(self, name: str, df: pd.DataFrame) -> None:
        """Add a DataFrame to the context."""
        self.data[name] = df
        logger.debug(f"Added DataFrame '{name}' with {len(df):,} rows")
    
    def get_dataframe(self, name: str) -> Optional[pd.DataFrame]:
        """Get a DataFrame from the context."""
        return self.data.get(name)
    
    def set_metric(self, key: str, value: Any) -> None:
        """Set a metric value."""
        self.metrics[key] = value
    
    def get_metric(self, key: str, default: Any = None) -> Any:
        """Get a metric value."""
        return self.metrics.get(key, default)
    
    def elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class PipelineConfig:
    """
    Pipeline configuration.
    
    Attributes:
        name: Pipeline name
        stop_on_error: Stop pipeline on first error
        stop_on_warning: Stop pipeline on warnings
        validate_inputs: Run input validation
        validate_outputs: Run output validation
        parallel_execution: Enable parallel stage execution
        max_workers: Max parallel workers
        cache_enabled: Enable caching
        log_level: Logging level
        config: Additional configuration dict
    """
    
    name: str = "MovistarPipeline"
    stop_on_error: bool = True
    stop_on_warning: bool = False
    validate_inputs: bool = True
    validate_outputs: bool = True
    parallel_execution: bool = False
    max_workers: int = 4
    cache_enabled: bool = True
    log_level: str = "INFO"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """
    Result of pipeline execution.
    
    Attributes:
        status: Overall status
        context: Final pipeline context
        total_time: Total execution time (seconds)
        stages_executed: Number of stages executed
        stages_failed: Number of stages that failed
        error_count: Total errors
        warning_count: Total warnings
    """
    
    status: PipelineStatus
    context: PipelineContext
    total_time: float
    stages_executed: int
    stages_failed: int = 0
    error_count: int = 0
    warning_count: int = 0
    
    @property
    def success(self) -> bool:
        """Check if pipeline succeeded."""
        return self.status == PipelineStatus.COMPLETED
    
    def summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        return {
            'status': self.status.value,
            'success': self.success,
            'total_time': f"{self.total_time:.2f}s",
            'stages_executed': self.stages_executed,
            'stages_failed': self.stages_failed,
            'errors': self.error_count,
            'warnings': self.warning_count,
            'dataframes_generated': len(self.context.data),
        }


# ============================================================================
# PIPELINE STAGE
# ============================================================================

class PipelineStage(ABC):
    """
    Abstract base class for pipeline stages.
    
    All pipeline stages must implement execute() method.
    Optionally override validate_inputs() for input validation.
    
    Attributes:
        name: Stage name
        config: Stage-specific configuration
        status: Current status
        logger: Stage logger
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize pipeline stage.
        
        Args:
            name: Stage name (defaults to class name)
            config: Stage configuration
        """
        self.name = name or self.__class__.__name__
        self.config = config or {}
        self.status = StageStatus.PENDING
        self.logger = logging.getLogger(f"pipeline.{self.name}")
        
        # Metrics
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.records_processed: int = 0
        self.records_failed: int = 0
    
    @abstractmethod
    def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute this stage.
        
        Args:
            context: Pipeline context
            
        Returns:
            Updated pipeline context
            
        Raises:
            Exception: If stage execution fails
        """
        pass
    
    def validate_inputs(self, context: PipelineContext) -> bool:
        """
        Validate inputs before execution.
        
        Override in subclasses for custom validation.
        
        Args:
            context: Pipeline context
            
        Returns:
            True if inputs are valid
        """
        return True
    
    def on_start(self, context: PipelineContext) -> None:
        """Hook called before execute()."""
        self.status = StageStatus.RUNNING
        self.start_time = datetime.now()
        self.logger.info(f"▶️  Starting stage: {self.name}")
    
    def on_success(self, context: PipelineContext) -> None:
        """Hook called on successful execution."""
        self.status = StageStatus.COMPLETED
        self.end_time = datetime.now()
        elapsed = (self.end_time - self.start_time).total_seconds()
        self.logger.info(f"✅ Stage '{self.name}' completed in {elapsed:.2f}s")
    
    def on_failure(self, context: PipelineContext, error: Exception) -> None:
        """Hook called on failure."""
        self.status = StageStatus.FAILED
        self.end_time = datetime.now()
        self.logger.error(f"❌ Stage '{self.name}' failed: {error}")
        context.add_error(str(error), self.name)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get stage metrics."""
        elapsed = None
        if self.start_time and self.end_time:
            elapsed = (self.end_time - self.start_time).total_seconds()
        
        return {
            'name': self.name,
            'status': self.status.value,
            'elapsed_time': elapsed,
            'records_processed': self.records_processed,
            'records_failed': self.records_failed,
        }
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}', status={self.status.value})"


# ============================================================================
# PIPELINE
# ============================================================================

class Pipeline:
    """
    Data processing pipeline orchestrator.
    
    Executes a sequence of stages, passing context between them.
    Handles error recovery, logging, and metrics collection.
    
    Example:
        >>> pipeline = Pipeline([
        ...     IngestionStage(),
        ...     ValidationStage(),
        ...     TransformationStage(),
        ... ])
        >>> result = pipeline.execute()
        >>> if result.success:
        ...     print("Pipeline succeeded!")
    """
    
    def __init__(
        self,
        stages: List[PipelineStage],
        config: Optional[PipelineConfig] = None
    ):
        """
        Initialize pipeline.
        
        Args:
            stages: List of pipeline stages to execute
            config: Pipeline configuration
        """
        self.stages = stages
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger(f"pipeline.{self.config.name}")
        
        # Execution state
        self.context: Optional[PipelineContext] = None
        self.result: Optional[PipelineResult] = None
    
    def execute(self) -> PipelineResult:
        """
        Execute the pipeline.
        
        Runs all stages in sequence, handling errors and collecting metrics.
        
        Returns:
            PipelineResult with execution details
        """
        self.logger.info("=" * 80)
        self.logger.info(f"🚀 STARTING PIPELINE: {self.config.name}")
        self.logger.info("=" * 80)
        self.logger.info(f"Total stages: {len(self.stages)}")
        self.logger.info(f"Stop on error: {self.config.stop_on_error}")
        self.logger.info("=" * 80)
        
        # Initialize context
        context = PipelineContext()
        context.start_time = datetime.now()
        context.metadata['pipeline_name'] = self.config.name
        context.metadata['pipeline_config'] = self.config
        
        stages_executed = 0
        stages_failed = 0
        
        # Execute stages
        for i, stage in enumerate(self.stages, 1):
            self.logger.info(f"\n[Stage {i}/{len(self.stages)}] {stage.name}")
            
            try:
                # Validate inputs
                if self.config.validate_inputs:
                    if not stage.validate_inputs(context):
                        raise ValueError(f"Input validation failed for stage: {stage.name}")
                
                # Execute stage
                stage.on_start(context)
                context = stage.execute(context)
                stage.on_success(context)
                
                # Store metrics
                context.stage_results[stage.name] = stage.get_metrics()
                stages_executed += 1
                
                # Check for errors
                if context.has_errors():
                    self.logger.warning(f"⚠️  Stage completed with {len(context.errors)} errors")
                    if self.config.stop_on_error:
                        self.logger.error("Stopping pipeline due to errors")
                        break
                
                # Check for warnings
                if context.has_warnings():
                    self.logger.warning(f"⚠️  Stage completed with {len(context.warnings)} warnings")
                    if self.config.stop_on_warning:
                        self.logger.error("Stopping pipeline due to warnings")
                        break
                
            except Exception as e:
                stage.on_failure(context, e)
                stages_failed += 1
                
                if self.config.stop_on_error:
                    self.logger.error(f"Pipeline aborted due to error in stage: {stage.name}")
                    break
        
        # Finalize
        context.end_time = datetime.now()
        total_time = context.elapsed_time() or 0
        
        # Determine status
        if stages_failed > 0:
            status = PipelineStatus.FAILED if stages_failed == len(self.stages) else PipelineStatus.PARTIAL
        elif context.has_errors():
            status = PipelineStatus.PARTIAL
        else:
            status = PipelineStatus.COMPLETED
        
        # Create result
        result = PipelineResult(
            status=status,
            context=context,
            total_time=total_time,
            stages_executed=stages_executed,
            stages_failed=stages_failed,
            error_count=len(context.errors),
            warning_count=len(context.warnings)
        )
        
        self.result = result
        self.context = context
        
        # Log summary
        self._log_summary(result)
        
        return result
    
    def _log_summary(self, result: PipelineResult) -> None:
        """Log execution summary."""
        self.logger.info("\n" + "=" * 80)
        
        if result.success:
            self.logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        elif result.status == PipelineStatus.PARTIAL:
            self.logger.warning("⚠️  PIPELINE COMPLETED WITH ERRORS")
        else:
            self.logger.error("❌ PIPELINE FAILED")
        
        self.logger.info("=" * 80)
        self.logger.info(f"Status: {result.status.value}")
        self.logger.info(f"Total time: {result.total_time:.2f}s")
        self.logger.info(f"Stages executed: {result.stages_executed}/{len(self.stages)}")
        self.logger.info(f"Stages failed: {result.stages_failed}")
        self.logger.info(f"Errors: {result.error_count}")
        self.logger.info(f"Warnings: {result.warning_count}")
        self.logger.info(f"DataFrames: {len(result.context.data)}")
        
        # List DataFrames
        if result.context.data:
            self.logger.info("\nGenerated DataFrames:")
            for name, df in result.context.data.items():
                self.logger.info(f"  • {name}: {len(df):,} rows, {len(df.columns)} columns")
        
        self.logger.info("=" * 80)


# Export public API
__all__ = [
    'PipelineContext',
    'PipelineStage',
    'Pipeline',
    'PipelineConfig',
    'PipelineResult',
    'StageStatus',
    'PipelineStatus',
]
