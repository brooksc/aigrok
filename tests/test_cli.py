"""Test cases for CLI functionality."""
from pathlib import Path
from aigrok.cli import format_output, create_parser, process_single_file, process_file, main
from aigrok.types import ProcessingResult
import pytest
from unittest.mock import patch
import sys
from io import StringIO

def test_format_output_single_file():
    """Test that format_output shows both extracted text and LLM response when both are present."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    # Format without filename (single file)
    output = format_output(result, format_type="text", show_filenames=False)
    assert "test.pdf:" not in output
    assert "Extracted text:\nSample text" in output
    assert "LLM response:\nSample response" in output
    assert output.index("Extracted text:") < output.index("LLM response:")  # Verify order

def test_format_output_text_only():
    """Test that format_output shows only extracted text when no LLM response."""
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response=None,
        metadata={"file_name": "test.pdf"}
    )
    
    output = format_output(result, format_type="text", show_filenames=False)
    assert "Extracted text:\nSample text" in output
    assert "LLM response:" not in output

def test_format_output_llm_only():
    """Test that format_output shows only LLM response when no extracted text."""
    result = ProcessingResult(
        success=True,
        text=None,
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    output = format_output(result, format_type="text", show_filenames=False)
    assert "LLM response:\nSample response" in output
    assert "Extracted text:" not in output

def test_format_output_multiple_files():
    """Test that format_output shows both text and LLM response for multiple files."""
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
    
    # Check first file
    assert "test1.pdf:" in output
    assert "Extracted text:\nSample text 1" in output
    assert "LLM response:\nSample response 1" in output
    
    # Check second file
    assert "test2.pdf:" in output
    assert "Extracted text:\nSample text 2" in output
    assert "LLM response:\nSample response 2" in output
    
    # Verify order within each file's output
    file1_start = output.index("test1.pdf:")
    file2_start = output.index("test2.pdf:")
    assert file1_start < file2_start  # Files are in order
    
    # Verify sections are properly ordered within each file
    file1_text = output[file1_start:file2_start]
    assert file1_text.index("Extracted text:") < file1_text.index("LLM response:")
    
    file2_text = output[file2_start:]
    assert file2_text.index("Extracted text:") < file2_text.index("LLM response:")

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
    """Test markdown formatting with various combinations of text and LLM response."""
    # Test with both text and LLM response
    result = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response="Sample response",
        metadata={"file_name": "test.pdf"}
    )
    
    output = format_output(result, format_type="markdown", show_filenames=False)
    assert "# test.pdf" in output
    assert "## Extracted Text" in output
    assert "Sample text" in output
    assert "## LLM Response" in output
    assert "Sample response" in output
    
    # Verify order of sections
    assert output.index("## Extracted Text") < output.index("## LLM Response")
    
    # Test with only text
    result_text_only = ProcessingResult(
        success=True,
        text="Sample text",
        llm_response=None,
        metadata={"file_name": "text_only.pdf"}
    )
    
    output_text_only = format_output(result_text_only, format_type="markdown", show_filenames=False)
    assert "# text_only.pdf" in output_text_only
    assert "## Extracted Text" in output_text_only
    assert "Sample text" in output_text_only
    assert "## LLM Response" in output_text_only
    assert "N/A" in output_text_only  # LLM response should show N/A
    
    # Test with only LLM response
    result_llm_only = ProcessingResult(
        success=True,
        text=None,
        llm_response="Sample response",
        metadata={"file_name": "llm_only.pdf"}
    )
    
    output_llm_only = format_output(result_llm_only, format_type="markdown", show_filenames=False)
    assert "# llm_only.pdf" in output_llm_only
    assert "## Extracted Text" in output_llm_only
    assert "N/A" in output_llm_only  # Text should show N/A
    assert "## LLM Response" in output_llm_only
    assert "Sample response" in output_llm_only

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

import io
import contextlib
from unittest.mock import patch, MagicMock
import pytest
from aigrok.cli import process_files, format_output
from aigrok.pdf_processor import PDFProcessor, PDFProcessingResult

class TestCLI:
    @pytest.fixture
    def mock_processor(self):
        """Create a mock PDF processor"""
        with patch('aigrok.cli.PDFProcessor') as mock:
            processor = mock.return_value
            processor.process_file.return_value = PDFProcessingResult(
                success=True,
                text="test text",
                llm_response="test response",
                metadata={"file_name": "test.pdf"}
            )
            yield processor

    @pytest.fixture
    def mock_args(self):
        """Create mock arguments"""
        args = MagicMock()
        args.files = ["test.pdf"]
        args.prompt = "test prompt"
        args.format = "text"
        args.output = None
        args.verbose = False
        return args

    def test_immediate_output(self, mock_processor, mock_args):
        """Test that results are output immediately"""
        # Setup multiple mock files
        mock_args.files = ["test1.pdf", "test2.pdf", "test3.pdf"]
        
        # Capture stdout
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            process_files(mock_args)
            output = buf.getvalue()
            
            # Verify each result appears in order
            lines = output.strip().split('\n')
            assert len(lines) == 3
            assert all(':' in line for line in lines)
            assert all(line.endswith("test response") for line in lines)

    def test_llm_response_formats(self, mock_args):
        """Test different LLM response formats"""
        processor = PDFProcessor()
        
        # Test object-style response
        class MockObjectResponse:
            class Choice:
                class Message:
                    content = "test content"
                choices = [Message()]
            choices = [Choice()]
        
        # Test dict-style response
        dict_response = {
            'choices': [{
                'message': {
                    'content': 'test content'
                }
            }]
        }
        
        with patch('aigrok.pdf_processor.litellm.completion') as mock_llm:
            # Test object response
            mock_llm.return_value = MockObjectResponse()
            result = processor._query_llm("test prompt", "", "openai", None)
            assert result == "test content"
            
            # Test dict response
            mock_llm.return_value = dict_response
            result = processor._query_llm("test prompt", "", "openai", None)
            assert result == "test content"
            
            # Test invalid responses
            for invalid_response in [{}, {'choices': []}, {'choices': [{}]}, None]:
                mock_llm.return_value = invalid_response
                result = processor._query_llm("test prompt", "", "openai", None)
                assert result is None or "Error" in result

    def test_error_handling(self, mock_args):
        """Test error handling in processing"""
        processor = PDFProcessor()
        
        with patch('aigrok.pdf_processor.litellm.completion') as mock_llm:
            # Test network error
            mock_llm.side_effect = ConnectionError("Network error")
            result = processor._query_llm("test prompt", "", "openai", None)
            assert "Error" in result
            
            # Test timeout
            mock_llm.side_effect = TimeoutError("Timeout")
            result = processor._query_llm("test prompt", "", "openai", None)
            assert "Error" in result
            
            # Test malformed response
            mock_llm.return_value = "invalid response"
            result = processor._query_llm("test prompt", "", "openai", None)
            assert result is None or "Error" in result

    def test_end_to_end_processing(self, mock_processor, mock_args):
        """Test complete processing pipeline"""
        # Setup multiple files with different responses
        responses = [
            PDFProcessingResult(success=True, text="text1", llm_response="response1", metadata={"file_name": "test1.pdf"}),
            PDFProcessingResult(success=True, text="text2", llm_response="response2", metadata={"file_name": "test2.pdf"}),
            PDFProcessingResult(success=False, error="Failed", metadata={"file_name": "test3.pdf"})
        ]
        
        mock_processor.process_file.side_effect = responses
        mock_args.files = ["test1.pdf", "test2.pdf", "test3.pdf"]
        
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            process_files(mock_args)
            output = buf.getvalue()
            
            # Verify successful outputs
            assert "test1.pdf:response1" in output
            assert "test2.pdf:response2" in output
            # Verify failed file doesn't output
            assert "test3.pdf" not in output

    def test_output_formatting(self):
        """Test output formatting options"""
        results = [
            PDFProcessingResult(success=True, text="text1", llm_response="response1", metadata={"file_name": "test1.pdf"}),
            PDFProcessingResult(success=True, text="text2", llm_response="response2", metadata={"file_name": "test2.pdf"})
        ]
        
        # Test text format
        text_output = format_output(results, format_type="text", show_filenames=True)
        assert "test1.pdf:response1" in text_output
        assert "test2.pdf:response2" in text_output
        
        # Test JSON format
        json_output = format_output(results, format_type="json", show_filenames=True)
        assert '"file_name": "test1.pdf"' in json_output
        assert '"llm_response": "response1"' in json_output
        
        # Test markdown format
        md_output = format_output(results, format_type="markdown", show_filenames=True)
        assert "# test1.pdf" in md_output
        assert "## LLM Response" in md_output
