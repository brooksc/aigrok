"""
Test service implementations for both mock and e2e modes.
"""
from abc import ABC, abstractmethod
from typing import Optional
import pytest

class OCRService(ABC):
    """Base class for OCR services."""
    
    @abstractmethod
    def process_document(self, file_path: str) -> dict:
        """Process a document and return extracted text."""
        pass

class MockOCRService(OCRService):
    """Mock OCR service for testing."""
    
    def process_document(self, file_path: str) -> dict:
        """Return mock OCR results."""
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            return {
                "success": False,
                "text": "",
                "error": "Invalid file format. Only image and PDF files are supported."
            }
        
        return {
            "success": True,
            "text": "Mock OCR text for testing",
            "confidence": 0.95
        }

class RealOCRService(OCRService):
    """Real OCR service using EasyOCR."""
    
    def __init__(self):
        """Initialize OCR reader."""
        import easyocr
        self.reader = easyocr.Reader(['en'])
    
    def process_document(self, file_path: str) -> dict:
        """Process document with real OCR."""
        try:
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                return {
                    "success": False,
                    "text": "",
                    "error": "Invalid file format. Only image and PDF files are supported."
                }
            
            result = self.reader.readtext(file_path)
            if not result:
                return {
                    "success": False,
                    "text": "",
                    "error": "No text detected in image"
                }
            
            text = " ".join([r[1] for r in result])
            confidence = sum([r[2] for r in result]) / len(result)
            
            return {
                "success": True,
                "text": text,
                "confidence": confidence
            }
        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }

@pytest.fixture
def ocr_service(test_mode):
    """Get OCR service based on test mode."""
    if test_mode == "e2e":
        return RealOCRService()
    return MockOCRService()
