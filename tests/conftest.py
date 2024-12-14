"""
Test fixtures and configuration.
"""
import os
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def test_files_dir():
    """Get the test files directory."""
    return Path(__file__).parent / "files"

@pytest.fixture(scope="session")
def ensure_test_files(test_files_dir):
    """Ensure test files exist."""
    # Create test files directory if it doesn't exist
    test_files_dir.mkdir(exist_ok=True)
    
    # Create test PDFs if they don't exist
    files = {
        "invoice.pdf": b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [3 0 R]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 68\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Invoice Date: 2016.01.25) Tj\n(Due Date: 2016.01.31) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000254 00000 n\n0000000321 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n439\n%%EOF",
        "simple.pdf": b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [3 0 R]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Simple test PDF) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000254 00000 n\n0000000321 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n415\n%%EOF",
        "empty.pdf": b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 0\n/Kids []\n>>\nendobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\ntrailer\n<<\n/Size 3\n/Root 1 0 R\n>>\nstartxref\n115\n%%EOF",
        "not_a_pdf.txt": b"This is not a PDF file",
    }
    
    for filename, content in files.items():
        file_path = test_files_dir / filename
        if not file_path.exists():
            file_path.write_bytes(content)
    
    return test_files_dir

@pytest.fixture
def invoice_pdf(ensure_test_files, test_files_dir):
    """Get path to invoice test PDF."""
    return test_files_dir / "invoice.pdf"

@pytest.fixture
def simple_pdf(ensure_test_files, test_files_dir):
    """Get path to simple test PDF."""
    return test_files_dir / "simple.pdf"

@pytest.fixture
def empty_pdf(ensure_test_files, test_files_dir):
    """Get path to empty test PDF."""
    return test_files_dir / "empty.pdf"

@pytest.fixture
def not_a_pdf(ensure_test_files, test_files_dir):
    """Get path to non-PDF test file."""
    return test_files_dir / "not_a_pdf.txt"

@pytest.fixture(autouse=True)
def cleanup_test_files(request, test_files_dir):
    """Clean up test files after tests."""
    yield
    if request.node.get_closest_marker('no_cleanup'):
        return
    
    # Clean up any additional files created during tests
    for file in test_files_dir.glob("*"):
        if file.name not in ["invoice.pdf", "simple.pdf", "empty.pdf", "not_a_pdf.txt"]:
            file.unlink() 