"""
Document processing module for text extraction and analysis.
"""
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from loguru import logger
from pypdf import PdfReader
from .formats import validate_format

@dataclass
class ProcessingResult:
    """Container for document processing results."""
    success: bool
    text: Optional[str] = None
    metadata: Optional[Dict[Any, Any]] = None
    error: Optional[str] = None
    page_count: int = 0
    llm_response: Optional[str] = None
    metadata_only: bool = False

class DocumentProcessor:
    """Handles document processing and text extraction."""
    
    def __init__(self):
        """Initialize the document processor."""
        logger.debug("Initializing document processor")
        try:
            import litellm
            self.llm = litellm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            self.llm = None
        self.current_prompt = None
    
    def _extract_title(self, text: str) -> str:
        """Extract title from text, handling multi-line titles."""
        lines = text.split('\n')
        title_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that look like headers or metadata
            if any(line.lower().startswith(x) for x in ['doi:', 'http', 'abstract', 'introduction']):
                break
                
            # Skip lines that look like author information
            if any(x in line.lower() for x in ['university', '@', 'institute', 'department']):
                break
                
            # Stop if we hit author names (usually contains commas)
            if ',' in line and len(line.split(',')) > 1:
                break
                
            title_lines.append(line)
            
            # Stop if we have what looks like a complete title
            if len(title_lines) >= 1 and (
                line.endswith(('.', '?', '!')) or  # Ends with punctuation
                any(x in line.lower() for x in ['university', '@', 'institute', 'department'])  # Next line is authors
            ):
                break
                
            # Stop if we've collected too many lines
            if len(title_lines) >= 3:
                break
        
        return ' '.join(title_lines)
    
    def _extract_authors(self, text: str) -> str:
        """Extract author names from text."""
        lines = text.split('\n')
        author_lines = []
        found_authors = False
        
        for line in lines[1:]:  # Skip title line
            line = line.strip()
            if not line:
                if found_authors:  # Stop at empty line after authors
                    break
                continue
            
            # Skip lines that look like headers or metadata
            if any(line.lower().startswith(x) for x in ['doi:', 'http', 'abstract', 'introduction']):
                break
            
            # Look for author lines (contain commas and no special characters)
            if ',' in line and not any(x in line.lower() for x in ['@', 'http', 'doi', 'university', 'institute', 'department']):
                found_authors = True
                author_lines.append(line)
                continue
            
            # Stop if we hit non-author content
            if found_authors:
                break
        
        # Clean up author list
        if author_lines:
            # Join all authors and split by commas
            all_authors = ', '.join(author_lines).split(',')
            # Clean each author name and filter out affiliations
            authors = [
                name.strip() for name in all_authors 
                if name.strip() and not any(x in name.lower() for x in ['university', 'institute', 'department'])
            ]
            return ', '.join(authors)
        
        return ""
    
    def _process_pdf(self, file_path: Path) -> ProcessingResult:
        """Process a PDF file."""
        try:
            # Verify it's actually a PDF by trying to read it
            reader = PdfReader(str(file_path))
            
            # For title or author queries, just get first page text
            if self.current_prompt and ("title" in self.current_prompt.lower() or "author" in self.current_prompt.lower()):
                # Get first page text and limit to first few lines
                text = reader.pages[0].extract_text()
                
                # For title, extract complete title
                if "title" in self.current_prompt.lower():
                    text = self._extract_title(text)
                # For authors, extract author names
                elif "author" in self.current_prompt.lower():
                    text = self._extract_authors(text)
            else:
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            return ProcessingResult(
                success=True,
                text=text,
                metadata=reader.metadata,
                page_count=len(reader.pages)
            )
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return ProcessingResult(
                success=False,
                error=f"Not a valid PDF file: {str(e)}"
            )
    
    def _process_text(self, file_path: Path) -> ProcessingResult:
        """Process a text file."""
        try:
            text = file_path.read_text()
            stat = file_path.stat()
            
            return ProcessingResult(
                success=True,
                text=text,
                metadata={
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "created": stat.st_ctime
                },
                page_count=len(text.splitlines())  # Use line count as page count
            )
        except Exception as e:
            logger.error(f"Error processing text file: {str(e)}")
            return ProcessingResult(
                success=False,
                error=str(e)
            )
    
    def process_file(self, file_path: str | Path, prompt: Optional[str] = None, model: Optional[str] = None, enforce_pdf: bool = True) -> ProcessingResult:
        """
        Process a file and extract its contents, optionally analyzing with LLM.
        
        Args:
            file_path: Path to the file
            prompt: Optional prompt for analysis
            model: Optional model name
            enforce_pdf: If True, only accept PDF files (default: True)
            
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
            
            # Validate format
            validation = validate_format(file_path)
            if not validation.is_valid:
                return ProcessingResult(
                    success=False,
                    error=validation.error
                )
            
            # Check if PDF is required
            ext = file_path.suffix.lower()
            if enforce_pdf and ext != '.pdf':
                return ProcessingResult(
                    success=False,
                    error="Not a PDF file"
                )
            
            # Store prompt for optimization
            self.current_prompt = prompt
            
            # Process based on file type
            if ext == '.pdf':
                result = self._process_pdf(file_path)
            elif ext == '.txt':
                result = self._process_text(file_path)
            else:
                return ProcessingResult(
                    success=False,
                    error=f"Unsupported file type: {ext}"
                )
            
            if not result.success:
                return result
            
            # Process with LLM if prompt provided
            if prompt and self.llm:
                try:
                    # For summarization, focus on title, abstract, and conclusion
                    if "summarize" in prompt.lower():
                        text = result.text
                        # Extract title and abstract
                        lines = text.split('\n')
                        summary_text = []
                        in_abstract = False
                        in_conclusion = False
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            # Always include title
                            if len(summary_text) < 3:
                                summary_text.append(line)
                                continue
                                
                            # Look for abstract
                            if "abstract" in line.lower():
                                in_abstract = True
                                continue
                                
                            # Look for conclusion
                            if any(x in line.lower() for x in ["conclusion", "discussion"]):
                                in_conclusion = True
                                in_abstract = False
                                continue
                                
                            # Include abstract and conclusion text
                            if in_abstract or in_conclusion:
                                summary_text.append(line)
                                
                            # Stop after conclusion
                            if in_conclusion and len(summary_text) > 20:
                                break
                        
                        # Use focused text for summary
                        text = "\n".join(summary_text)
                    else:
                        text = result.text
                    
                    # Determine if we need exact value extraction
                    exact_value = any(x in prompt.lower() for x in ["date", "amount", "total", "number", "email", "phone", "address", "due"])
                    
                    kwargs = {
                        "model": model or "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": (
                                "You are a document analysis assistant. " +
                                ("You must extract ONLY the exact value with NO additional text, labels, or context. " +
                                 "For dates, return ONLY the date in YYYY.MM.DD format with no labels or text. " +
                                 "For amounts, return ONLY the amount with currency symbol (e.g. $93.50). " +
                                 "For emails, return ONLY the email address with no labels or text. " if exact_value else
                                 "Your responses must be EXACTLY one line long - no bullet points, no multiple sentences with periods. " +
                                 "Combine all information into a single flowing sentence using commas and semicolons where needed.")
                            )},
                            {"role": "user", "content": f"{prompt}\n\nDocument text:\n{text}\n\n" +
                                ("Return ONLY the exact value with NO additional text, labels, or context." if exact_value else
                                 "Remember: Respond with EXACTLY one line, no matter how complex the information is.")}
                        ]
                    }
                    
                    response = self.llm.completion(**kwargs)
                    result.llm_response = response.choices[0].message.content.strip()
                except Exception as e:
                    logger.error(f"Error in LLM processing: {str(e)}")
                    result.error = f"Document text extracted successfully, but analysis failed: {str(e)}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return ProcessingResult(
                success=False,
                error=str(e)
            )

# Alias for backward compatibility
PDFProcessor = DocumentProcessor