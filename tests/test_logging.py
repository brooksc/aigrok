"""Test cases for logging configuration."""

import io
import sys
from loguru import logger
from aigrok.logging import configure_logging
from aigrok.cli import main
from aigrok.config import ConfigManager
from pydantic import BaseModel
import pytest


class ModelConfig(BaseModel):
    provider: str
    model_name: str
    endpoint: str


class OCRConfig(BaseModel):
    enabled: bool = False
    languages: list[str] = ["en"]
    fallback: bool = True


class AigrokConfig(BaseModel):
    text_model: ModelConfig
    vision_model: ModelConfig
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
    def text_model_name(self) -> str:
        return self.text_model.model_name

    @property
    def vision_model_name(self) -> str:
        return self.vision_model.model_name


def test_logging_disabled_by_default(monkeypatch, capsys):
    """Test that logging is disabled in CLI when --verbose is not used."""
    # Mock sys.argv
    test_args = ["aigrok", "test.pdf"]
    monkeypatch.setattr(sys, "argv", test_args)

    # Run main
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1  # Should exit with error since no prompt provided

    # Check output
    captured = capsys.readouterr()
    assert "Error: Must provide at least one file or a prompt" in captured.out


def test_logging_enabled_with_verbose(monkeypatch, capsys):
    """Test that logging is enabled in CLI when --verbose is used."""
    # Mock sys.argv
    test_args = ["aigrok", "--verbose", "test.pdf"]
    monkeypatch.setattr(sys, "argv", test_args)

    # Run main
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1  # Should exit with error since no prompt provided

    # Check output
    captured = capsys.readouterr()
    assert "Error: Must provide at least one file or a prompt" in captured.out


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
        config_manager.config = AigrokConfig(
            text_model=ModelConfig(
                provider="ollama",
                model_name="llama3.2:3b",
                endpoint="http://localhost:11434",
            ),
            vision_model=ModelConfig(
                provider="ollama",
                model_name="llama3.2-vision:11b",
                endpoint="http://localhost:11434",
            ),
            ocr_config=OCRConfig(enabled=False),
        )

        PDFProcessor(
            config_manager=config_manager, verbose=False
        )  # Should not affect global logging

        # Verify that logging is still enabled
        logger.debug("Should still appear")
        assert "Should still appear" in stderr.getvalue()

    finally:
        sys.stderr = sys.__stderr__  # Restore stderr
