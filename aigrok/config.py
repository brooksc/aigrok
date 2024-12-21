"""
Configuration management for aigrok.

This module handles:
1. Initial configuration and setup
2. Model selection and validation
3. API key management
4. Configuration persistence
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from pydantic import BaseModel, Field
import litellm
from loguru import logger
import ollama
import httpx

class ModelConfig(BaseModel):
    """Configuration for a model."""
    provider: str
    model_name: str
    endpoint: Optional[str] = None
    
    model_config = {
        'protected_namespaces': (),
        'extra': 'allow'
    }
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """Override model_dump to handle name field."""
        data = super().model_dump(*args, **kwargs)
        if 'name' in data:
            data['model_name'] = data.pop('name')
        return data

class OCRConfig(BaseModel):
    """Configuration for OCR."""
    enabled: bool = False
    languages: List[str] = Field(default_factory=lambda: ["en"])
    fallback: bool = False

class AigrokConfig(BaseModel):
    """Main configuration class."""
    text_model: ModelConfig
    vision_model: ModelConfig
    audio_model: Optional[ModelConfig] = None
    ocr_enabled: bool = Field(default=False)
    ocr_languages: List[str] = Field(default_factory=lambda: ["en"])
    ocr_fallback: bool = Field(default=False)
    ocr_confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    class Config:
        extra = "allow"

class ConfigManager:
    """Configuration manager."""
    CONFIG_DIR = Path.home() / ".config" / "aigrok"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    
    SUPPORTED_PROVIDERS = {
        "ollama": {
            "description": "Local LLM models via Ollama",
            "endpoint_required": True,
            "default_endpoint": "http://localhost:11434"
        },
        "openai": {
            "description": "OpenAI's GPT models",
            "env_var": "OPENAI_API_KEY",
            "endpoint_required": False
        }
    }
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config = None
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file."""
        try:
            # Create config directory if it doesn't exist
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # If config file doesn't exist, initialize with empty config
            if not self.CONFIG_FILE.exists():
                self.config = None
                return

            with open(self.CONFIG_FILE, 'r') as f:
                config_dict = yaml.safe_load(f) or {}  # Handle empty file case
                
            # Convert old config format
            if config_dict.get('ocr') and isinstance(config_dict['ocr'], dict):
                config_dict['ocr_enabled'] = config_dict['ocr'].get('enabled', False)
                config_dict['ocr_languages'] = config_dict['ocr'].get('languages', ['en'])
                config_dict['ocr_fallback'] = config_dict['ocr'].get('fallback', False)
                del config_dict['ocr']
                
            # Convert old model format
            for model_key in ['text_model', 'vision_model', 'audio_model']:
                if model_key in config_dict:
                    model = config_dict[model_key]
                    if isinstance(model, dict):
                        if 'api_base' in model:
                            model['endpoint'] = model.pop('api_base')
                        if 'api_key' in model:
                            model.pop('api_key')
            
            # Only try to create AigrokConfig if we have required fields
            if 'text_model' in config_dict and 'vision_model' in config_dict:
                self.config = AigrokConfig(**config_dict)
            else:
                self.config = None
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = None
    
    def _get_providers(self, model_type: str) -> List[str]:
        """Get supported providers for a model type."""
        if model_type == "text":
            return ["ollama", "openai"]
        elif model_type == "vision":
            return ["ollama", "openai"]
        elif model_type == "audio":
            return ["openai"]  # Only OpenAI supports audio
        else:
            return []

    def _get_models(self, provider: str, model_type: str) -> List[str]:
        """Get available models for a provider and type."""
        if provider == "openai":
            try:
                if not hasattr(self, '_openai_models'):
                    self._openai_models = self._get_openai_models()
                return self._openai_models.get(f"{model_type}_models", [])
            except Exception as e:
                logger.warning(f"Failed to get OpenAI models: {e}")
                return []
        elif provider == "ollama":
            try:
                if not hasattr(self, '_ollama_models'):
                    self._ollama_models = self._get_ollama_models()
                if model_type == "text":
                    return self._ollama_models.get("text_models", [])
                elif model_type == "vision":
                    return self._ollama_models.get("vision_models", [])
                elif model_type == "audio":
                    return self._ollama_models.get("audio_models", [])
                return []
            except Exception as e:
                logger.warning(f"Failed to get Ollama models: {e}")
                return []
        else:
            return []

    def _get_openai_models(self) -> Dict[str, List[str]]:
        """Get available OpenAI models using the API."""
        try:
            # Check if OpenAI API key is available
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OpenAI API key not found in environment")
                return {"text_models": [], "vision_models": [], "audio_models": []}

            import openai
            client = openai.OpenAI(api_key=api_key)
            models = client.models.list()

            # Get all models except special purpose ones
            all_models = []
            audio_models = []
            for model in models:
                model_id = model.id.lower()
                if not any(x in model_id for x in ["embedding", "moderation", "tts"]):
                    if "whisper" in model_id:
                        audio_models.append(model.id)
                    else:
                        all_models.append(model.id)
            
            # For backward compatibility, return all models as text models
            # Let the user choose which model to use for each purpose
            return {
                "text_models": all_models,
                "vision_models": all_models,
                "audio_models": audio_models
            }
        except Exception as e:
            logger.warning(f"Error fetching OpenAI models: {e}")
            return {"text_models": [], "vision_models": [], "audio_models": []}

    def _get_provider_model_count(self, provider: str, model_type: str) -> int:
        """Get number of models available for a provider and type."""
        if provider not in self.SUPPORTED_PROVIDERS:
            raise KeyError(f"Invalid provider: {provider}")
        return len(self._get_models(provider, model_type))

    def _configure_model(self, model_type: str, current_config: Optional[ModelConfig] = None) -> Optional[Dict]:
        """Configure a model interactively."""
        print(f"\nConfiguring {model_type} model:")

        # Get available providers
        providers = self._get_providers(model_type)
        if not providers:
            print(f"No providers available for {model_type} models")
            return None

        # Show provider options
        print("\nAvailable providers:")
        for idx, provider in enumerate(providers, 1):
            provider_info = self.SUPPORTED_PROVIDERS[provider]
            desc = provider_info.get("description", "")
            model_count = self._get_provider_model_count(provider, model_type)
            print(f"{idx}. {provider} ({model_count} models available) {desc}")

        # Get provider selection
        default_idx = None
        if current_config:
            try:
                default_idx = providers.index(current_config.provider) + 1
            except ValueError:
                pass

        provider_idx = None
        while provider_idx is None:
            prompt = f"\nSelect provider (number) [{default_idx}]: " if default_idx else "\nSelect provider (number): "
            choice = input(prompt).strip()
            
            # Use default if empty and default exists
            if not choice and default_idx:
                provider_idx = default_idx
                continue
                
            # Validate input
            try:
                idx = int(choice)
                if 1 <= idx <= len(providers):
                    provider_idx = idx
                else:
                    print(f"Please enter a number between 1 and {len(providers)}")
            except ValueError:
                print("Please enter a valid number")

        provider = providers[provider_idx - 1]
        provider_info = self.SUPPORTED_PROVIDERS[provider]

        # Check for required environment variables
        if env_var := provider_info.get("env_var"):
            if not os.getenv(env_var):
                print(f"\nWarning: {env_var} environment variable not set")
                print(f"Please set {env_var} to use {provider}")
                return None

        # Get endpoint if required
        endpoint = None
        if provider_info.get("endpoint_required"):
            default_endpoint = provider_info.get("default_endpoint", "")
            endpoint = input(f"\nEnter {provider} endpoint [{default_endpoint}]: ").strip() or default_endpoint

        # Get available models
        models = self._get_models(provider, model_type)
        if not models:
            print(f"\nNo {model_type} models available for {provider}")
            if provider == "openai":
                print("Please check your OPENAI_API_KEY and try again")
            return None

        # Show model options
        print("\nAvailable models:")
        for idx, model in enumerate(models, 1):
            print(f"{idx}. {model}")

        # Get model selection
        default_idx = None
        if current_config and current_config.provider == provider:
            try:
                default_idx = models.index(current_config.model_name) + 1
            except ValueError:
                pass

        model_idx = None
        while model_idx is None:
            prompt = f"\nSelect model (number) [{default_idx}]: " if default_idx else "\nSelect model (number): "
            choice = input(prompt).strip()
            
            # Use default if empty and default exists
            if not choice and default_idx:
                model_idx = default_idx
                continue
                
            # Validate input
            try:
                idx = int(choice)
                if 1 <= idx <= len(models):
                    model_idx = idx
                else:
                    print(f"Please enter a number between 1 and {len(models)}")
            except ValueError:
                print("Please enter a valid number")

        return {
            "provider": provider,
            "model_name": models[model_idx - 1],
            "endpoint": endpoint
        }
    
    def configure(self):
        """Configure settings interactively."""
        print("\nConfiguring Aigrok settings...")
        
        # Create default config if none exists
        if not self.config:
            self.config = AigrokConfig(
                ocr_enabled=False,
                ocr_languages=['en'],
                ocr_fallback=False,
                text_model=ModelConfig(
                    provider='ollama',
                    model_name='llama3.2:3b',
                    endpoint='http://localhost:11434'
                ),
                vision_model=ModelConfig(
                    provider='ollama',
                    model_name='llama3.2-vision:11b',
                    endpoint='http://localhost:11434'
                )
            )
            self.save_config()
            print("\nCreated default configuration with OCR disabled and default Ollama models.")
            return
            
        # Initialize empty config
        config_dict = {}
        
        # Configure text model
        print("\n=== Text Model Configuration ===")
        print("This model will be used for general text processing and analysis.\n")
        current_text_model = self.config.text_model if self.config else None
        text_model = self._configure_model("text", current_text_model)
        if text_model:
            config_dict["text_model"] = ModelConfig(**text_model)
        
        # Configure vision model
        print("\n=== Vision Model Configuration ===")
        print("This model will be used for processing images and PDFs with visual content.\n")
        current_vision_model = self.config.vision_model if self.config else None
        vision_model = self._configure_model("vision", current_vision_model)
        if vision_model:
            config_dict["vision_model"] = ModelConfig(**vision_model)
        
        # Configure audio model (optional)
        print("\n=== Audio Model Configuration ===")
        print("This model will be used for transcribing audio content.\n")
        current_audio_model = self.config.audio_model if self.config else None
        audio_model = self._configure_model("audio", current_audio_model)
        if audio_model:
            config_dict["audio_model"] = ModelConfig(**audio_model)
        
        # Configure OCR settings
        current_ocr_enabled = self.config.ocr_enabled if self.config else False
        enable_ocr = input(f"\nEnable OCR support? (y/N) [{current_ocr_enabled and 'y' or 'N'}]: ").strip().lower()
        if enable_ocr == 'y' or (not enable_ocr and current_ocr_enabled):
            config_dict["ocr_enabled"] = True
            
            current_languages = self.config.ocr_languages if self.config else ["en"]
            default_languages = ",".join(current_languages)
            languages = input(f"\nEnter OCR languages (comma-separated) [{default_languages}]: ").strip()
            if languages:
                config_dict["ocr_languages"] = [lang.strip() for lang in languages.split(',')]
            else:
                config_dict["ocr_languages"] = current_languages
                
            current_fallback = self.config.ocr_fallback if self.config else False
            fallback = input(f"\nEnable OCR fallback? (y/N) [{current_fallback and 'y' or 'N'}]: ").strip().lower()
            config_dict["ocr_fallback"] = fallback == 'y' or (not fallback and current_fallback)
            
            current_threshold = self.config.ocr_confidence_threshold if self.config else 0.5
            threshold = input(f"\nEnter OCR confidence threshold (0.0-1.0) [{current_threshold}]: ").strip()
            if threshold:
                config_dict["ocr_confidence_threshold"] = float(threshold)
            else:
                config_dict["ocr_confidence_threshold"] = current_threshold
        
        # Create and validate config
        try:
            self.config = AigrokConfig(**config_dict)
            self.save_config()
            print("\nConfiguration saved successfully!")
            
            # Print summary
            print("\nConfiguration Summary:")
            print(f"- Text: {self.config.text_model.provider} / {self.config.text_model.model_name}")
            print(f"- Vision: {self.config.vision_model.provider} / {self.config.vision_model.model_name}")
            if self.config.audio_model:
                print(f"- Audio: {self.config.audio_model.provider} / {self.config.audio_model.model_name}")
            if self.config.ocr_enabled:
                print(f"- OCR: enabled={self.config.ocr_enabled}, languages={self.config.ocr_languages}, fallback={self.config.ocr_fallback}, confidence_threshold={self.config.ocr_confidence_threshold}")
        except Exception as e:
            print(f"\nError saving configuration: {e}")
            raise

    def save_config(self):
        """Save configuration to file."""
        if not self.config:
            return

        # Ensure directory exists
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict
        config_dict = self.config.model_dump()
        
        # Write config
        with open(self.CONFIG_FILE, 'w') as f:
            yaml.dump(config_dict, f)

    def _get_ollama_models(self) -> Dict[str, List[str]]:
        """Get available Ollama models."""
        try:
            # Try to connect to Ollama server
            client = ollama.Client(host=self.SUPPORTED_PROVIDERS["ollama"]["default_endpoint"])
            models = client.list()
            
            text_models = []
            vision_models = []
            
            if isinstance(models, dict) and 'models' in models:
                for model in models['models']:
                    name = model.get('name', '')
                    if name:
                        # Simple classification based on model name
                        if any(x in name.lower() for x in ['vision', 'clip', 'image']):
                            vision_models.append(name)
                        else:
                            text_models.append(name)
            
            if not text_models and not vision_models:
                logger.warning("No models found in Ollama response")
                
            return {
                "text_models": text_models,
                "vision_models": vision_models,
                "audio_models": []
            }
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {e}")
            return {
                "text_models": [],
                "vision_models": [],
                "audio_models": []
            }
