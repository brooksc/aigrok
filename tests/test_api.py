"""
Tests for API functionality.
"""
import pytest
import warnings
from pathlib import Path
from unittest.mock import Mock, patch
from aigrok.api import APIClient, APIProcessor, ProcessRequest, ProcessResponse
from aigrok.pdf_processor import ProcessingResult

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

def test_process_request_validation():
    """Test ProcessRequest validation."""
    # Test valid request
    request = ProcessRequest(file_path="test.pdf")
    assert request.file_path == "test.pdf"
    assert request.prompt is None
    
    # Test with prompt
    request = ProcessRequest(file_path="test.pdf", prompt="Analyze this")
    assert request.file_path == "test.pdf"
    assert request.prompt == "Analyze this"
    
    # Test invalid request (missing file_path)
    with pytest.raises(ValueError):
        ProcessRequest()

def test_process_response_validation():
    """Test ProcessResponse validation."""
    # Test successful response
    response = ProcessResponse(
        success=True,
        text="Sample text",
        page_count=1
    )
    assert response.success
    assert response.text == "Sample text"
    assert response.page_count == 1
    assert response.error is None
    
    # Test error response
    response = ProcessResponse(
        success=False,
        error="File not found"
    )
    assert not response.success
    assert response.error == "File not found"
    assert response.text is None

def test_api_processor():
    """Test APIProcessor functionality."""
    processor = APIProcessor()
    test_file = "tests/files/invoice.pdf"
    
    # Test basic processing
    request = ProcessRequest(file_path=test_file)
    response = processor.process_pdf(request)
    assert response.success
    assert response.text is not None
    assert response.page_count == 1
    
    # Test with prompts
    for test_case in TEST_CASES:
        request = ProcessRequest(
            file_path=test_file,
            prompt=test_case["prompt"]
        )
        response = processor.process_pdf(request)
        
        assert response.success, f"Failed to process file for test: {test_case['name']}"
        assert response.llm_response is not None, f"No LLM response for test: {test_case['name']}"
        
        # Clean the response
        cleaned_response = response.llm_response.strip()
        
        # Check exact match
        if test_case["error_margin"] is None:
            assert cleaned_response == test_case["expected"], (
                f"Test '{test_case['name']}' failed.\n"
                f"Expected: {test_case['expected']}\n"
                f"Got: {cleaned_response}"
            )

def test_api_client():
    """Test APIClient functionality."""
    client = APIClient()
    test_file = "tests/files/invoice.pdf"
    
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "text": "Sample text",
        "page_count": 1,
        "llm_response": "2016.01.25"
    }
    
    with patch('requests.post', return_value=mock_response):
        # Test basic processing
        response = client.process_pdf(test_file)
        assert response.success
        assert response.text == "Sample text"
        assert response.page_count == 1
        
        # Test with prompt
        response = client.process_pdf(
            test_file,
            prompt="What is the invoice date?"
        )
        assert response.success
        assert response.llm_response == "2016.01.25"
    
    # Test error handling
    with patch('requests.post', side_effect=Exception("Connection error")):
        response = client.process_pdf(test_file)
        assert not response.success
        assert "Connection error" in response.error

def test_invalid_file_path():
    """Test handling of non-existent file."""
    processor = APIProcessor()
    request = ProcessRequest(file_path="nonexistent.pdf")
    response = processor.process_pdf(request)
    assert not response.success
    assert "File not found" in response.error

def test_invalid_file_type():
    """Test handling of non-PDF file."""
    processor = APIProcessor()
    
    # Create a temporary text file
    test_file = Path("test.txt")
    test_file.write_text("This is not a PDF")
    
    request = ProcessRequest(file_path=str(test_file))
    response = processor.process_pdf(request)
    assert not response.success
    assert "Not a PDF file" in response.error
    
    # Cleanup
    test_file.unlink() 