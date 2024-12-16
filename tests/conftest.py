"""
Test configuration and fixtures.
"""
import os
import shutil
import pytest
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

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
    return os.getenv("TEST_MODE", "mock")

@pytest.fixture
def test_dir(tmp_path):
    """Create and return a temporary test directory."""
    return tmp_path

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

@pytest.fixture(autouse=True)
def cleanup_test_files(request, test_dir):
    """Clean up test files after tests."""
    def cleanup():
        if test_dir.exists():
            for file in test_dir.iterdir():
                try:
                    file.unlink()
                except Exception:
                    pass
            test_dir.rmdir()
    
    request.addfinalizer(cleanup)