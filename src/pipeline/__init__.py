"""
Pipeline Framework for Data Processing.

This module provides a structured, stage-based pipeline for processing
Movistar sales data. Each stage is independent, testable, and composable.

Architecture:
    Pipeline
    ├── IngestionStage: Load data from sources
    ├── ValidationStage: Validate data quality
    ├── TransformationStage: Transform and enrich data
    ├── DeduplicationStage: Remove duplicates
    └── OutputStage: Generate output files

Example:
    >>> from src.pipeline import Pipeline, PipelineConfig
    >>> from src.pipeline.stages import *
    >>> 
    >>> pipeline = Pipeline([
    ...     IngestionStage(),
    ...     ValidationStage(),
    ...     TransformationStage(),
    ...     OutputStage()
    ... ])
    >>> 
    >>> result = pipeline.execute()
"""

from src.pipeline.base import (
    PipelineContext,
    PipelineStage,
    Pipeline,
    PipelineConfig,
    PipelineResult
)

__all__ = [
    'PipelineContext',
    'PipelineStage',
    'Pipeline',
    'PipelineConfig',
    'PipelineResult',
]

__version__ = '1.0.0'
