#!/usr/bin/env python3
"""
Command-line interface for PDF processing.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, Union, List
from loguru import logger
from .pdf_processor import PDFProcessor, ProcessingResult
from .formats import validate_format, get_supported_formats
from io import StringIO
import csv

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
    
    # Required arguments
    parser.add_argument(
        "prompt",
        type=str,
        help="Prompt for LLM analysis of the document"
    )
    
    parser.add_argument(
        "input",
        type=str,
        nargs='+',  # Accept one or more input files
        help="Path to one or more input files"
    )
    
    # Optional arguments
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use for analysis"
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
    
    parser.add_argument(
        "--type",
        help=f"Input file type. Supported types: {', '.join(t.strip('.') for t in get_supported_formats())}"
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

def format_output(result: ProcessingResult, format_type: str = "text") -> str:
    """Format processing result for output.
    
    Args:
        result: Processing result to format
        format_type: Output format (text, json, markdown)
    
    Returns:
        Formatted output string
    """
    if format_type == "text":
        return result.llm_response or result.text or ""
    
    if format_type == "json":
        return json.dumps({
            "success": result.success,
            "text": result.text,
            "metadata": result.metadata,
            "page_count": result.page_count,
            "llm_response": result.llm_response,
            "error": result.error
        }, indent=2)
    
    if format_type == "markdown":
        lines = [
            "# Document Analysis",
            f"Text: {result.text or 'N/A'}",
            f"Page Count: {result.page_count}",
            f"LLM Response: {result.llm_response or 'N/A'}"
        ]
        if result.metadata:
            lines.extend([
                "## Metadata",
                *[f"{k}: {v}" for k, v in result.metadata.items()]
            ])
        if result.error:
            lines.append(f"## Error\n{result.error}")
        return "\n".join(lines)
    
    raise ValueError(f"Unknown format type: {format_type}")

def process_single_file(file_path: Union[str, Path], prompt: str) -> ProcessingResult:
    """Process a single PDF file.
    
    Args:
        file_path: Path to PDF file
        prompt: Processing prompt
    
    Returns:
        Processing result
    
    Raises:
        Exception: If processing fails
    """
    processor = PDFProcessor()
    return processor.process_file(str(file_path), prompt)

def process_file(
    files: Union[str, Path, List[Union[str, Path]]],
    prompt: str
) -> Union[ProcessingResult, List[ProcessingResult]]:
    """Process one or more PDF files.
    
    Args:
        files: Path(s) to PDF file(s)
        prompt: Processing prompt
    
    Returns:
        Single result or list of results
    """
    if isinstance(files, (str, Path)):
        return process_single_file(files, prompt)
    
    return [process_single_file(f, prompt) for f in files]

def main():
    """Main entry point."""
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        # Setup logging
        setup_logger(args.verbose)
        
        # Process file
        output = process_file(args.input, args.prompt)
        if output.success:
            if args.output:
                Path(args.output).write_text(format_output(output, args.format))
                logger.info(f"Output written to {args.output}")
            else:
                try:
                    print(format_output(output, args.format))
                except BrokenPipeError:
                    # Python flushes standard streams on exit; redirect remaining output
                    # to devnull to avoid another BrokenPipeError at shutdown
                    import sys, os
                    devnull = os.open(os.devnull, os.O_WRONLY)
                    os.dup2(devnull, sys.stdout.fileno())
                    sys.exit(0)
        else:
            sys.exit(1)
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        import sys, os
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 