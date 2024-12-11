#!/usr/bin/env python3
"""
Command-line interface for PDF processing.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from .pdf_processor import PDFProcessor, ProcessingResult

def setup_logger(verbose: bool = False):
    """Configure logging based on verbosity level."""
    logger.remove()  # Remove default handler
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=log_level)

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Process and analyze documents using aigrok.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Input file/directory arguments
    parser.add_argument(
        "input",
        type=str,
        help="Path to the input PDF file"
    )
    
    # Processing options
    parser.add_argument(
        "--prompt",
        type=str,
        help="Prompt for LLM analysis of the document"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        help="Ollama model to use for analysis"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Path to save the output (defaults to stdout)"
    )
    
    # Format options
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    
    # Additional options
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Only extract and display document metadata"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser

def format_metadata(metadata) -> str:
    """Format metadata as markdown list."""
    if not metadata:
        return "- No metadata available"
    return "\n".join(f"- {k}: {v}" for k, v in metadata.items() if v)

def clean_llm_response(response: str, format_type: str) -> str:
    """Clean LLM response based on format type."""
    if format_type == "json":
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
        return response
    elif format_type == "csv":
        # Extract CSV from markdown code blocks if present
        csv_match = re.search(r'```(?:csv)?\s*(.*?)\s*```', response, re.DOTALL)
        if csv_match:
            return csv_match.group(1).strip()
        return response
    return response

def format_output(result: ProcessingResult, format_type: str = "text") -> str:
    """Format the processing result based on the specified format."""
    if not result.success:
        return f"Error: {result.error}"
    
    if format_type == "json":
        if result.llm_response:
            # Clean and validate JSON response
            cleaned_response = clean_llm_response(result.llm_response, format_type)
            try:
                # Verify it's valid JSON by parsing and re-serializing
                return json.dumps(json.loads(cleaned_response), indent=2)
            except:
                pass
        
        # Fallback to wrapping all data in JSON
        return json.dumps({
            "success": result.success,
            "text": result.text,
            "metadata": result.metadata,
            "page_count": result.page_count,
            "llm_response": result.llm_response
        }, indent=2)
    
    elif format_type == "csv":
        if result.llm_response:
            # Clean CSV response
            return clean_llm_response(result.llm_response, format_type)
        # Fallback to basic CSV with metadata
        rows = ["key,value"]
        if result.metadata:
            rows.extend(f"{k},{v}" for k, v in result.metadata.items() if v)
        return "\n".join(rows)
    
    elif format_type == "markdown":
        return f"""# Document Analysis Results

## Metadata
- Pages: {result.page_count}
{format_metadata(result.metadata) if result.metadata else '- No metadata available'}

## Extracted Text
{result.text if result.text else 'No text extracted'}

## LLM Analysis
{result.llm_response if result.llm_response else 'No analysis performed'}
"""
    else:  # text format
        if result.llm_response:
            return clean_llm_response(result.llm_response, "text")
        return result.text if result.text else ""

def process_file(args) -> Optional[str]:
    """Process a single file based on command line arguments."""
    try:
        processor = PDFProcessor()
        result = processor.process_file(
            args.input,
            prompt=args.prompt,
            model=args.model
        )
        
        if args.metadata_only:
            result.text = None
        
        return format_output(result, args.format)
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return None

def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging
    setup_logger(args.verbose)
    
    # Process input
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)
    
    output = process_file(args)
    
    if output is None:
        sys.exit(1)
    
    # Handle output
    if args.output:
        Path(args.output).write_text(output)
        logger.info(f"Output written to: {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main() 