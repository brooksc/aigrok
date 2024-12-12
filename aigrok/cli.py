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
from .formats import validate_format, get_supported_formats

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

def format_output(result: ProcessingResult, format_type: str) -> str:
    """Format processing result based on output type."""
    if not result.success:
        return f"Error: {result.error}"
    
    if format_type == "json":
        try:
            # If LLM response is JSON, try to extract it from markdown code blocks
            if result.llm_response:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', result.llm_response, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(1))
                        return json.dumps(json_data, indent=2)
                    except json.JSONDecodeError:
                        pass
                
                # Try parsing the raw response as JSON
                try:
                    if isinstance(result.llm_response, (dict, list)):
                        return json.dumps(result.llm_response, indent=2)
                    json_data = json.loads(result.llm_response)
                    return json.dumps(json_data, indent=2)
                except (json.JSONDecodeError, TypeError):
                    pass
            
            # Special case for author list
            if "author" in result.text.lower():
                # Split authors and create JSON structure
                authors = []
                # Remove special characters and split by commas
                text = re.sub(r'[^\w\s,]', '', result.text)
                for author in text.split(','):
                    name_parts = [part for part in author.strip().split() if part.strip()]
                    if len(name_parts) >= 2:
                        # Handle special case for author names
                        if name_parts[0].lower() in ['university', 'institute', 'department']:
                            continue
                        authors.append({
                            "first_name": " ".join(name_parts[:-1]),
                            "last_name": name_parts[-1]
                        })
                return json.dumps(authors, indent=2)
            
            # Fallback to structured output
            return json.dumps({
                "text": result.text,
                "metadata": result.metadata,
                "page_count": result.page_count,
                "analysis": result.llm_response
            }, indent=2)
        except Exception as e:
            logger.error(f"Error formatting JSON output: {str(e)}")
            return json.dumps({
                "error": "Failed to format JSON output",
                "text": result.text,
                "metadata": result.metadata,
                "page_count": result.page_count,
                "analysis": result.llm_response
            }, indent=2)
    
    elif format_type == "csv":
        if result.llm_response and '\n' in result.llm_response:
            return result.llm_response  # Return CSV from LLM
        elif "author" in result.text.lower():
            # Special case for author list
            authors = []
            text = re.sub(r'[^\w\s,]', '', result.text)
            for author in text.split(','):
                name_parts = [part for part in author.strip().split() if part.strip()]
                if len(name_parts) >= 2:
                    if name_parts[0].lower() in ['university', 'institute', 'department']:
                        continue
                    authors.append({
                        "first_name": " ".join(name_parts[:-1]),
                        "last_name": name_parts[-1]
                    })
            # Format as CSV with newlines
            csv_lines = ["first_name,last_name"]
            for author in authors:
                csv_lines.append(f"{author['first_name']},{author['last_name']}")
            return "\n".join(csv_lines)
        else:
            # Basic CSV format
            return f"field,value\ntext,{result.text}\npage_count,{result.page_count}"
    
    elif format_type == "markdown":
        md = "# Document Analysis Results\n\n"
        if result.metadata:
            md += "## Metadata\n"
            for key, value in result.metadata.items():
                md += f"- {key}: {value}\n"
        md += f"\n## Page Count\n{result.page_count}\n"
        if result.text:
            md += f"\n## Extracted Text\n{result.text}\n"
        if result.llm_response:
            md += f"\n## Analysis\n{result.llm_response}\n"
        return md
    
    # Default to text format - ensure one line
    if result.llm_response:
        return result.llm_response.replace('\n', ' ').strip()
    return result.text.replace('\n', ' ').strip() if result.text else "No text content extracted"

def process_file(args) -> Optional[str]:
    """Process files based on command line arguments."""
    try:
        processor = PDFProcessor()
        outputs = []
        
        # Convert single file to list for consistent handling
        input_files = [args.input] if isinstance(args.input, str) else args.input
        
        for input_file in input_files:
            try:
                # Modify prompt to enforce one-line response
                prompt = args.prompt
                if prompt and "one line" not in prompt.lower():
                    prompt += " Respond with ONLY one line, no other text."
                
                # Process the file
                result = processor.process_file(
                    input_file,
                    prompt=prompt,
                    model=args.model,
                    enforce_pdf=True
                )
                
                # Format the output
                if result.success:
                    output = format_output(result, args.format)
                    # Only force one line for text format
                    if args.format == "text":
                        output = output.replace('\n', ' ').strip()
                else:
                    output = result.error
                    logger.error(f"Error processing {input_file}: {result.error}")
                
                if len(input_files) > 1:
                    # Add filename prefix for multiple files
                    outputs.append(f"{input_file}:{output}")
                else:
                    outputs.append(output)
                    
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error processing {input_file}: {error_msg}")
                return None
        
        # Join outputs with newlines
        return "\n".join(outputs) if outputs else None
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing files: {error_msg}")
        return None

def main():
    """Main entry point."""
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        # Setup logging
        setup_logger(args.verbose)
        
        # Process file
        output = process_file(args)
        if output:
            if args.output:
                Path(args.output).write_text(output)
                logger.info(f"Output written to {args.output}")
            else:
                try:
                    print(output)
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