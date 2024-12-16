"""Tests for the PDF processor module."""
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
from PIL import Image
import numpy as np
from aigrok.pdf_processor import PDFProcessor, PDFProcessingResult
from aigrok.config import ConfigManager, AigrokConfig, ModelConfig

@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    return {
        'text_model': ModelConfig(provider='ollama', model_name='llama2', endpoint='http://localhost:11434'),
        'vision_model': ModelConfig(provider='ollama', model_name='llama2-vision', endpoint='http://localhost:11434'),
        'ocr_enabled': True,
        'ocr_languages': ['en'],
        'ocr_fallback': True
    }

@pytest.fixture
def processor(mock_config):
    """Create a PDFProcessor instance with mocked configuration."""
    config = AigrokConfig(**mock_config)
    config_manager = ConfigManager()
    config_manager.config = config
    return PDFProcessor(config_manager=config_manager)

@pytest.fixture
def sample_image():
    """Create a sample PIL Image."""
    image = Image.new('RGB', (100, 30), color='white')
    return image

def test_process_image_ocr_no_reader(processor, sample_image):
    """Test OCR processing with no reader."""
    processor.reader = None
    text, confidence = processor._process_image_ocr(sample_image)
    assert text == ""
    assert confidence == 0.0

@patch('easyocr.Reader')
def test_process_image_ocr_success(mock_reader, processor, sample_image):
    """Test successful OCR processing."""
    # Mock OCR results
    mock_results = [
        ([[0, 0], [100, 0], [100, 30], [0, 30]], "Sample text", 0.95)
    ]
    mock_reader_instance = Mock()
    mock_reader_instance.readtext.return_value = mock_results
    mock_reader.return_value = mock_reader_instance
    
    processor.reader = mock_reader_instance
    text, confidence = processor._process_image_ocr(sample_image)
    
    assert text == "Sample text"
    assert confidence == 0.95
    mock_reader_instance.readtext.assert_called_once()

@patch('easyocr.Reader')
def test_process_image_ocr_error(mock_reader, processor, sample_image):
    """Test OCR processing with error."""
    mock_reader_instance = Mock()
    mock_reader_instance.readtext.side_effect = Exception("OCR error")
    mock_reader.return_value = mock_reader_instance
    
    processor.ocr_reader = mock_reader_instance
    text, confidence = processor._process_image_ocr(sample_image)
    
    assert text == ""
    assert confidence == 0.0

def test_combine_text(processor):
    """Test text combination."""
    pdf_text = "PDF content"
    ocr_text = "OCR content"

    # Test with both texts
    combined = processor._combine_text(pdf_text, ocr_text)
    assert "Text extracted from PDF:\nPDF content" in combined
    assert "Text extracted via OCR:\nOCR content" in combined

    # Test with empty OCR text
    combined = processor._combine_text(pdf_text, "")
    assert combined == "Text extracted from PDF:\nPDF content"

    # Test with empty PDF text
    combined = processor._combine_text("", ocr_text)
    assert combined == "Text extracted via OCR:\nOCR content"

@patch('fitz.open')
@patch('easyocr.Reader')
@patch('ollama.Client')
def test_process_document_with_ocr(mock_ollama, mock_reader, mock_fitz_open, processor, sample_image):
    """Test document processing with OCR enabled."""
    # Mock PDF document
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "PDF content"
    mock_doc.__iter__.return_value = iter([mock_page])
    mock_doc.__len__.return_value = 1
    mock_fitz_open.return_value = mock_doc

    # Mock image extraction
    mock_image_list = [(1, 0, 100, 30, None, None, None)]  # xref is 1
    mock_page.get_images.return_value = mock_image_list
    mock_doc.extract_image.return_value = {"image": sample_image.tobytes()}

    # Mock OCR results
    mock_results = [([[0, 0], [100, 0], [100, 30], [0, 30]], "OCR content", 0.95)]
    mock_reader_instance = MagicMock()
    mock_reader_instance.readtext.return_value = mock_results
    mock_reader.return_value = mock_reader_instance
    processor.reader = mock_reader_instance

    # Mock Ollama
    mock_ollama_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.response = "LLM response"
    mock_ollama_instance.generate.return_value = mock_response
    mock_ollama.return_value = mock_ollama_instance
    processor.llm = mock_ollama_instance
    processor.text_provider = "ollama"
    processor.text_model = "llama2"

    # Process document
    with patch.object(processor, '_extract_images') as mock_extract_images:
        mock_extract_images.return_value = [(sample_image, 0)]
        result = processor.process_document("/path/to/doc.pdf", "test prompt")
        assert result.success
        assert "Text extracted from PDF:\nPDF content" in result.text
        assert "Text extracted via OCR:\n[Page 1] OCR content" in result.text
        assert result.llm_response == "LLM response"

@patch('fitz.open')
@patch('ollama.Client')
def test_process_document_ocr_disabled(mock_ollama, mock_fitz_open, processor):
    """Test document processing with OCR disabled."""
    # Disable OCR
    processor.reader = None

    # Mock PDF document
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "PDF content"
    mock_doc.__iter__.return_value = iter([mock_page])
    mock_fitz_open.return_value = mock_doc

    # Mock Ollama
    mock_ollama_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.response = "LLM response"
    mock_ollama_instance.generate.return_value = mock_response
    mock_ollama.return_value = mock_ollama_instance
    processor.llm = mock_ollama_instance

    # Process document
    result = processor.process_document("/path/to/doc.pdf", "test prompt")
    assert result.success
    assert "PDF content" in result.text
    assert result.llm_response == "LLM response"
