"""Input adapters package."""

from .input_adapter import (
 InputAdapter,
 CSVAdapter,
 ExcelAdapter,
 InputAdapterFactory,
 read_file,
 get_file_info,
)

__all__ = [
 'InputAdapter',
 'CSVAdapter',
 'ExcelAdapter',
 'InputAdapterFactory',
 'read_file',
 'get_file_info',
]
