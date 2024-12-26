#!/usr/bin/env python3
"""
Command-line interface for PDF processing.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Union, List
from loguru import logger
from .pdf_processor import PDFProcessor, ProcessingResult
from .formats import get_supported_formats
from .config import ConfigManager
from . import __version__
import glob
from .logging import configure_logging
from pprint import pformat


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""

    class ExitOnEmptyParser(argparse.ArgumentParser):
        def parse_args(self, args=None, namespace=None):
            if args is None:
                args = sys.argv[1:]
            if not args:
                self.print_help()
                sys.exit(1)
            return super().parse_args(args, namespace)

    parser = ExitOnEmptyParser(
        description="Process PDF files with AI assistance",
        usage="aigrok [options] PROMPT file ...",
        prog="aigrok",
    )

    # Version
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # Required arguments - but only if not configuring
    parser.add_argument(
        "prompt",
        nargs="?",  # Make prompt optional
        help="Processing prompt",
    )

    parser.add_argument(
        "files",
        nargs="*",  # Zero or more files
        help="Files to process",
    )

    # Optional arguments
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--configure", action="store_true", help="Configure the application"
    )

    # Add other arguments
    parser.add_argument("--model", type=str, help="Model to use for analysis")

    parser.add_argument(
        "--output", "-o", type=str, help="Path to save the output (defaults to stdout)"
    )

    # Format options
    parser.add_argument(
        "--type",
        help=f"Input file type. Supported types: {', '.join(t.strip('.') for t in get_supported_formats())}",
    )

    # Additional options
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Only extract and display document metadata",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--easyocr",
        action="store_true",
        help="Enable OCR processing of images in PDFs. This is useful for PDFs with scanned text or embedded images containing text. Example: --easyocr",
    )

    parser.add_argument(
        "--ocr-languages",
        default="en",
        help="Languages to use for OCR (comma-separated). Example: en,fr,de",
    )

    parser.add_argument(
        "--ocr-fallback",
        action="store_true",
        help="Continue processing if OCR fails (default: False)",
    )

    return parser


def format_output(results, format_type="text", show_filenames=True):
    """Format the processing results based on the specified format type."""
    if not isinstance(results, list):
        results = [results]

    if format_type == "text":
        output = []
        for result in results:
            if result and result.llm_response:  # Only output if we have a response
                line = ""
                if show_filenames and result.metadata.get("file_name"):
                    line += f"{result.metadata.get('file_name')}:"
                line += f"{result.llm_response}"
                if line:  # Only append non-empty lines
                    output.append(line)
        return "\n".join(output) if output else ""

    elif format_type == "json":
        return json.dumps(
            [
                {
                    "file_name": r.metadata.get("file_name", ""),
                    "text": r.text,
                    "llm_response": r.llm_response,
                    "success": r.success,
                    "metadata": r.metadata,
                }
                for r in results
            ],
            indent=2,
        )

    elif format_type == "markdown":
        output = []
        for result in results:
            filename = result.metadata.get("file_name", "")
            output.append(f"# {filename}")

            if result.text:
                output.append("## Extracted Text")
                output.append(result.text)

            if result.llm_response:
                output.append("## LLM Response")
                output.append(result.llm_response)

            output.append("")  # Add blank line between files

        return "\n".join(output)

    else:
        raise ValueError(f"Unsupported format type: {format_type}")


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
    try:
        processor = PDFProcessor()
        result = processor.process_file(file_path, prompt)
        result.filename = str(Path(file_path).name)  # Store just the filename
        return result
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {str(e)}")
        return ProcessingResult(
            success=False, error=str(e), filename=str(Path(file_path).name)
        )


def process_file(
    files: Union[str, Path, List[Union[str, Path]]], prompt: str
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


def process_files(args):
    """Process files based on the provided arguments."""
    config_manager = ConfigManager()

    # Initialize processor with verbose setting
    processor = PDFProcessor(config_manager=config_manager, verbose=args.verbose)

    # Expand glob patterns in file arguments
    files = []
    for pattern in args.files or []:
        matched_files = glob.glob(pattern)
        if not matched_files:
            print(f"Error: File not found: {pattern}")
            sys.exit(1)
        files.extend(matched_files)

    # Process files and format output
    results = []
    for file in files:
        logger.info(f"Processing file: {file}")

        if args.verbose:
            logger.debug(
                "Processing Configuration:\n%s",
                pformat(
                    {
                        "text_model": config_manager.config.text_model.model_dump(),
                        "vision_model": config_manager.config.vision_model.model_dump(),
                        "audio_model": config_manager.config.audio_model.model_dump()
                        if config_manager.config.audio_model
                        else None,
                        "ocr_enabled": config_manager.config.ocr_enabled,
                        "ocr_languages": config_manager.config.ocr_languages,
                        "format": args.format,
                    }
                ),
            )

        result = processor.process_file(file, args.prompt)

        if args.verbose:
            logger.debug(
                "File Processing Response:\n%s",
                pformat(
                    {
                        "success": result.success,
                        "text": result.text[:200] + "..."
                        if result.text
                        else None,  # Truncate long text
                        "llm_response": result.llm_response,
                        "metadata": result.metadata,
                        "error": result.error,
                    }
                ),
            )

        if result and result.llm_response:
            results.append(result)
            # Print each result immediately
            line = ""
            if result.metadata.get("file_name"):
                line += f"{result.metadata.get('file_name')}:"
            line += f"{result.llm_response}"
            print(line, flush=True)

    # Always pass the full list to format_output
    output = format_output(
        results,
        format_type=args.format,
        show_filenames=True,  # Always show filenames when processing multiple files
    )

    # Only write to output file if specified
    if args.output:
        Path(args.output).write_text(output)


def main():
    """Main entry point."""
    parser = create_parser()

    try:
        args = parser.parse_args()
    except SystemExit:
        # Re-raise SystemExit for --help and --version
        raise

    # Configure logging based on verbosity
    configure_logging(args.verbose)

    if args.verbose:
        logger.debug(f"Arguments: {args}")
        logger.debug(f"Verbose mode: {args.verbose}")

    # Handle configuration
    if args.configure:
        config_manager = ConfigManager()
        config_manager.configure()
        sys.exit(0)

    # Check for required arguments
    if not args.prompt and not args.files and not args.configure:
        parser.print_help()
        print("\nError: Must provide at least one file or a prompt")
        sys.exit(1)

    # Update configuration if OCR options are provided
    if args.easyocr:
        try:
            config_manager = ConfigManager()
            config_manager.config.ocr_enabled = True
            config_manager.config.ocr_languages = args.ocr_languages.split(",")
            config_manager.config.ocr_fallback = args.ocr_fallback
            config_manager.save_config()
            if args.verbose:
                logger.debug("Updated OCR configuration")
        except Exception as e:
            logger.error(f"Failed to update OCR configuration: {e}")
            sys.exit(1)

    # Process files
    try:
        if args.prompt and not args.files:
            print("Error: Must provide at least one file or a prompt")
            sys.exit(1)
        elif not args.prompt:
            print("Error: Must provide at least one file or a prompt")
            sys.exit(1)
        else:
            logger.info(f"Processing files with prompt: {args.prompt}")
            process_files(args)
            sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
