"""
Refactored main entry point using clean architecture and pipeline pattern.

This new main.py uses:
- Pipeline orchestration for clear data flow
- Separated stages for each processing step
- Proper error handling and logging
- Type-safe configuration

To use: python main_refactored.py
"""

import logging
import logging.config
import sys
from datetime import datetime
from pathlib import Path

# Import configuration
from config import (
    TIPIFICADOR_CONFIG,
    DIGITAL_CONFIG,
    HISTORICAL_SALES_CONFIG,
    INPUT_DIR,
    OUTPUT_FILES,
    TIPIFICADOR_COLS_MAP,
    DIGITAL_COLS_MAP,
    START_DATE,
    END_DATE,
    LOGGING_CONFIG,
    get_output_dir,
)

# Import new pipeline architecture
from src.pipeline.orchestrator import DataPipeline, PipelineContext
from src.pipeline.stages import (
    IngestionStage,
    ValidationStageImpl,
    TransformationStage,
    OutputStage,
)

# Get logger
logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure logging system."""
    logging.config.dictConfig(LOGGING_CONFIG)


def create_pipeline() -> DataPipeline:
    """
    Create and configure the data processing pipeline.
    
    Returns:
        Configured pipeline ready to execute
    """
    # Get output directory with date
    output_dir = get_output_dir()
    
    # Create pipeline
    pipeline = DataPipeline(name="Movistar Sales Automation Pipeline")
    
    # Stage 1: Data Ingestion
    tipificador_config = {
        **TIPIFICADOR_CONFIG,
        'file_path': INPUT_DIR / TIPIFICADOR_CONFIG['file_name']
    }
    digital_config = {
        **DIGITAL_CONFIG,
        'file_path': INPUT_DIR / DIGITAL_CONFIG['file_name']
    }
    
    pipeline.add_stage(
        IngestionStage(
            tipificador_config=tipificador_config,
            digital_config=digital_config,
            historical_config=HISTORICAL_SALES_CONFIG
        )
    )
    
    # Stage 2: Validation & Processing
    pipeline.add_stage(
        ValidationStageImpl(
            tipificador_cols_map=TIPIFICADOR_COLS_MAP,
            digital_cols_map=DIGITAL_COLS_MAP,
            start_date=START_DATE,
            end_date=END_DATE
        )
    )
    
    # Stage 3: Transformation & Consolidation
    pipeline.add_stage(
        TransformationStage()
    )
    
    # Stage 4: Output Generation
    pipeline.add_stage(
        OutputStage(
            output_files=OUTPUT_FILES,
            output_dir=output_dir
        )
    )
    
    return pipeline


def main() -> int:
    """
    Main entry point for the refactored pipeline.
    
    Returns:
        0 if successful, 1 if errors occurred
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Banner
    logger.info("=" * 80)
    logger.info("🚀 MOVISTAR SALES AUTOMATION - REFACTORED ARCHITECTURE")
    logger.info("=" * 80)
    logger.info(f"📅 Period: {START_DATE.strftime('%d/%m/%Y')} → {END_DATE.strftime('%d/%m/%Y')}")
    logger.info(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📁 Output: {get_output_dir().name}")
    logger.info("=" * 80)
    
    try:
        # Create pipeline
        logger.info("\n🔧 Configuring pipeline...")
        pipeline = create_pipeline()
        logger.info(f"✅ Pipeline configured with {len(pipeline.stages)} stages")
        
        # Execute pipeline
        context = pipeline.execute()
        
        # Check for errors
        if context.has_errors():
            logger.error("\n❌ Pipeline completed with errors")
            logger.error(f"Errors: {len(context.errors)}")
            for error in context.errors:
                logger.error(f"  • {error}")
            return 1
        
        # Success summary
        logger.info("\n" + "=" * 80)
        logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        
        # Display key metrics
        if context.metrics:
            logger.info("\n📊 Key Metrics:")
            logger.info(f"  • Valid ventas: {context.metrics.get('tipificador_total_valid', 0):,}")
            logger.info(f"  • Valid digital: {context.metrics.get('digital_total_valid', 0):,}")
            logger.info(f"  • Novedades: {context.metrics.get('total_novedades', 0):,}")
            logger.info(f"  • Monthly consolidated: {context.metrics.get('monthly_total_consolidated', 0):,}")
            logger.info(f"  • Contact log records: {context.metrics.get('contact_log_records', 0):,}")
        
        logger.info(f"\n📁 Output directory: {context.metrics.get('output_directory', 'N/A')}")
        logger.info(f"⏱️  Total time: {context.get_elapsed_time():.2f}s")
        logger.info("=" * 80)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"\n❌ CRITICAL ERROR: {e}", exc_info=True)
        return 1
    
    finally:
        logger.info(f"\n⏰ End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    sys.exit(main())
