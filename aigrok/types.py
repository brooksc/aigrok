"""
Common types and data structures.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ProcessingResult:
    """Result of processing a PDF file."""
    success: bool
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    page_count: int = 0
    error: Optional[str] = None
    llm_response: Optional[Any] = None 