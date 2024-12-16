"""Tests for the API module."""
import pytest
from unittest.mock import Mock, patch
import json
from aigrok.api import (
    APIProcessor,
    ProcessRequest,
    ProcessResponse,
    OutputSchema,
    APIClient
)
from aigrok.pdf_processor import ProcessingResult
from aigrok.config import ConfigManager
from pydantic import BaseModel

class ModelConfig(BaseModel):
    text_model: str
    vision_model: str

class OCRConfig(BaseModel):
    enabled: bool = False
    languages: list[str] = ["en"]
    fallback: bool = True

class AigrokConfig(BaseModel):
    model_config: ModelConfig
    ocr_config: OCRConfig

    @property
    def ocr_enabled(self) -> bool:
        return self.ocr_config.enabled

    @property
    def ocr_languages(self) -> list[str]:
        return self.ocr_config.languages

    @property
    def ocr_fallback(self) -> bool:
        return self.ocr_config.fallback

    @property
    def text_model(self) -> str:
        return self.model_config.text_model

    @property
    def vision_model(self) -> str:
        return self.model_config.vision_model

@pytest.fixture
def sample_pdf_path():
    """Get path to sample PDF file."""
    return str(Path(__file__).parent / "files" / "invoice.pdf")

@pytest.fixture
def mock_processor():
    """Create a mock PDFProcessor."""
    with patch('aigrok.api.PDFProcessor') as mock:
        processor = APIProcessor()
        # Replace the real PDFProcessor with our mock
        processor.pdf_processor = mock.return_value
        yield processor

@pytest.fixture
def mock_requests():
    """Create a mock for requests."""
    with patch('aigrok.api.requests') as mock:
        yield mock

@pytest.fixture
def mock_api_processor(mocker):
    """Create a mock API processor for testing."""
    processor = APIProcessor()
    # Mock the process_file method
    mocker.patch.object(processor.pdf_processor, 'process_file')
    return processor

def test_process_request_validation():
    """Test ProcessRequest validation."""
    # Valid request
    request = ProcessRequest(file_path="test.pdf")
    assert request.file_path == "test.pdf"
    assert request.prompt is None
    assert request.output_schema is None

    # Valid request with prompt
    request = ProcessRequest(file_path="test.pdf", prompt="Analyze this")
    assert request.prompt == "Analyze this"

    # Invalid request (missing file_path)
    with pytest.raises(ValueError):
        ProcessRequest()

def test_output_schema_validation():
    """Test OutputSchema validation."""
    # Valid JSON schema
    schema = OutputSchema(
        format="json",
        schema_def='{"title": "str", "amount": "float"}'
    )
    assert schema.format == "json"

    # Valid CSV schema
    schema = OutputSchema(
        format="csv",
        schema_def=["title", "amount"]
    )
    assert schema.format == "csv"

    # Invalid format
    with pytest.raises(ValueError):
        OutputSchema(format="invalid", schema_def=[])

def test_process_response_validation():
    """Test ProcessResponse validation."""
    # Success response
    response = ProcessResponse(
        success=True,
        text="Sample text",
        page_count=1
    )
    assert response.success
    assert response.text == "Sample text"
    assert response.error is None

    # Error response
    response = ProcessResponse(
        success=False,
        error="Failed to process"
    )
    assert not response.success
    assert response.error == "Failed to process"

def test_api_processor_basic(mock_api_processor):
    """Test basic API processor functionality."""
    request = ProcessRequest(file_path="test.pdf")
    mock_api_processor.pdf_processor.process_file.return_value = ProcessingResult(
        success=True,
        text="Sample text",
        metadata={"pages": 1},
        page_count=1,
        llm_response="Analysis result"  # Preserving LLM response testing
    )
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert response.text == "Sample text"
    assert response.page_count == 1
    assert response.metadata == {"pages": 1}
    assert response.llm_response == "Analysis result"  # Testing LLM response

def test_api_processor_json_output(mock_api_processor):
    """Test JSON output from API processor."""
    schema = OutputSchema(
        format="json",
        schema_def='{"title": "string", "amount": "number"}'
    )
    request = ProcessRequest(file_path="test.pdf", output_schema=schema)
    
    # Mock first call for text extraction
    mock_api_processor.pdf_processor.process_file.side_effect = [
        ProcessingResult(success=True, text="Sample text"),
        ProcessingResult(success=True, llm_response='{"title": "Invoice", "amount": 100.0}')
    ]
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert response.structured_output == '{"title": "Invoice", "amount": 100.0}'
    
    # Additional validation of JSON structure (preserved from original)
    output = json.loads(response.structured_output)
    assert "title" in output
    assert "amount" in output

def test_api_processor_csv_output(mock_api_processor):
    """Test CSV output from API processor."""
    schema = OutputSchema(
        format="csv",
        schema_def=["title", "amount"]
    )
    request = ProcessRequest(file_path="test.pdf", output_schema=schema)
    
    # Mock first call for text extraction
    mock_api_processor.pdf_processor.process_file.side_effect = [
        ProcessingResult(success=True, text="Sample text"),
        ProcessingResult(success=True, llm_response="Invoice,100.0")
    ]
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert response.structured_output == "Invoice,100.0"

def test_api_processor_error_handling(mock_api_processor):
    """Test error handling in API processor."""
    request = ProcessRequest(file_path="test.pdf")
    mock_api_processor.pdf_processor.process_file.side_effect = Exception("Test error")
    
    response = mock_api_processor.process_pdf(request)
    assert not response.success
    assert response.error == "Test error"

def test_invalid_structured_output(mock_api_processor):
    """Test handling of invalid structured output."""
    schema = OutputSchema(
        format="json",
        schema_def='{"title": "string", "amount": "number"}'
    )
    request = ProcessRequest(file_path="test.pdf", output_schema=schema)
    
    # Mock responses with invalid JSON
    mock_api_processor.pdf_processor.process_file.side_effect = [
        ProcessingResult(success=True, text="Sample text"),
        ProcessingResult(success=True, llm_response='Invalid JSON')
    ]
    
    response = mock_api_processor.process_pdf(request)
    assert response.success  # Overall process succeeded
    assert response.error == "Failed to generate valid structured output"

def test_api_processor_ocr_not_initialized(mock_api_processor):
    """Test OCR initialization error handling."""
    request = ProcessRequest(file_path="test.pdf")
    mock_api_processor.pdf_processor.process_file.side_effect = Exception("OCR not initialized")
    
    response = mock_api_processor.process_pdf(request)
    assert not response.success
    assert "OCR not initialized" in response.error

def test_api_processor_ocr_success(mock_api_processor):
    """Test successful OCR processing."""
    request = ProcessRequest(file_path="test.pdf")
    mock_api_processor.pdf_processor.process_file.return_value = ProcessingResult(
        success=True,
        text="OCR extracted text",
        metadata={"ocr_confidence": 0.95},
        page_count=1
    )
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert response.text == "OCR extracted text"
    assert response.metadata["ocr_confidence"] > 0

def test_api_processor_ocr_error(mock_api_processor):
    """Test OCR error handling."""
    request = ProcessRequest(file_path="test.pdf")
    mock_api_processor.pdf_processor.process_file.side_effect = Exception("Invalid image data")
    
    response = mock_api_processor.process_pdf(request)
    assert not response.success
    assert "Invalid image data" in response.error

def test_api_processor_text_combination(mock_api_processor):
    """Test combining text from multiple sources."""
    request = ProcessRequest(file_path="test.pdf")
    mock_api_processor.pdf_processor.process_file.return_value = ProcessingResult(
        success=True,
        text="PDF text\nOCR text",
        metadata={"sources": ["pdf", "ocr"]},
        page_count=1
    )
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert "PDF text" in response.text
    assert "OCR text" in response.text
    assert "sources" in response.metadata

def test_api_processor_no_ocr(mock_api_processor):
    """Test processing without OCR."""
    request = ProcessRequest(file_path="test.pdf")
    mock_api_processor.pdf_processor.process_file.return_value = ProcessingResult(
        success=True,
        text="PDF text only",
        metadata={"sources": ["pdf"]},
        page_count=1
    )
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert response.text == "PDF text only"
    assert response.metadata["sources"] == ["pdf"]

def test_api_processor_large_file(mock_api_processor):
    """Test processing large files."""
    request = ProcessRequest(file_path="large.pdf")
    # Simulate a large file with many pages
    mock_api_processor.pdf_processor.process_file.return_value = ProcessingResult(
        success=True,
        text="Large file content",
        metadata={"file_size_mb": 50, "processing_time_ms": 5000},
        page_count=100
    )
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert response.page_count == 100
    assert response.metadata["file_size_mb"] == 50
    assert response.metadata["processing_time_ms"] <= 10000  # Max processing time

def test_api_processor_markdown_output(mock_api_processor):
    """Test markdown output format."""
    schema = OutputSchema(
        format="markdown",
        schema_def=["# Title", "## Section", "Content"]
    )
    request = ProcessRequest(file_path="test.pdf", output_schema=schema)
    
    mock_api_processor.pdf_processor.process_file.side_effect = [
        ProcessingResult(success=True, text="Sample text"),
        ProcessingResult(success=True, llm_response="# Document Title\n## Summary\nContent here")
    ]
    
    response = mock_api_processor.process_pdf(request)
    assert response.success
    assert "# Document Title" in response.structured_output
    assert "## Summary" in response.structured_output

def test_api_processor_multiple_files(mock_api_processor):
    """Test processing multiple files."""
    requests = [
        ProcessRequest(file_path="file1.pdf"),
        ProcessRequest(file_path="file2.pdf")
    ]
    
    mock_api_processor.pdf_processor.process_file.side_effect = [
        ProcessingResult(success=True, text="Content 1", page_count=1),
        ProcessingResult(success=True, text="Content 2", page_count=1)
    ]
    
    responses = [mock_api_processor.process_pdf(req) for req in requests]
    assert all(r.success for r in responses)
    assert responses[0].text == "Content 1"
    assert responses[1].text == "Content 2"

def test_api_client_initialization():
    """Test API client initialization."""
    client = APIClient()
    assert client.base_url == "http://localhost:8000"
    
    client = APIClient("http://example.com/")
    assert client.base_url == "http://example.com"

def test_api_client_process_success(mocker):
    """Test successful API client request processing."""
    # Create mock before the test
    requests_mock = mocker.patch('requests.post')
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "success": True,
        "text": "Sample text",
        "page_count": 1,
        "metadata": {"pages": 1}
    }
    mock_response.raise_for_status = mocker.Mock()
    requests_mock.return_value = mock_response
    
    client = APIClient()
    request = ProcessRequest(file_path="test.pdf", prompt="Analyze this")
    response = client.process(request)
    
    assert response.success
    assert response.text == "Sample text"
    assert response.page_count == 1
    assert response.metadata == {"pages": 1}
    
    # Verify request was made correctly
    requests_mock.assert_called_once()
    call_args = requests_mock.call_args
    assert call_args[0][0] == "http://localhost:8000/process"

def test_api_client_structured_output(mocker):
    """Test API client with structured output."""
    # Create mock before the test
    requests_mock = mocker.patch('requests.post')
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "success": True,
        "structured_output": '{"title": "Invoice", "amount": 100.0}',
        "text": "Sample text"
    }
    mock_response.raise_for_status = mocker.Mock()
    requests_mock.return_value = mock_response
    
    client = APIClient()
    schema = OutputSchema(
        format="json",
        schema_def='{"title": "string", "amount": "number"}'
    )
    request = ProcessRequest(file_path="test.pdf", output_schema=schema)
    response = client.process(request)
    
    assert response.success
    assert response.structured_output == '{"title": "Invoice", "amount": 100.0}'
    assert response.text == "Sample text"
    
    # Verify schema was included in request
    requests_mock.assert_called_once()
    call_args = requests_mock.call_args
    request_data = call_args[1]['json']
    assert "output_schema" in request_data
    assert request_data["output_schema"]["format"] == "json"
    assert request_data["output_schema"]["schema_def"] == '{"title": "string", "amount": "number"}'

def test_api_client_process_error(mocker):
    """Test API client error handling."""
    mocker.patch('requests.post', side_effect=Exception("Connection error"))
    
    client = APIClient()
    request = ProcessRequest(file_path="test.pdf")
    response = client.process(request)
    
    assert not response.success
    assert "Connection error" in response.error
