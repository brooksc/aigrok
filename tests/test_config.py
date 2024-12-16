"""Tests for configuration management."""
import os
from pathlib import Path
import pytest
from unittest.mock import MagicMock
import yaml
from pydantic import ValidationError
from aigrok.config import ConfigManager, ModelConfig, OCRConfig, AigrokConfig

@pytest.fixture
def config_manager():
    """Create a ConfigManager instance for testing."""
    manager = ConfigManager()
    # Ensure we start with a clean state
    if manager.CONFIG_FILE.exists():
        manager.CONFIG_FILE.unlink()
    if not manager.CONFIG_DIR.exists():
        manager.CONFIG_DIR.mkdir(parents=True)
    return manager

def test_model_config_validation():
    """Test ModelConfig validation."""
    # Valid config
    config = ModelConfig(provider="ollama", model_name="llama3.2:3b")
    assert config.provider == "ollama"
    assert config.model_name == "llama3.2:3b"
    assert config.endpoint is None

    # Test with endpoint
    config = ModelConfig(provider="ollama", model_name="llama3.2:3b", endpoint="http://localhost:11434")
    assert config.endpoint == "http://localhost:11434"

    # Test model_dump with name field
    config_dict = {"provider": "ollama", "model_name": "llama3.2:3b"}
    config = ModelConfig(**config_dict)
    dumped = config.model_dump()
    assert "model_name" in dumped
    assert dumped["model_name"] == "llama3.2:3b"

def test_ocr_config_defaults():
    """Test OCRConfig default values."""
    config = OCRConfig()
    assert config.enabled is False
    assert config.languages == ["en"]
    assert config.fallback is False

def test_aigrok_config_validation():
    """Test AigrokConfig validation."""
    # Valid minimal config
    config = AigrokConfig(
        text_model=ModelConfig(provider="ollama", model_name="llama3.2:3b"),
        vision_model=ModelConfig(provider="ollama", model_name="llama3.2-vision:11b")
    )
    assert config.text_model.provider == "ollama"
    assert config.vision_model.provider == "ollama"
    assert config.audio_model is None
    assert config.ocr_enabled is False
    assert config.ocr_languages == ["en"]
    assert config.ocr_fallback is False

def test_supported_providers():
    """Test supported providers configuration."""
    manager = ConfigManager()
    
    # Test text model providers
    text_providers = manager._get_providers("text")
    assert "ollama" in text_providers
    assert "openai" in text_providers
    
    # Test vision model providers
    vision_providers = manager._get_providers("vision")
    assert "ollama" in vision_providers
    assert "openai" in vision_providers
    
    # Test getting models for a provider
    openai_text_models = manager._get_models("openai", "text")
    assert "gpt-4" in openai_text_models
    assert "gpt-3.5-turbo" in openai_text_models

def test_config_file_creation(config_manager):
    """Test configuration file creation."""
    # Initial state
    if config_manager.CONFIG_FILE.exists():
        config_manager.CONFIG_FILE.unlink()
    
    # Configure with minimal settings
    config = AigrokConfig(
        text_model=ModelConfig(provider="ollama", model_name="llama3.2:3b"),
        vision_model=ModelConfig(provider="ollama", model_name="llama3.2-vision:11b")
    )
    config_manager.config = config
    
    # Save and verify
    config_manager.save_config()
    assert config_manager.CONFIG_FILE.exists()
    assert config_manager.CONFIG_FILE.is_file()

def test_config_loading(config_manager):
    """Test configuration loading."""
    # Create a test configuration
    config = AigrokConfig(
        text_model=ModelConfig(provider="ollama", model_name="llama3.2:3b"),
        vision_model=ModelConfig(provider="ollama", model_name="llama3.2-vision:11b")
    )
    
    # Save config directly to file
    config_dict = {
        "text_model": {"provider": "ollama", "model_name": "llama3.2:3b"},
        "vision_model": {"provider": "ollama", "model_name": "llama3.2-vision:11b"},
        "ocr_enabled": False,
        "ocr_languages": ["en"],
        "ocr_fallback": False
    }
    os.makedirs(config_manager.CONFIG_DIR, exist_ok=True)
    with open(config_manager.CONFIG_FILE, 'w') as f:
        yaml.dump(config_dict, f)
    
    # Create new manager to test loading
    new_manager = ConfigManager()
    assert new_manager.config is not None
    assert new_manager.config.text_model.provider == "ollama"
    assert new_manager.config.text_model.model_name == "llama3.2:3b"

def test_ollama_model_detection(monkeypatch):
    """Test Ollama model detection."""
    # Mock the ollama module with realistic model list
    mock_ollama = MagicMock()
    mock_ollama.list.return_value = [
        {"name": "llama3.2:3b"},
        {"name": "llama3.2-vision:11b"},
        {"name": "llama3.2:1b"},
        {"name": "opencoder:8b"},
        {"name": "phi3:mini-128k"}
    ]
    monkeypatch.setattr("aigrok.config.ollama", mock_ollama)
    
    manager = ConfigManager()
    models = manager._get_ollama_models()
    assert "llama3.2:3b" in models["text_models"]
    assert "llama3.2-vision:11b" in models["vision_models"]

def test_provider_model_count():
    """Test provider model count calculation."""
    manager = ConfigManager()
    
    # Test OpenAI model counts
    text_count = len(manager._get_models("openai", "text"))
    vision_count = len(manager._get_models("openai", "vision"))
    audio_count = len(manager._get_models("openai", "audio"))
    
    assert text_count > 0
    assert vision_count > 0
    assert audio_count > 0  # OpenAI has Whisper

def test_invalid_provider():
    """Test handling of invalid provider."""
    manager = ConfigManager()
    
    # Test with non-existent provider
    with pytest.raises(KeyError):
        manager._get_provider_model_count("invalid_provider", "text")
