"""Test cases for CLI functionality."""
from pathlib import Path
from aigrok.cli import format_output, create_parser, process_single_file, process_file, main
from aigrok.types import ProcessingResult
import pytest
from unittest.mock import patch
import sys
from io import StringIO

def test_format_output_single_file():
    """Test that format_output doesn't add filename prefix for single file in text mode."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    # Format without filename (single file)
    output = format_output(result, format_type="text", show_filenames=False)
    assert "test.pdf:" not in output
    assert output == "Sample response"

def test_format_output_multiple_files():
    """Test that format_output adds filename prefix for multiple files in text mode."""
    results = [
        ProcessingResult(
            success=True,
            text="Sample text 1",
            llm_response="Sample response 1",
            metadata={"file_name": "test1.pdf"}
        ),
        ProcessingResult(
            success=True,
            text="Sample text 2",
            llm_response="Sample response 2",
            metadata={"file_name": "test2.pdf"}
        )
    ]
    
    # Format with filenames (multiple files)
    output = format_output(results, format_type="text", show_filenames=True)
    assert "test1.pdf: Sample response 1" in output
    assert "test2.pdf: Sample response 2" in output

def test_format_output_json():
    """Test that format_output includes filenames in JSON mode regardless of show_filenames."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    # Format as JSON (should always include filename)
    output = format_output(result, format_type="json", show_filenames=False)
    assert '"file_name": "test.pdf"' in output

def test_format_output_markdown():
    """Test that format_output includes filenames in Markdown mode regardless of show_filenames."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    # Format as Markdown (should always include filename)
    output = format_output(result, format_type="markdown", show_filenames=False)
    assert "# test.pdf" in output

@pytest.fixture
def mock_pdf_processor():
    """Create a mock PDFProcessor."""
    with patch('aigrok.cli.PDFProcessor') as mock:
        processor = mock.return_value
        processor.process_file.return_value = ProcessingResult(
            success=True,
            text="Sample text",
            llm_response="Sample response",
            metadata={"file_name": "test.pdf"}
        )
        yield processor

@pytest.fixture
def sample_pdf(tmp_path):
    """Create a sample PDF file."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")  # Minimal valid PDF
    return pdf_path

def test_create_parser():
    """Test argument parser creation."""
    parser = create_parser()

    # Test with valid arguments
    args = parser.parse_args(["prompt", "file1.pdf"])
    assert args.prompt == "prompt"
    assert args.files == ["file1.pdf"]

    # Test with multiple files
    args = parser.parse_args(["prompt", "file1.pdf", "file2.pdf"])
    assert args.prompt == "prompt"
    assert args.files == ["file1.pdf", "file2.pdf"]

    # Test with no arguments should raise SystemExit
    with pytest.raises(SystemExit):
        parser.parse_args([])

def test_process_single_file(mock_pdf_processor, sample_pdf):
    """Test processing a single PDF file."""
    result = process_single_file(sample_pdf, "Analyze this")
    
    assert result.success
    assert result.llm_response == "Sample response"
    
    # Verify processor was called correctly
    mock_pdf_processor.process_file.assert_called_once_with(
        sample_pdf,
        "Analyze this"
    )

def test_process_file_list(mock_pdf_processor, tmp_path):
    """Test processing multiple PDF files."""
    # Create multiple sample PDFs
    pdf1 = tmp_path / "test1.pdf"
    pdf2 = tmp_path / "test2.pdf"
    pdf1.write_bytes(b"%PDF-1.4\n")
    pdf2.write_bytes(b"%PDF-1.4\n")
    
    results = process_file([pdf1, pdf2], "Analyze these")
    
    assert isinstance(results, list)
    assert len(results) == 2
    assert all(r.success for r in results)
    
    # Verify processor was called for each file
    assert mock_pdf_processor.process_file.call_count == 2

def test_main_single_file(mock_pdf_processor, sample_pdf, monkeypatch):
    """Test main function with single file."""
    pdf_path = sample_pdf

    # Capture stdout
    output = StringIO()
    monkeypatch.setattr(sys, 'stdout', output)

    # Run with single file
    with patch('sys.argv', ['aigrok', 'analyze this', str(pdf_path)]), \
         pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0

def test_main_error_handling():
    """Test error handling in main function."""
    # Test with nonexistent file
    with patch('sys.argv', ['aigrok', 'test prompt', 'nonexistent.pdf']):
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code != 0

def test_main_configure():
    """Test configuration mode."""
    with patch('sys.argv', ['aigrok', '--configure']):
        with patch('aigrok.cli.ConfigManager') as mock_config:
            mock_config.return_value.configure.return_value = True
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0

def test_no_arguments_shows_help():
    """Test that running without arguments shows help."""
    with patch('sys.argv', ['aigrok']):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code != 0

def test_version_flag():
    """Test version flag."""
    with patch('sys.argv', ['aigrok', '--version']):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

def test_logging_disabled_by_default(capsys):
    """Test that logging is disabled by default."""
    with patch('sys.argv', ['aigrok', 'test prompt', 'test.pdf']):
        with patch('pathlib.Path.exists', return_value=True):
            with pytest.raises(SystemExit):
                main()
    
    captured = capsys.readouterr()
    # No debug output should be present
    assert "DEBUG" not in captured.err

def test_logging_enabled_with_verbose(capsys):
    """Test that logging is enabled with --verbose."""
    with patch('sys.argv', ['aigrok', '--verbose', 'test prompt', 'test.pdf']):
        with patch('pathlib.Path.exists', return_value=True):
            with pytest.raises(SystemExit):
                main()
    
    captured = capsys.readouterr()
    # Debug output should be present
    assert "DEBUG" in captured.err
    assert "Arguments:" in captured.err
    assert "Verbose mode: True" in captured.err

def test_logging_scoped_to_aigrok(capsys):
    """Test that logging is only enabled for aigrok modules."""
    with patch('sys.argv', ['aigrok', '--verbose', 'test prompt', 'test.pdf']):
        with patch('pathlib.Path.exists', return_value=True):
            # Log from another module
            import logging
            logging.debug("Debug from another module")
            with pytest.raises(SystemExit):
                main()
    
    captured = capsys.readouterr()
    # Our debug output should be present
    assert "Arguments:" in captured.err
    # But debug from other modules should not
    assert "Debug from another module" not in captured.err

def test_help_format(capsys):
    """Test that help message follows Unix conventions."""
    parser = create_parser()
    with pytest.raises(SystemExit) as e:
        parser.parse_args(['--help'])
    assert e.value.code == 0
    captured = capsys.readouterr()
    help_text = captured.out
    
    # Check Unix-style format
    assert "usage: aigrok [options] PROMPT file ..." in help_text

@pytest.fixture
def mock_ollama():
    """Mock Ollama response."""
    with patch('ollama.list') as mock:
        mock.return_value = {
            'models': [
                {'name': 'llama3.2:3b'},
                {'name': 'llama3.2-vision:11b'}
            ]
        }
        yield mock

def test_configure_creates_default_config(tmp_path, mock_ollama):
    """Test that configure creates a default config file."""
    config_dir = tmp_path / ".config" / "aigrok"
    config_file = config_dir / "config.yaml"

    with patch('aigrok.config.ConfigManager.CONFIG_DIR', config_dir), \
         patch('aigrok.config.ConfigManager.CONFIG_FILE', config_file), \
         patch('sys.argv', ['aigrok', '--configure']), \
         pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert config_file.exists()

def test_configure_with_ollama_error(tmp_path):
    """Test configure handles Ollama errors gracefully."""
    config_dir = tmp_path / ".config" / "aigrok"
    config_file = config_dir / "config.yaml"

    with patch('aigrok.config.ConfigManager.CONFIG_DIR', config_dir), \
         patch('aigrok.config.ConfigManager.CONFIG_FILE', config_file), \
         patch('ollama.list', side_effect=Exception("Failed to connect")), \
         patch('sys.argv', ['aigrok', '--configure']), \
         pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert config_file.exists()
