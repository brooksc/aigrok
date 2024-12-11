"""
Tests for PDF processing functionality.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from aigrok.pdf_processor import PDFProcessor, ProcessingResult

TEST_CASES = [
    {
        "name": "invoice_date",
        "prompt": "What is the invoice date? Please respond with just the date in YYYY.MM.DD format.",
        "expected": "2016.01.25",
        "error_margin": None  # Exact match required
    },
    {
        "name": "due_date",
        "prompt": "What is the due date? Please respond with just the date in YYYY.MM.DD format.",
        "expected": "2016.01.31",
        "error_margin": None  # Exact match required
    },
    {
        "name": "total_amount",
        "prompt": "What is the total amount due? Please respond with just the amount in format $XX.XX.",
        "expected": "$93.50",
        "error_margin": None  # Exact match required
    },
    {
        "name": "tax_amount",
        "prompt": "What is the tax amount? Please respond with just the amount in format $XX.XX.",
        "expected": "$8.50",
        "error_margin": None  # Exact match required
    },
    {
        "name": "email",
        "prompt": "What is the sender's email address? Please respond with just the email address.",
        "expected": "admin@slicedinvoices.com",
        "error_margin": None  # Exact match required
    }
]

def test_pdf_processor_initialization():
    """Test that PDF processor initializes correctly."""
    processor = PDFProcessor()
    assert isinstance(processor, PDFProcessor)

def test_prompt_responses():
    """Test specific prompts get expected responses."""
    processor = PDFProcessor()
    test_file = "tests/files/invoice.pdf"
    
    for test_case in TEST_CASES:
        result = processor.process_file(test_file, prompt=test_case["prompt"])
        
        assert result.success, f"Failed to process file for test: {test_case['name']}"
        assert result.llm_response is not None, f"No LLM response for test: {test_case['name']}"
        
        # Clean the response (remove extra whitespace, newlines, etc.)
        cleaned_response = result.llm_response.strip()
        
        # For exact match tests
        if test_case["error_margin"] is None:
            assert cleaned_response == test_case["expected"], (
                f"Test '{test_case['name']}' failed.\n"
                f"Expected: {test_case['expected']}\n"
                f"Got: {cleaned_response}"
            )

def test_invalid_file_path():
    """Test handling of non-existent file."""
    processor = PDFProcessor()
    result = processor.process_file("nonexistent.pdf")
    assert not result.success
    assert "File not found" in result.error

def test_invalid_file_type():
    """Test handling of non-PDF file."""
    processor = PDFProcessor()
    # Create a temporary text file
    test_file = Path("test.txt")
    test_file.write_text("This is not a PDF")
    
    result = processor.process_file(test_file)
    assert not result.success
    assert "Not a PDF file" in result.error
    
    # Cleanup
    test_file.unlink()