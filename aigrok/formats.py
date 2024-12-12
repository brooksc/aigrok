"""
File format handling and validation.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from loguru import logger

SUPPORTED_FORMATS = {
    '.pdf': 'PDF Document',
    '.txt': 'Plain Text'
}

@dataclass
class FormatValidationResult:
    """Result of format validation."""
    is_valid: bool
    format_name: Optional[str] = None
    error: Optional[str] = None

def validate_format(file_path: str | Path, type_hint: Optional[str] = None) -> FormatValidationResult:
    """
    Validate if a file format is supported.
   
    Args:
        file_path: Path to the file
        type_hint: Optional type hint (e.g., 'pdf', 'text')
       
    Returns:
        FormatValidationResult indicating if format is supported
    """
    file_path = Path(file_path)
   
    # If type hint is provided, validate it first
    if type_hint:
        # Handle mock objects in tests
        if hasattr(type_hint, 'strip'):
            # Check for whitespace in original type hint
            if type_hint != type_hint.strip():
                return FormatValidationResult(
                    is_valid=False,
                    error=f"Invalid type hint: contains whitespace. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
                )
           
            # Convert to lowercase for comparison
            type_hint = type_hint.lower()
            if not type_hint:
                return FormatValidationResult(
                    is_valid=False,
                    error=f"Empty type hint. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
                )
           
            # Handle type hints with or without dot
            hint_ext = f".{type_hint}" if not type_hint.startswith('.') else type_hint
            if hint_ext in SUPPORTED_FORMATS:
                return FormatValidationResult(
                    is_valid=True,
                    format_name=SUPPORTED_FORMATS[hint_ext]
                )
        return FormatValidationResult(
            is_valid=False,
            error=f"Unsupported format type: {type_hint}. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
        )
   
    # Handle files with no extension
    ext = file_path.suffix.lower()
    if not ext:
        return FormatValidationResult(
            is_valid=False,
            error=f"Unsupported file format: no extension. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
        )
   
    # Handle hidden files (starting with dot)
    name_parts = file_path.name.split('.')
    if len(name_parts) > 2:
        # Special case for hidden files with valid extensions
        if name_parts[0] == '' and len(name_parts) == 3:
            ext = f".{name_parts[-1].lower()}"
            if ext in SUPPORTED_FORMATS:
                return FormatValidationResult(
                    is_valid=True,
                    format_name=SUPPORTED_FORMATS[ext]
                )
        return FormatValidationResult(
            is_valid=False,
            error=f"Ambiguous file format: multiple extensions detected. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
        )
   
    # Check if extension is supported
    if ext in SUPPORTED_FORMATS:
        return FormatValidationResult(
            is_valid=True,
            format_name=SUPPORTED_FORMATS[ext]
        )
   
    return FormatValidationResult(
        is_valid=False,
        error=f"Unsupported file format: {ext}. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
    )

def get_supported_formats() -> Dict[str, str]:
    """Get dictionary of supported formats and their descriptions."""
    return SUPPORTED_FORMATS.copy()