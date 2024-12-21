"""
Common types and data structures.
"""
# Import only what we need from typing
from typing_extensions import Optional, Dict, Any

from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

class ProcessingResult(BaseModel):
    """Result of processing a PDF file."""
    model_config = ConfigDict(
        extra='forbid',
        validate_default=True
    )
    
    success: bool
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    page_count: int = Field(default=0, ge=0)
    error: Optional[str] = None
    llm_response: Optional[Any] = None
    filename: Optional[str] = None  # Path to the processed file