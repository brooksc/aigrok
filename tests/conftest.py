"""
Test configuration and fixtures.
"""
import os
import shutil
import pytest
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import tempfile

# Set default test environment variables
os.environ.setdefault("AIGROK_TEST_MODE", "mock")
os.environ.setdefault("AIGROK_MOCK_RESPONSES", "true")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")

def create_test_image(text: str, size=(800, 400), bg_color="white", text_color="black"):
    """Create a test image with text."""
    image = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_position = ((size[0] - text_bbox[2]) // 2, (size[1] - text_bbox[3]) // 2)
    draw.text(text_position, text, font=font, fill=text_color)
    return image

@pytest.fixture
def test_mode():
    """Get test mode from environment."""
    return os.getenv("AIGROK_TEST_MODE", "mock")

@pytest.fixture
def test_dir():
    """Create a temporary directory for testing."""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    
    # Cleanup: Remove all files and directories recursively
    if test_dir.exists():
        for file in test_dir.glob('**/*'):
            try:
                if file.is_file():
                    file.unlink()
                elif file.is_dir():
                    file.rmdir()
            except Exception as e:
                print(f"Warning: Failed to remove {file}: {e}")
        try:
            test_dir.rmdir()
        except Exception as e:
            print(f"Warning: Failed to remove test directory: {e}")

@pytest.fixture
def test_files(test_dir):
    """Create test files for OCR testing."""
    # Create test image with text
    img_path = test_dir / "test.png"
    img = Image.new('RGB', (300, 100), color='white')
    d = ImageDraw.Draw(img)
    d.text((10,10), "Hello World", fill='black')
    img.save(img_path)
    
    # Create empty image
    empty_img_path = test_dir / "empty.png"
    empty_img = Image.new('RGB', (100, 100), color='white')
    empty_img.save(empty_img_path)
    
    # Create invalid file
    invalid_path = test_dir / "test.txt"
    invalid_path.write_text("Not an image file")
    
    return {
        "image": img_path,
        "empty": empty_img_path,
        "invalid": invalid_path
    }

@pytest.fixture
def invoice_pdf(test_files):
    """Get path to invoice test image."""
    return test_files["image"]

@pytest.fixture
def simple_pdf(test_files):
    """Get path to simple test image."""
    return test_files["empty"]

@pytest.fixture
def not_a_pdf(test_files):
    """Get path to non-PDF test file."""
    return test_files["invalid"]

@pytest.fixture
def ocr_service(test_mode):
    """Get OCR service based on test mode."""
    from .services import MockOCRService, RealOCRService
    if test_mode == "mock":
        return MockOCRService()
    else:
        return RealOCRService()

@pytest.fixture
def llm_service(test_mode):
    """Get LLM service based on test mode."""
    from .services import MockLLMService, RealLLMService
    if test_mode == "mock":
        return MockLLMService()
    else:
        return RealLLMService()

@pytest.fixture
def mock_llm_response(monkeypatch):
    """Mock LLM response for testing."""
    def mock_completion(*args, **kwargs):
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
    
    if os.getenv("AIGROK_TEST_MODE") == "mock":
        import ollama
        monkeypatch.setattr(ollama, "chat", mock_completion)
        monkeypatch.setattr(ollama, "generate", mock_completion)

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    test_vars = {
        "AIGROK_TEST_MODE": "mock",
        "AIGROK_MOCK_RESPONSES": "true",
        "OLLAMA_BASE_URL": "http://localhost:11434"
    }
    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)

@pytest.fixture(autouse=True)
def cleanup_test_files(request, test_dir):
    """Clean up test files after tests."""
    def cleanup():
        pass
    
    request.addfinalizer(cleanup)