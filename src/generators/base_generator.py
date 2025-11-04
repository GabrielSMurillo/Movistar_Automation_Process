"""
Base Generator classes for file generation.

This module provides the abstract base class that all file generators
must implement, ensuring consistency and enabling the factory pattern.

Architecture:
    BaseGenerator (ABC)
    ├── ContactLogGenerator
    ├── FormatoMovistarGenerator
    ├── SVASGenerator
    └── MonthlyReportGenerator

Example:
    >>> class MyGenerator(BaseGenerator):
    ...     def generate(self, df, output_path):
    ...         # Implementation
    ...         pass
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    Abstract base class for all file generators.
    
    All generators must implement:
    - generate(): Main generation logic
    - validate_output(): Output validation
    - file_type: Property identifying generator type
    
    Attributes:
        config: Generator configuration
        records_processed: Counter for processed records
        records_skipped: Counter for skipped records
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize generator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.records_processed = 0
        self.records_skipped = 0
        self.generation_time: Optional[float] = None
        self.logger = logging.getLogger(f"generator.{self.file_type}")
    
    @property
    @abstractmethod
    def file_type(self) -> str:
        """
        Unique identifier for this generator type.
        
        Returns:
            String identifier (e.g., 'contact_log', 'svas')
        """
        pass
    
    @property
    def required_columns(self) -> List[str]:
        """
        List of required columns in input DataFrame.
        
        Override in subclasses to specify required columns.
        
        Returns:
            List of column names
        """
        return []
    
    @abstractmethod
    def generate(self, df: pd.DataFrame, output_path: Path) -> bool:
        """
        Generate the output file.
        
        Args:
            df: Input DataFrame with data to process
            output_path: Path where file should be saved
            
        Returns:
            True if generation successful, False otherwise
            
        Raises:
            ValueError: If input is invalid
            IOError: If file cannot be written
        """
        pass
    
    @abstractmethod
    def validate_output(self, file_path: Path) -> bool:
        """
        Validate the generated output file.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if validation passes, False otherwise
        """
        pass
    
    def validate_input(self, df: pd.DataFrame) -> bool:
        """
        Validate input DataFrame before generation.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if empty
        if df.empty:
            self.logger.warning(f"Empty DataFrame provided to {self.file_type}")
            return False
        
        # Check required columns
        if self.required_columns:
            missing_cols = set(self.required_columns) - set(df.columns)
            if missing_cols:
                self.logger.error(
                    f"Missing required columns for {self.file_type}: {missing_cols}"
                )
                return False
        
        return True
    
    def _reset_counters(self) -> None:
        """Reset processing counters."""
        self.records_processed = 0
        self.records_skipped = 0
    
    def _save_excel(
        self,
        df: pd.DataFrame,
        output_path: Path,
        sheet_name: str = 'Sheet1',
        apply_formatting: bool = True
    ) -> None:
        """
        Save DataFrame as Excel with optional formatting.
        
        Args:
            df: DataFrame to save
            output_path: Output file path
            sheet_name: Name of the Excel sheet
            apply_formatting: Whether to apply formatting
            
        Raises:
            IOError: If file cannot be written
        """
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            if apply_formatting:
                self._apply_excel_formatting(
                    writer,
                    sheet_name,
                    df
                )
        
        self.logger.debug(f"Excel file saved: {output_path.name}")
    
    def _apply_excel_formatting(
        self,
        writer: pd.ExcelWriter,
        sheet_name: str,
        df: pd.DataFrame
    ) -> None:
        """
        Apply default Excel formatting.
        
        Override in subclasses for custom formatting.
        
        Args:
            writer: ExcelWriter object
            sheet_name: Name of sheet to format
            df: DataFrame being written
        """
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Default header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Apply to headers
        for col_num, value in enumerate(df.columns):
            worksheet.write(0, col_num, value, header_format)
            
            # Auto-size columns
            max_len = max(
                df[value].astype(str).apply(len).max(),
                len(str(value))
            )
            worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get generation statistics.
        
        Returns:
            Dictionary with generation statistics
        """
        return {
            'file_type': self.file_type,
            'records_processed': self.records_processed,
            'records_skipped': self.records_skipped,
            'generation_time': self.generation_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def log_summary(self, output_path: Path, success: bool) -> None:
        """
        Log generation summary.
        
        Args:
            output_path: Path to generated file
            success: Whether generation was successful
        """
        if success:
            file_size = output_path.stat().st_size / 1024  # KB
            self.logger.info("=" * 80)
            self.logger.info(f"✅ {self.file_type.upper()} GENERATION SUCCESSFUL")
            self.logger.info("=" * 80)
            self.logger.info(f"   📁 File: {output_path.name}")
            self.logger.info(f"   📊 Records processed: {self.records_processed:,}")
            self.logger.info(f"   ⊘ Records skipped: {self.records_skipped:,}")
            self.logger.info(f"   💾 File size: {file_size:.2f} KB")
            if self.generation_time:
                self.logger.info(f"   ⏱️  Generation time: {self.generation_time:.2f}s")
            self.logger.info("=" * 80)
        else:
            self.logger.error("=" * 80)
            self.logger.error(f"❌ {self.file_type.upper()} GENERATION FAILED")
            self.logger.error("=" * 80)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(type='{self.file_type}')"


class GeneratorRegistry:
    """
    Registry for managing generator instances.
    
    Implements the Registry pattern to track and manage
    all available generators in the system.
    """
    
    _generators: Dict[str, type[BaseGenerator]] = {}
    
    @classmethod
    def register(cls, generator_class: type[BaseGenerator]) -> type[BaseGenerator]:
        """
        Register a generator class.
        
        Can be used as a decorator:
            @GeneratorRegistry.register
            class MyGenerator(BaseGenerator):
                ...
        
        Args:
            generator_class: Generator class to register
            
        Returns:
            The registered class (for decorator chaining)
        """
        # Create temporary instance to get file_type
        temp_instance = generator_class()
        file_type = temp_instance.file_type
        
        if file_type in cls._generators:
            logger.warning(
                f"Overwriting existing generator for type '{file_type}'"
            )
        
        cls._generators[file_type] = generator_class
        logger.debug(f"Registered generator: {file_type} -> {generator_class.__name__}")
        
        return generator_class
    
    @classmethod
    def get(cls, file_type: str) -> Optional[type[BaseGenerator]]:
        """
        Get generator class by file type.
        
        Args:
            file_type: File type identifier
            
        Returns:
            Generator class or None if not found
        """
        return cls._generators.get(file_type)
    
    @classmethod
    def list_generators(cls) -> List[str]:
        """
        List all registered generator types.
        
        Returns:
            List of file type identifiers
        """
        return list(cls._generators.keys())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registered generators (useful for testing)."""
        cls._generators.clear()


class GeneratorFactory:
    """
    Factory for creating generator instances.
    
    Provides a clean interface for creating generators without
    knowing their concrete classes.
    
    Example:
        >>> generator = GeneratorFactory.create('contact_log')
        >>> success = generator.generate(df, output_path)
    """
    
    @staticmethod
    def create(
        file_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseGenerator:
        """
        Create a generator instance.
        
        Args:
            file_type: Type of generator to create
            config: Optional configuration for the generator
            
        Returns:
            Configured generator instance
            
        Raises:
            ValueError: If generator type is not registered
            
        Example:
            >>> gen = GeneratorFactory.create('contact_log', {'validate': True})
            >>> gen.generate(df, Path('output.xlsx'))
        """
        generator_class = GeneratorRegistry.get(file_type)
        
        if generator_class is None:
            available = GeneratorRegistry.list_generators()
            raise ValueError(
                f"Unknown generator type: '{file_type}'\n"
                f"Available types: {available}"
            )
        
        logger.debug(f"Creating generator: {file_type} ({generator_class.__name__})")
        return generator_class(config)
    
    @staticmethod
    def list_available() -> List[str]:
        """
        List all available generator types.
        
        Returns:
            List of registered generator types
        """
        return GeneratorRegistry.list_generators()
    
    @staticmethod
    def create_all(config: Optional[Dict[str, Any]] = None) -> Dict[str, BaseGenerator]:
        """
        Create instances of all registered generators.
        
        Args:
            config: Optional configuration for all generators
            
        Returns:
            Dictionary mapping file_type to generator instance
        """
        return {
            file_type: GeneratorFactory.create(file_type, config)
            for file_type in GeneratorFactory.list_available()
        }


# Export public API
__all__ = [
    'BaseGenerator',
    'GeneratorFactory',
    'GeneratorRegistry',
]
