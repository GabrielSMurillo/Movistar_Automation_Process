"""
Output generation stage - creates final output files.
"""

import logging
from pathlib import Path

from src.pipeline.orchestrator import PipelineStage, PipelineContext
from src.file_generator import (
    generate_movistar_files,
    generate_internal_files,
    generate_monthly_report,
)
from src.generators.contact_log_generator import ContactLogGenerator

logger = logging.getLogger(__name__)


class OutputStage(PipelineStage):
    """
    Stage 4: Output Generation
    
    Responsibilities:
    - Generate all output files
    - Validate output format
    - Create output manifest
    - Generate novelty reports
    """
    
    def __init__(
        self,
        output_files: dict,
        output_dir: Path
    ):
        """
        Initialize output stage.
        
        Args:
            output_files: Output file configuration
            output_dir: Output directory path
        """
        super().__init__("Output Generation")
        self.output_files = output_files
        self.output_dir = Path(output_dir)
    
    def validate(self, context: PipelineContext) -> bool:
        """Validate that processed data is present."""
        if context.get_data('ventas_valid') is None:
            context.add_error("Valid ventas data not found for output")
            return False
        
        if context.get_data('digital_valid') is None:
            context.add_error("Valid digital data not found for output")
            return False
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def _execute(self, context: PipelineContext) -> PipelineContext:
        """Generate all output files."""
        
        # Get data from context
        df_ventas = context.get_data('ventas_valid')
        df_digital = context.get_data('digital_valid')
        df_monthly = context.get_data('monthly_consolidated')
        
        # 1. Generate Movistar files
        logger.info("\n[1/5] Generating Movistar files...")
        generate_movistar_files(df_ventas, self.output_files, self.output_dir)
        
        # 2. Generate internal files
        logger.info("\n[2/5] Generating internal files...")
        generate_internal_files(df_digital, df_ventas, self.output_files, self.output_dir)
        
        # 3. Generate monthly report
        logger.info("\n[3/5] Generating monthly report...")
        generate_monthly_report(df_monthly, df_digital, self.output_files, self.output_dir)
        
        # 4. Generate Contact Log
        logger.info("\n[4/5] Generating Contact Log...")
        try:
            contact_log_generator = ContactLogGenerator()
            contact_log_path = self.output_dir / self.output_files['movistar_contact_log']
            
            success = contact_log_generator.generate(
                df_ventas,
                contact_log_path,
                validate=True
            )
            
            if success:
                logger.info(
                    f"✅ Contact Log generated: {contact_log_generator.records_processed:,} records, "
                    f"{contact_log_generator.records_skipped:,} skipped"
                )
                context.add_metric('contact_log_records', contact_log_generator.records_processed)
            else:
                logger.warning("⚠️  Contact Log generation had issues")
        except Exception as e:
            logger.error(f"❌ Error generating Contact Log: {e}", exc_info=True)
            context.add_warning(f"Contact Log generation failed: {str(e)}")
        
        # 5. Generate Novelty Reports
        logger.info("\n[5/5] Generating Novelty Reports...")
        try:
            from src.services.novelty_detector import NoveltyDetector
            detector = NoveltyDetector()
            
            df_novedades_tip = context.get_data('tipificador_novedades')
            df_novedades_dig = context.get_data('digital_novedades')
            
            novelties_generated = 0
            
            if df_novedades_tip is not None and not df_novedades_tip.empty:
                novelty_tip_path = self.output_dir / f"Tipificador_Novedades_{self.output_files['date_range_short']}.xlsx"
                detector.generate_novelty_report(df_novedades_tip, str(novelty_tip_path))
                logger.info(f"  ✅ Tipificador novedades: {len(df_novedades_tip):,} records")
                novelties_generated += len(df_novedades_tip)
            
            if df_novedades_dig is not None and not df_novedades_dig.empty:
                novelty_dig_path = self.output_dir / f"Digital_Novedades_{self.output_files['date_range_short']}.xlsx"
                detector.generate_novelty_report(df_novedades_dig, str(novelty_dig_path))
                logger.info(f"  ✅ Digital novedades: {len(df_novedades_dig):,} records")
                novelties_generated += len(df_novedades_dig)
            
            if novelties_generated == 0:
                logger.info("  ℹ️  No novedades - all records are valid")
            
            context.add_metric('total_novedades', novelties_generated)
            
        except Exception as e:
            logger.error(f"❌ Error generating novelty reports: {e}", exc_info=True)
            context.add_warning(f"Novelty report generation failed: {str(e)}")
        
        logger.info(f"\n✅ All outputs generated in: {self.output_dir}")
        context.add_metric('output_directory', str(self.output_dir))
        
        return context
