"""
Core configuration module with Pydantic validation.

This module provides a robust, type-safe configuration system using Pydantic.
Supports environment variables, validation, and multiple profiles (dev/prod).

Example:
 >>> from src.core.config import get_settings
 >>> settings = get_settings()
 >>> print(settings.input_dir)
 PosixPath('/path/to/input')
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator, field_validator
from pathlib import Path
from typing import Optional, Literal
from datetime import date, timedelta
from enum import Enum

class Environment(str, Enum):
 """Supported environments."""
 DEVELOPMENT = "development"
 STAGING = "staging"
 PRODUCTION = "production"

class Settings(BaseSettings):
 """
 Application settings with automatic validation.
 
 Settings are loaded from:
 1. Environment variables (prefixed with MOVISTAR_)
 2. .env file
 3. Default values
 
 Attributes:
 env: Current environment (development/staging/production)
 debug: Enable debug mode
 base_dir: Root directory of the project
 data_dir: Data directory
 input_dir: Input files directory
 output_dir: Output files directory
 logs_dir: Logs directory
 tracking_dir: Tracking files directory
 start_date: Processing start date (default: first day of current month)
 end_date: Processing end date (default: yesterday)
 max_workers: Maximum parallel workers
 chunk_size: Chunk size for large file processing
 enable_cache: Enable caching
 cache_ttl: Cache TTL in seconds
 max_null_rate: Maximum allowed null rate
 max_duplicate_rate: Maximum allowed duplicate rate
 min_phone_length: Minimum phone number length
 max_phone_length: Maximum phone number length
 log_level: Logging level
 log_to_file: Enable file logging
 log_rotation_size: Log file rotation size in bytes
 log_backup_count: Number of backup log files
 """
 
 model_config = SettingsConfigDict(
 env_file=".env",
 env_file_encoding="utf-8",
 env_prefix="MOVISTAR_",
 case_sensitive=False,
 extra="ignore"
 )
 
 # ===== ENVIRONMENT =====
 env: Environment = Field(default=Environment.DEVELOPMENT)
 debug: bool = Field(default=False)
 
 # ===== PATHS =====
 base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
 
 @property
 def data_dir(self) -> Path:
 """Data directory."""
 return self.base_dir / "data"
 
 @property
 def input_dir(self) -> Path:
 """Input directory."""
 return self.data_dir / "input"
 
 @property
 def output_dir(self) -> Path:
 """Output directory."""
 return self.data_dir / "output"
 
 @property
 def logs_dir(self) -> Path:
 """Logs directory."""
 return self.base_dir / "logs"
 
 @property
 def tracking_dir(self) -> Path:
 """Tracking directory."""
 return self.data_dir / "tracking"
 
 @property
 def processed_dir(self) -> Path:
 """Processed files directory."""
 return self.data_dir / "processed"
 
 # ===== PROCESSING DATES =====
 start_date: Optional[date] = Field(default=None)
 end_date: Optional[date] = Field(default=None)
 
 @field_validator('start_date', mode='before')
 @classmethod
 def set_start_date(cls, v) -> date:
 """Set default start date to first day of current month."""
 if v is None or v == '':
 return date.today().replace(day=1)
 if isinstance(v, str):
 return date.fromisoformat(v)
 return v
 
 @field_validator('end_date', mode='before')
 @classmethod
 def set_end_date(cls, v) -> date:
 """Set default end date to yesterday."""
 if v is None or v == '':
 return date.today() - timedelta(days=1)
 if isinstance(v, str):
 return date.fromisoformat(v)
 return v
 
 # ===== PERFORMANCE =====
 max_workers: int = Field(default=4, ge=1, le=16)
 chunk_size: int = Field(default=10000, ge=1000, le=100000)
 enable_cache: bool = Field(default=True)
 cache_ttl: int = Field(default=3600, ge=60)
 
 # ===== QUALITY THRESHOLDS =====
 max_null_rate: float = Field(default=0.30, ge=0.0, le=1.0)
 max_duplicate_rate: float = Field(default=0.15, ge=0.0, le=1.0)
 min_phone_length: int = Field(default=7, ge=5, le=10)
 max_phone_length: int = Field(default=10, ge=7, le=15)
 
 # ===== LOGGING =====
 log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
 log_to_file: bool = Field(default=True)
 log_rotation_size: int = Field(default=10485760) # 10MB
 log_backup_count: int = Field(default=5)
 
 # ===== FEATURE FLAGS =====
 enable_parallel_processing: bool = Field(default=False)
 enable_notifications: bool = Field(default=False)
 enable_auto_backup: bool = Field(default=True)
 
 # ===== DATABASE (Future) =====
 db_url: Optional[str] = Field(default=None)
 db_pool_size: int = Field(default=5)
 
 def create_directories(self) -> None:
 """Create all required directories if they don't exist."""
 directories = [
 self.data_dir,
 self.input_dir,
 self.output_dir,
 self.logs_dir,
 self.tracking_dir,
 self.processed_dir,
 ]
 
 for directory in directories:
 directory.mkdir(parents=True, exist_ok=True)
 
 @property
 def date_range_str(self) -> str:
 """Get formatted date range string for file names."""
 return f"{self.start_date.strftime('%d')}_Al_{self.end_date.strftime('%d')}_{self.start_date.strftime('%b').upper()}_{self.start_date.year}"
 
 @property
 def date_range_str_short(self) -> str:
 """Get short formatted date range string."""
 return f"{self.start_date.strftime('%d')}_A_{self.end_date.strftime('%d')}_{self.start_date.strftime('%b').upper()}"
 
 def is_production(self) -> bool:
 """Check if running in production environment."""
 return self.env == Environment.PRODUCTION
 
 def is_development(self) -> bool:
 """Check if running in development environment."""
 return self.env == Environment.DEVELOPMENT

# Singleton instance
_settings: Optional[Settings] = None

def get_settings(force_reload: bool = False) -> Settings:
 """
 Get settings singleton instance.
 
 Args:
 force_reload: Force reload settings from environment
 
 Returns:
 Settings instance
 
 Example:
 >>> settings = get_settings()
 >>> print(settings.env)
 'development'
 """
 global _settings
 
 if _settings is None or force_reload:
 _settings = Settings()
 _settings.create_directories()
 
 return _settings

def reset_settings() -> None:
 """Reset settings singleton (useful for testing)."""
 global _settings
 _settings = None

# Export for convenience
__all__ = [
 "Settings",
 "Environment",
 "get_settings",
 "reset_settings",
]
