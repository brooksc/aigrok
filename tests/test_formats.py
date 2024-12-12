"""
Tests for file format handling and validation.
"""
import pytest
from pathlib import Path
from aigrok.formats import validate_format, get_supported_formats, SUPPORTED_FORMATS

def test_supported_formats():
    """Test that supported formats are correctly defined."""
    formats = get_supported_formats()
    assert '.pdf' in formats
    assert '.txt' in formats
    assert formats['.pdf'] == 'PDF Document'
    assert formats['.txt'] == 'Plain Text'

def test_validate_pdf_format():
    """Test PDF format validation."""
    # Test with .pdf extension
    result = validate_format("test.pdf")
    assert result.is_valid
    assert result.format_name == 'PDF Document'
    assert result.error is None

    # Test with PDF type hint
    result = validate_format("test.file", type_hint="pdf")
    assert result.is_valid
    assert result.format_name == 'PDF Document'
    assert result.error is None

    # Test with uppercase extension
    result = validate_format("test.PDF")
    assert result.is_valid
    assert result.format_name == 'PDF Document'
    assert result.error is None

def test_validate_text_format():
    """Test text format validation."""
    # Test with .txt extension
    result = validate_format("test.txt")
    assert result.is_valid
    assert result.format_name == 'Plain Text'
    assert result.error is None

    # Test with text type hint
    result = validate_format("test.file", type_hint="txt")
    assert result.is_valid
    assert result.format_name == 'Plain Text'
    assert result.error is None

    # Test with uppercase extension
    result = validate_format("test.TXT")
    assert result.is_valid
    assert result.format_name == 'Plain Text'
    assert result.error is None

def test_unsupported_formats():
    """Test rejection of unsupported formats."""
    unsupported_formats = [
        "test.docx",
        "test.mp3",
        "test.mp4",
        "test.jpg",
        "test.png",
        "test.wav",
        "test"  # No extension
    ]
    
    for file_path in unsupported_formats:
        result = validate_format(file_path)
        assert not result.is_valid
        assert result.format_name is None
        assert "Unsupported file format" in result.error
        assert ".pdf" in result.error
        assert ".txt" in result.error

def test_invalid_type_hints():
    """Test rejection of invalid type hints."""
    invalid_hints = ["doc", "mp3", "jpg", "invalid"]
    
    for hint in invalid_hints:
        result = validate_format("test.file", type_hint=hint)
        assert not result.is_valid
        assert result.format_name is None
        assert "Unsupported format type" in result.error
        assert ".pdf" in result.error
        assert ".txt" in result.error

def test_path_handling():
    """Test handling of different path formats."""
    # Test with Path object
    result = validate_format(Path("test.pdf"))
    assert result.is_valid
    assert result.format_name == 'PDF Document'

    # Test with absolute path
    result = validate_format("/absolute/path/test.txt")
    assert result.is_valid
    assert result.format_name == 'Plain Text'

    # Test with relative path
    result = validate_format("./relative/path/test.pdf")
    assert result.is_valid
    assert result.format_name == 'PDF Document'

def test_format_case_sensitivity():
    """Test case sensitivity in format handling."""
    variations = [
        ("test.PDF", True),
        ("test.pdf", True),
        ("test.Pdf", True),
        ("test.TXT", True),
        ("test.txt", True),
        ("test.Txt", True),
        ("TEST.PDF", True),
        ("TEST.TXT", True)
    ]
    
    for file_path, should_be_valid in variations:
        result = validate_format(file_path)
        assert result.is_valid == should_be_valid

def test_type_hint_case_sensitivity():
    """Test case sensitivity in type hints."""
    variations = [
        ("PDF", True),
        ("pdf", True),
        ("Pdf", True),
        ("TXT", True),
        ("txt", True),
        ("Text", False),  # Should fail as we expect exact match (case-insensitive)
        ("PDF ", False),  # Should fail due to whitespace
        (" txt", False)   # Should fail due to whitespace
    ]
    
    for hint, should_be_valid in variations:
        result = validate_format("test.file", type_hint=hint)
        assert result.is_valid == should_be_valid, f"Failed for hint: {hint}" 

def test_comprehensive_unsupported_formats():
    """Test rejection of a comprehensive list of unsupported formats."""
    unsupported_formats = [
        # Binary formats
        "test.exe", "test.dll", "test.so", "test.dylib",
        # Archive formats
        "test.zip", "test.tar", "test.gz", "test.7z",
        # Image formats
        "test.jpg", "test.png", "test.gif", "test.webp",
        # Document formats
        "test.docx", "test.rtf", "test.odt", "test.pages",
        # Data formats
        "test.csv", "test.json", "test.xml", "test.yaml",
        # Web formats
        "test.html", "test.htm", "test.js", "test.css",
        # No extension
        "test", "noextension", ".hidden"
    ]
    
    for file_path in unsupported_formats:
        result = validate_format(file_path)
        assert not result.is_valid, f"Format {file_path} should be rejected"
        assert result.format_name is None
        assert "Unsupported file format" in result.error
        assert ".pdf" in result.error and ".txt" in result.error

def test_edge_case_formats():
    """Test edge cases in format handling."""
    edge_cases = [
        # Multiple extensions
        ("test.txt.pdf", False),  # Should reject ambiguous extensions
        ("test.pdf.txt", False),  # Should reject ambiguous extensions
        # Hidden files
        (".test.txt", True),     # Should accept if extension is valid
        (".test.pdf", True),     # Should accept if extension is valid
        (".test", False),        # Should reject no extension
        # Special characters
        ("test file.pdf", True),  # Spaces in name
        ("test-file.txt", True),  # Hyphens
        ("test_file.pdf", True),  # Underscores
        ("test.PDF.txt", False),  # Mixed case multiple extensions
        # Unicode filenames
        ("测试.pdf", True),        # Chinese characters
        ("тест.txt", True),       # Cyrillic characters
        ("test™.pdf", True),      # Special characters
        # Path-like names
        ("path/to/file.txt", True),
        ("/absolute/path/file.pdf", True),
        ("../relative/path/file.txt", True)
    ]
    
    for file_path, should_accept in edge_cases:
        result = validate_format(file_path)
        assert result.is_valid == should_accept, \
            f"Format {file_path} validation failed: expected {should_accept}, got {result.is_valid}"
        if should_accept:
            assert result.format_name is not None
            assert result.error is None
        else:
            assert result.format_name is None
            assert result.error is not None

def test_type_hint_with_no_extension():
    """Test type hints for files without extensions."""
    cases = [
        ("noext", "pdf", True),
        ("noext", "txt", True),
        (".hidden", "pdf", True),
        ("file", "invalid", False),
        ("", "pdf", True),
        ("", "txt", True)
    ]
    
    for file_path, hint, should_accept in cases:
        result = validate_format(file_path, type_hint=hint)
        assert result.is_valid == should_accept, \
            f"File '{file_path}' with hint '{hint}' validation failed"
        if should_accept:
            assert result.format_name is not None
            assert result.error is None
        else:
            assert result.format_name is None
            assert result.error is not None 