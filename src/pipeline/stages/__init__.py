"""
Concrete pipeline stages for the Movistar Automation System.
"""

from .ingestion_stage import IngestionStage
from .validation_stage_impl import ValidationStageImpl
from .transformation_stage import TransformationStage
from .output_stage import OutputStage

__all__ = [
    "IngestionStage",
    "ValidationStageImpl",
    "TransformationStage",
    "OutputStage",
]
