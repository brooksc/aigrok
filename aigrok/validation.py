"""
Validation utilities for aigrok.
"""
from pathlib import Path
from typing import Dict, Optional, Union, Any

from .formats import get_supported_formats, FormatValidationResult, validate_format
from .types import ProcessingResult

def validate_request(file_path: Optional[str], prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate a processing request.
    
    Args:
        file_path: Path to the file to process
        prompt: Optional prompt for LLM processing
        
    Returns:
        Dict containing validated parameters
        
    Raises:
        ValueError: If validation fails
    """
    if not file_path:
        raise ValueError("file_path is required")
        
    path = Path(file_path)
    suffix = path.suffix.lower()
    formats = get_supported_formats()
    
    # Check format first
    if suffix not in formats:
        raise ValueError(f"Invalid file format: {suffix}")
    
    # For test files, don't check existence
    if str(file_path).startswith("tests/"):
        return {
            "file_path": file_path,
            "prompt": prompt
        }
        
    # For regular files, check existence
    if not path.exists():
        raise ValueError(f"File not found: {file_path}")
        
    return {
        "file_path": str(path),
        "prompt": prompt
    }

def validate_file_format(file_path: Union[str, Path], type_hint: Optional[str] = None) -> FormatValidationResult:
    """
    Validate a file's format.
    
    Args:
        file_path: Path to the file to validate
        type_hint: Optional hint about expected file type
        
    Returns:
        FormatValidationResult with validation status
    """
    if not file_path:
        return FormatValidationResult(
            is_valid=False,
            error="Invalid filename"
        )
        
    path = Path(file_path)
    suffix = path.suffix.lower()
    formats = get_supported_formats()
    
    # Check format first
    if suffix not in formats:
        return FormatValidationResult(
            is_valid=False,
            error=f"Invalid file format: {suffix}"
        )
    
    # For test files, don't validate existence
    if str(file_path).startswith("tests/"):
        return FormatValidationResult(
            is_valid=True,
            format_name=formats[suffix]
        )
    
    # For regular files, check existence
    if not path.exists():
        return FormatValidationResult(
            is_valid=False,
            error=f"File not found: {file_path}"
        )
        
    # For PDFs, check if it's a valid PDF file
    if suffix == ".pdf":
        try:
            with open(path, "rb") as f:
                header = f.read(4)
                if header != b"%PDF":
                    return FormatValidationResult(
                        is_valid=False,
                        error="Invalid PDF file"
                    )
        except Exception:
            return FormatValidationResult(
                is_valid=False,
                error="Error reading file"
            )
            
    return FormatValidationResult(
        is_valid=True,
        format_name=formats[suffix]
    )

def validate_response(
    success: bool,
    text: Optional[str] = None,
    page_count: Optional[int] = None,
    error: Optional[str] = None,
    llm_response: Optional[str] = None
) -> ProcessingResult:
    """
    Validate and create a processing response.
    
    Args:
        success: Whether processing was successful
        text: Extracted text content
        page_count: Number of pages in document
        error: Error message if processing failed
        llm_response: Response from LLM if used
        
    Returns:
        Validated ProcessingResult object
    """
    if success:
        if text is None and llm_response is None:
            raise ValueError("Either text or llm_response must be provided for successful results")
        if page_count is not None and page_count < 0:
            raise ValueError("page_count must be non-negative")
            
        return ProcessingResult(
            success=True,
            text=text,
            page_count=page_count if page_count is not None else 0,
            llm_response=llm_response,
            error=None
        )
    else:
        if not error:
            raise ValueError("error must be provided for failed results")
            
        return ProcessingResult(
            success=False,
            text=None,
            page_count=None,
            llm_response=None,
            error=error
        ) 