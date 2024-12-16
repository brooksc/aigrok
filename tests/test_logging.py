"""Test cases for logging configuration."""
import io
import sys
from pathlib import Path
from loguru import logger
from aigrok.logging import configure_logging
from aigrok.cli import main
from aigrok.config import ConfigManager
from pydantic import BaseModel

class ModelConfig(BaseModel):
    text_model: str
    vision_model: str

class OCRConfig(BaseModel):
    enabled: bool = False
    languages: list[str] = ["en"]
    fallback: bool = True

class AigrokConfig(BaseModel):
    model_config: ModelConfig
    ocr_config: OCRConfig

    @property
    def ocr_enabled(self) -> bool:
        return self.ocr_config.enabled

    @property
    def ocr_languages(self) -> list[str]:
        return self.ocr_config.languages

    @property
    def ocr_fallback(self) -> bool:
        return self.ocr_config.fallback

    @property
    def text_model(self) -> str:
        return self.model_config.text_model

    @property
    def vision_model(self) -> str:
        return self.model_config.vision_model

def test_logging_disabled_by_default(monkeypatch, capsys):
    """Test that logging is disabled in CLI when --verbose is not used."""
    # Mock sys.argv
    test_args = ["aigrok", "test.pdf"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    # Run main
    try:
        main()
    except Exception:
        pass  # Ignore errors, we just want to check logging
    
    # Check that no debug messages were logged
    captured = capsys.readouterr()
    assert "DEBUG" not in captured.err

def test_logging_enabled_with_verbose(monkeypatch, capsys):
    """Test that logging is enabled in CLI when --verbose is used."""
    # Mock sys.argv
    test_args = ["aigrok", "--verbose", "test.pdf"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    # Run main
    try:
        main()
    except Exception:
        pass  # Ignore errors, we just want to check logging
    
    # Check that debug messages were logged
    captured = capsys.readouterr()
    assert "DEBUG" in captured.err

def test_logging_configuration_isolation():
    """Test that logging configuration is properly isolated."""
    # Capture stderr
    stderr = io.StringIO()
    sys.stderr = stderr
    
    try:
        # Start with logging disabled
        configure_logging(verbose=False)
        logger.debug("Should not appear")
        assert stderr.getvalue() == ""
        
        # Enable logging
        configure_logging(verbose=True)
        logger.debug("Should appear")
        assert "Should appear" in stderr.getvalue()
        
        # Create new PDF processor (which might try to configure logging)
        from aigrok.pdf_processor import PDFProcessor
        
        # Create a mock config manager with a valid config
        config_manager = ConfigManager()
        model_config = ModelConfig(text_model="llama3.2:3b", vision_model="llama3.2-vision:11b")
        ocr_config = OCRConfig(enabled=False)
        config_manager.config = AigrokConfig(model_config=model_config, ocr_config=ocr_config)
        
        processor = PDFProcessor(config_manager=config_manager, verbose=False)  # Should not affect global logging
        
        # Log something else to verify logging is still enabled
        logger.debug("Should still appear")
        assert "Should still appear" in stderr.getvalue()
    finally:
        # Restore stderr
        sys.stderr = sys.__stderr__
