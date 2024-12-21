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
            
            results = self.reader.readtext(file_path)
            text = " ".join([result[1] for result in results])
            confidence = sum([result[2] for result in results]) / len(results) if results else 0
            
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

class LLMService(ABC):
    """Base class for LLM services."""
    
    @abstractmethod
    def generate(self, prompt: str) -> dict:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def chat(self, messages: list) -> dict:
        """Chat completion."""
        pass

class MockLLMService(LLMService):
    """Mock LLM service for testing."""
    
    def generate(self, prompt: str) -> dict:
        """Return mock generation results."""
        return {
            "model": "llama2",
            "created_at": "2024-12-15T22:10:00.000Z",
            "response": "This is a mock LLM response for testing.",
            "done": True,
            "context": [],
            "total_duration": 100000000,
            "load_duration": 50000000,
            "prompt_eval_duration": 25000000,
            "eval_duration": 25000000,
            "prompt_eval_count": 1,
            "eval_count": 1
        }
    
    def chat(self, messages: list) -> dict:
        """Return mock chat results."""
        return {
            "model": "llama2",
            "created_at": "2024-12-15T22:10:00.000Z",
            "message": {
                "role": "assistant",
                "content": "This is a mock chat response for testing."
            },
            "done": True,
            "total_duration": 100000000,
            "load_duration": 50000000,
            "prompt_eval_duration": 25000000,
            "eval_duration": 25000000,
            "prompt_eval_count": 1,
            "eval_count": 1
        }

class RealLLMService(LLMService):
    """Real LLM service using Ollama."""
    
    def __init__(self):
        """Initialize LLM client."""
        import ollama
        self.client = ollama
    
    def generate(self, prompt: str) -> dict:
        """Generate text using real LLM."""
        try:
            return self.client.generate(model="llama2", prompt=prompt)
        except Exception as e:
            return {
                "error": str(e),
                "response": "",
                "done": True
            }
    
    def chat(self, messages: list) -> dict:
        """Chat using real LLM."""
        try:
            return self.client.chat(model="llama2", messages=messages)
        except Exception as e:
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": ""},
                "done": True
            }

@pytest.fixture
def ocr_service(test_mode):
    """Get OCR service based on test mode."""
    if test_mode == "e2e":
        return RealOCRService()
    return MockOCRService()

@pytest.fixture
def llm_service(test_mode):
    """Get LLM service based on test mode."""
    if test_mode == "mock":
        return MockLLMService()
    else:
        return RealLLMService()
