"""
Test OCR functionality in both mock and e2e modes.
"""

import pytest
import os
from .services import MockOCRService, RealOCRService


def test_mock_ocr_valid_image(test_files):
    """Test mock OCR with valid image."""
    service = MockOCRService()
    result = service.process_document(str(test_files["image"]))
    assert result["success"]
    assert isinstance(result["text"], str)
    assert result["confidence"] > 0


def test_mock_ocr_empty_image(test_files):
    """Test mock OCR with empty image."""
    service = MockOCRService()
    result = service.process_document(str(test_files["empty"]))
    assert result["success"]
    assert isinstance(result["text"], str)


def test_mock_ocr_invalid_file(test_files):
    """Test mock OCR with invalid file."""
    service = MockOCRService()
    result = service.process_document(str(test_files["invalid"]))
    assert not result["success"]
    assert "Invalid file format" in result["error"]


@pytest.mark.skipif(os.getenv("TEST_MODE") != "e2e", reason="Only run in e2e mode")
def test_real_ocr_valid_image(test_files):
    """Test real OCR with valid image."""
    service = RealOCRService()
    result = service.process_document(str(test_files["image"]))
    assert result["success"]
    assert "Hello World" in result["text"]
    assert result["confidence"] > 0


@pytest.mark.skipif(os.getenv("TEST_MODE") != "e2e", reason="Only run in e2e mode")
def test_real_ocr_empty_image(test_files):
    """Test real OCR with empty image."""
    service = RealOCRService()
    result = service.process_document(str(test_files["empty"]))
    assert not result["success"]
    assert "No text detected" in result["error"]


@pytest.mark.skipif(os.getenv("TEST_MODE") != "e2e", reason="Only run in e2e mode")
def test_real_ocr_invalid_file(test_files):
    """Test real OCR with invalid file."""
    service = RealOCRService()
    result = service.process_document(str(test_files["invalid"]))
    assert not result["success"]
    assert "Invalid file format" in result["error"]
