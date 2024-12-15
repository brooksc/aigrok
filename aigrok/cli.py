#!/usr/bin/env python3
"""
Command-line interface for PDF processing.
"""
import sys
import os
import argparse
import json
import re
from pathlib import Path
from typing import Optional, Union, List
from loguru import logger
from .pdf_processor import PDFProcessor, ProcessingResult
from .formats import validate_format, get_supported_formats
from .config import ConfigManager, AigrokConfig
import csv
import io
import logging

def setup_logger(verbose: bool = False):
    """Configure logging based on verbosity level."""
    logger.remove()  # Remove default handler
    if verbose:
        logger.add(sys.stderr, level="DEBUG")

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Process PDF documents with LLMs"
    )
    
    # Required arguments
    parser.add_argument(
        "files",
        nargs="*",
        help="PDF files to process"
    )
    
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Prompt to send to the LLM"
    )
    
    # Optional arguments
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Configure the application"
    )
    
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
    
    parser.add_argument(
        "--easyocr",
        action="store_true",
        help="Enable OCR processing of images in PDFs. This is useful for PDFs with scanned text or embedded images containing text. Example: --easyocr"
    )
    
    parser.add_argument(
        "--ocr-languages",
        type=str,
        default="en",
        help="Comma-separated list of language codes for OCR. Available languages depend on EasyOCR's language packs. Example: --ocr-languages 'en,fr,de' for English, French, and German"
    )
    
    parser.add_argument(
        "--ocr-fallback",
        action="store_true",
        help="Continue processing even if OCR fails. This ensures the document is processed using standard text extraction even if OCR encounters errors. Example: --ocr-fallback"
    )
    
    return parser

def format_output(result: Union[ProcessingResult, List[ProcessingResult]], format_type: str = "text") -> str:
    """Format processing result for output.
    
    Args:
        result: Processing result or list of results to format
        format_type: Output format (text, json, markdown)
    
    Returns:
        Formatted output string
    """
    if isinstance(result, list):
        if format_type == "text":
            return "\n\n".join(r.llm_response or r.text or "" for r in result)
        
        if format_type == "json":
            return json.dumps([{
                "success": r.success,
                "text": r.text,
                "metadata": r.metadata,
                "page_count": r.page_count,
                "llm_response": r.llm_response,
                "error": r.error
            } for r in result], indent=2)
        
        if format_type == "markdown":
            all_lines = []
            for i, r in enumerate(result, 1):
                lines = [
                    f"# Document {i} Analysis",
                    f"Text: {r.text or 'N/A'}",
                    f"Page Count: {r.page_count}",
                    f"LLM Response: {r.llm_response or 'N/A'}"
                ]
                if r.metadata:
                    lines.extend([
                        "## Metadata",
                        *[f"{k}: {v}" for k, v in r.metadata.items()]
                    ])
                if r.error:
                    lines.append(f"## Error\n{r.error}")
                all_lines.extend(lines)
                all_lines.append("\n---\n")  # Separator between documents
            return "\n".join(all_lines)
    else:
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
    """Main entry point for the CLI."""
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        if args.verbose:
            logger.debug(f"Arguments: {args}")
            logger.debug(f"Verbose mode: {args.verbose}")

        config_manager = ConfigManager()
        
        # Handle configuration
        if args.configure:
            config_manager.configure()
            return
            
        # Update configuration if OCR options are provided
        if args.easyocr:
            if not config_manager.config:
                print("Error: PDF processor not properly initialized. Please run with --configure first.")
                return
            config_manager.config.ocr_enabled = True
            if args.ocr_languages:
                config_manager.config.ocr_languages = args.ocr_languages.split(',')
            config_manager.config.ocr_fallback = args.ocr_fallback
            config_manager.save_config()
        
        # Process files
        logger.debug(f"Processing files: {args.files}")
        
        # First argument is actually the prompt if no -p/--prompt was specified
        prompt = args.prompt if args.prompt else args.files[0]
        files = args.files[1:] if not args.prompt else args.files
        
        if not args.configure and not files:
            print("Error: No input files specified")
            return
        
        results = process_file(files, prompt)
        
        for result in results:
            if result.success:
                if args.format == "json":
                    print(result.model_dump_json(indent=2))
                elif args.format == "markdown":
                    print(f"# Processing Results\n")
                    print(f"## Document\n")
                    print(f"- File: {result.metadata.get('file_name', 'unknown')}")
                    print(f"- Pages: {result.page_count}\n")
                    if result.ocr_text:
                        print(f"## OCR Results\n")
                        print(f"- Confidence: {result.ocr_confidence:.2%}\n")
                        print("### Extracted Text\n")
                        print(f"```\n{result.ocr_text}\n```\n")
                    print(f"## LLM Response\n")
                    print(result.llm_response)
                else:
                    if args.verbose:
                        print(f"File: {result.metadata.get('file_name', 'unknown')}")
                        print(f"Pages: {result.page_count}")
                        if result.ocr_text:
                            print(f"\nOCR Results (Confidence: {result.ocr_confidence:.2%}):")
                            print(result.ocr_text)
                        print("\nLLM Response:")
                    print(result.llm_response)
            else:
                print(f"Error: {result.error}")
                
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_logger(verbose=False)
    main()