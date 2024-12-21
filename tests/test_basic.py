"""Basic tests to verify test infrastructure."""
import pytest
import os

def test_environment_setup():
    """Test that environment variables are set correctly."""
    assert os.getenv("AIGROK_TEST_MODE") == "mock"
    assert os.getenv("AIGROK_MOCK_RESPONSES") == "true"
    assert os.getenv("OLLAMA_BASE_URL") == "http://localhost:11434"

def test_ocr_service(ocr_service):
    """Test OCR service mocking."""
    result = ocr_service.process_document("test.png")
    assert result["success"] is True
    assert "Mock OCR text" in result["text"]
    assert result["confidence"] > 0

def test_llm_service(llm_service):
    """Test LLM service mocking."""
    # Test generate
    gen_result = llm_service.generate("Test prompt")
    assert gen_result["done"] is True
    assert "mock LLM response" in gen_result["response"]
    
    # Test chat
    chat_result = llm_service.chat([{"role": "user", "content": "Hello"}])
    assert chat_result["done"] is True
    assert "mock chat response" in chat_result["message"]["content"]

def test_invalid_file_handling(ocr_service):
    """Test handling of invalid files."""
    result = ocr_service.process_document("invalid.txt")
    assert result["success"] is False
    assert "Invalid file format" in result["error"]
