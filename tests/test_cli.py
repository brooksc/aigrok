"""Test cases for CLI functionality."""
from pathlib import Path
from aigrok.cli import format_output
from aigrok.types import ProcessingResult

def test_format_output_single_file():
    """Test that format_output doesn't add filename prefix for single file in text mode."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    # Format without filename (single file)
    output = format_output(result, format_type="text", show_filenames=False)
    assert "test.pdf:" not in output
    assert output == "Sample response"

def test_format_output_multiple_files():
    """Test that format_output adds filename prefix for multiple files in text mode."""
    results = [
        ProcessingResult(
            success=True,
            text="Sample text 1",
            llm_response="Sample response 1",
            metadata={"file_name": "test1.pdf"}
        ),
        ProcessingResult(
            success=True,
            text="Sample text 2",
            llm_response="Sample response 2",
            metadata={"file_name": "test2.pdf"}
        )
    ]
    
    # Format with filenames (multiple files)
    output = format_output(results, format_type="text", show_filenames=True)
    assert "test1.pdf: Sample response 1" in output
    assert "test2.pdf: Sample response 2" in output

def test_format_output_json():
    """Test that format_output includes filenames in JSON mode regardless of show_filenames."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    # Format as JSON (should always include filename)
    output = format_output(result, format_type="json", show_filenames=False)
    assert '"file_name": "test.pdf"' in output

def test_format_output_markdown():
    """Test that format_output includes filenames in Markdown mode regardless of show_filenames."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    # Format as Markdown (should always include filename)
    output = format_output(result, format_type="markdown", show_filenames=False)
    assert "# test.pdf" in output
