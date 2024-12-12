"""
API module for PDF processing functionality.
"""
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from loguru import logger
import json
import csv
from io import StringIO
import requests

from .pdf_processor import PDFProcessor, ProcessingResult

class OutputSchema(BaseModel):
    """Schema for structured output."""
    model_config = ConfigDict(strict=True)
    format: Literal["json", "csv"] = Field(..., description="Output format (json or csv)")
    schema_def: Union[str, List[str]] = Field(..., description="JSON schema example or CSV column names")

class ProcessRequest(BaseModel):
    """Request model for PDF processing."""
    model_config = ConfigDict(strict=True)
    file_path: str = Field(..., description="Path to the PDF file to process")
    prompt: Optional[str] = Field(None, description="Optional prompt for LLM analysis")
    output_schema: Optional[OutputSchema] = Field(None, description="Schema for structured output")

class ProcessResponse(BaseModel):
    """Response model for PDF processing."""
    model_config = ConfigDict(strict=True)
    success: bool = Field(..., description="Whether the processing was successful")
    text: Optional[str] = Field(None, description="Extracted text from the PDF")
    metadata: Optional[Dict[str, Any]] = Field(None, description="PDF metadata")
    error: Optional[str] = Field(None, description="Error message if processing failed")
    page_count: int = Field(0, description="Number of pages in the PDF")
    llm_response: Optional[str] = Field(None, description="Raw LLM analysis response if prompt was provided")
    structured_output: Optional[str] = Field(None, description="Structured output in JSON or CSV format")

class APIProcessor:
    """Server-side API processor."""
    
    def __init__(self):
        """Initialize the API processor."""
        self.pdf_processor = PDFProcessor()
    
    def _generate_format_prompt(self, format_type: str, schema: Union[str, List[str]]) -> str:
        """Generate a prompt for formatted output."""
        if format_type == "json":
            return f"""Analyze the document and extract information in the following JSON format.
            Use this example as a template for the structure (field names must match exactly):
            {schema}
            
            Respond ONLY with the JSON data, no other text."""
        else:  # csv
            columns = ", ".join(schema if isinstance(schema, list) else schema.split(","))
            return f"""Analyze the document and extract information in CSV format with these columns:
            {columns}
            
            Respond ONLY with the CSV data (no headers), with values separated by commas."""
    
    def _validate_structured_output(self, output: str, schema: OutputSchema) -> bool:
        """Validate the structured output against the schema."""
        try:
            if schema.format == "json":
                # Validate JSON structure
                example = json.loads(schema.schema_def if isinstance(schema.schema_def, str) else json.dumps(schema.schema_def))
                result = json.loads(output)
                # Check if all keys in example exist in result
                return all(key in result for key in example.keys())
            else:  # csv
                # Validate CSV structure
                expected_columns = len(schema.schema_def if isinstance(schema.schema_def, list) else schema.schema_def.split(","))
                reader = csv.reader(StringIO(output))
                row = next(reader)
                return len(row) == expected_columns
        except Exception:
            return False
    
    def process_pdf(self, request: ProcessRequest) -> ProcessResponse:
        """
        Process a PDF file based on the API request.
        
        Args:
            request: ProcessRequest containing file path and optional prompt
            
        Returns:
            ProcessResponse containing the processing results
        """
        try:
            # First, extract text from PDF
            result = self.pdf_processor.process_file(request.file_path, enforce_pdf=True)
            if not result.success:
                return ProcessResponse(
                    success=False,
                    error=result.error
                )
            
            response = ProcessResponse(
                success=True,
                text=result.text,
                metadata=result.metadata,
                page_count=result.page_count
            )
            
            # Handle structured output if schema provided
            if request.output_schema:
                format_prompt = self._generate_format_prompt(
                    request.output_schema.format,
                    request.output_schema.schema_def
                )
                
                # Get structured output from LLM
                format_result = self.pdf_processor.process_file(
                    request.file_path,
                    prompt=format_prompt,
                    enforce_pdf=True
                )
                
                if format_result.success and format_result.llm_response:
                    structured_output = format_result.llm_response.strip()
                    # Validate the output
                    if self._validate_structured_output(structured_output, request.output_schema):
                        response.structured_output = structured_output
                    else:
                        response.error = "Failed to generate valid structured output"
            
            # Handle additional prompt if provided
            if request.prompt:
                prompt_result = self.pdf_processor.process_file(
                    request.file_path,
                    prompt=request.prompt,
                    enforce_pdf=True
                )
                if prompt_result.success:
                    response.llm_response = prompt_result.llm_response
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing PDF through API: {str(e)}")
            return ProcessResponse(
                success=False,
                error=str(e)
            )

class APIClient:
    """Client for interacting with the PDF processing API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client."""
        self.base_url = base_url.rstrip('/')
        
    def process_pdf(
        self,
        file_path: Union[str, Path],
        prompt: Optional[str] = None,
        output_format: Optional[str] = None,
        output_schema: Optional[Union[str, List[str]]] = None
    ) -> ProcessResponse:
        """
        Process a PDF file through the API.
        
        Args:
            file_path: Path to the PDF file
            prompt: Optional prompt for LLM analysis
            output_format: Optional output format ("json" or "csv")
            output_schema: Optional schema for structured output
            
        Returns:
            ProcessResponse containing the processing results
        """
        try:
            request_data = {"file_path": str(file_path), "prompt": prompt}
            
            if output_format and output_schema:
                request_data["output_schema"] = {
                    "format": output_format,
                    "schema": output_schema
                }
            
            request = ProcessRequest(**request_data)
            response = requests.post(
                f"{self.base_url}/process",
                json=request.model_dump()
            )
            response.raise_for_status()
            return ProcessResponse(**response.json())
        except Exception as e:
            return ProcessResponse(
                success=False,
                error=str(e)
            ) 