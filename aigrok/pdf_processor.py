"""
PDF processing module for document analysis and text extraction.
"""
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from loguru import logger
from pypdf import PdfReader
import ollama

@dataclass
class ProcessingResult:
    """Container for PDF processing results."""
    success: bool
    text: Optional[str] = None
    metadata: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None
    page_count: int = 0
    llm_response: Optional[str] = None
    metadata_only: bool = False

class PDFProcessor:
    """Handles PDF document processing and text extraction."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        logger.debug("Initializing PDF processor")
        try:
            self.llm = ollama
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            self.llm = None
    
    def process_file(self, file_path: str | Path, prompt: Optional[str] = None, model: Optional[str] = None) -> ProcessingResult:
        """
        Process a PDF file and extract its contents, optionally analyzing with LLM.
        
        Args:
            file_path: Path to the PDF file
            prompt: Optional prompt for analysis
            model: Optional Ollama model name
            
        Returns:
            ProcessingResult containing extracted text, metadata, and optional llm response
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return ProcessingResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            if not file_path.suffix.lower() == '.pdf':
                return ProcessingResult(
                    success=False,
                    error=f"Not a PDF file: {file_path}"
                )
            
            # Extract text and metadata
            reader = PdfReader(str(file_path))
            
            # For title or author queries, just get first page text
            if prompt and ("title" in prompt.lower() or "author" in prompt.lower()):
                text = reader.pages[0].extract_text()[:1000]  # Just get first 1000 chars
            else:
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            metadata = reader.metadata
            result = ProcessingResult(
                success=True,
                text=text,
                metadata=metadata,
                page_count=len(reader.pages)
            )
            
            # Process with LLM if prompt provided
            if prompt and self.llm:
                try:
                    kwargs = {"prompt": f"{prompt}\n\nDocument text:\n{text}"}
                    if model:
                        kwargs["model"] = model
                    
                    response = self.llm.generate(**kwargs)
                    result.llm_response = response['response']
                except Exception as e:
                    logger.error(f"Error in LLM processing: {str(e)}")
                    result.error = f"PDF text extracted successfully, but analysis failed: {str(e)}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return ProcessingResult(
                success=False,
                error=str(e)
            ) 