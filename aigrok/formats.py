"""
File format validation and handling.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class FormatValidationResult:
    """Result of format validation."""

    is_valid: bool
    format_name: Optional[str] = None
    error: Optional[str] = None


def get_supported_formats() -> Dict[str, str]:
    """Get mapping of supported file extensions to format names."""
    return {".pdf": "PDF Document", ".txt": "Plain Text"}


def validate_format(
    file_path: str, type_hint: Optional[str] = None
) -> FormatValidationResult:
    """Validate file format.

    Args:
        file_path: Path to file to validate
        type_hint: Optional type hint to override extension check

    Returns:
        Validation result
    """
    if not file_path:
        return FormatValidationResult(False, None, "Invalid filename")

    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        return FormatValidationResult(False, None, f"File not found: {file_path}")

    # Get supported formats
    formats = get_supported_formats()

    # If type hint provided, validate against that
    if type_hint:
        type_hint = type_hint.lower()
        ext = f".{type_hint}"
        if ext not in formats:
            return FormatValidationResult(
                False, None, f"Invalid file type: {type_hint}"
            )

        # If type hint doesn't match actual extension, it's invalid
        if path.suffix.lower() != ext:
            return FormatValidationResult(
                False, None, f"File extension doesn't match type hint: {type_hint}"
            )

    # Check extension
    ext = path.suffix.lower()
    if not ext:
        return FormatValidationResult(False, None, "No file extension")

    if ext not in formats:
        return FormatValidationResult(False, None, f"Unsupported file format: {ext}")

    # Basic content validation
    try:
        content = path.read_bytes()
        if ext == ".pdf":
            if not content.startswith(b"%PDF-"):
                return FormatValidationResult(False, None, "Not a valid PDF file")
        elif ext == ".txt":
            try:
                content.decode("utf-8")
            except UnicodeDecodeError:
                return FormatValidationResult(False, None, "Not a valid text file")
    except Exception as e:
        return FormatValidationResult(False, None, f"Error reading file: {e}")

    return FormatValidationResult(True, formats[ext])
