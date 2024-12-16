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
    ocr_enabled: bool = False
    ocr_languages: List[str] = Field(default_factory=lambda: ["en"])
    ocr_fallback: bool = False
    
    class Config:
        extra = "allow"

class ConfigManager:
    """Configuration manager."""
    CONFIG_DIR = Path.home() / ".config" / "aigrok"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"
    
    SUPPORTED_PROVIDERS = {
        "ollama": {
            "text_models": [],  # Dynamic
            "vision_models": ["llama3.2-vision:11b"],
            "audio_models": []
        },
        "openai": {
            "text_models": ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
            "vision_models": ["gpt-4-vision-preview"],
            "audio_models": ["whisper-1"]
        },
        "anthropic": {
            "env_var": "ANTHROPIC_API_KEY",
            "text_models": ["claude-2.1", "claude-instant-1.2"],
            "vision_models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
            "audio_models": []
        },
        "anyscale": {
            "env_var": "ANYSCALE_API_KEY",
            "text_models": ["mistral-7b-instruct", "mixtral-8x7b-instruct"],
            "vision_models": [],
            "audio_models": []
        },
        "azure": {
            "env_var": "AZURE_API_KEY",
            "text_models": ["gpt-35-turbo", "gpt-4", "gpt-4-turbo"],
            "vision_models": ["gpt-4-vision"],
            "audio_models": []
        },
        "bedrock": {
            "env_var": "AWS_ACCESS_KEY_ID",  # Also needs AWS_SECRET_ACCESS_KEY
            "text_models": ["anthropic.claude-v2", "amazon.titan-text-express-v1"],
            "vision_models": ["anthropic.claude-3-sonnet-20240229-v1:0"],
            "audio_models": []
        },
        "cerebras": {
            "env_var": "CEREBRAS_API_KEY",
            "text_models": ["cerebras/btlm-3b-8k", "cerebras/btlm-7b-8k"],
            "vision_models": [],
            "audio_models": []
        },
        "cloudflare": {
            "env_var": "CLOUDFLARE_API_KEY",
            "text_models": ["@cf/meta/llama-2-7b", "@cf/mistral/mistral-7b-instruct"],
            "vision_models": [],
            "audio_models": []
        },
        "codestral": {
            "env_var": "CODESTRAL_API_KEY",
            "text_models": ["codestral-7b", "codestral-7b-instruct"],
            "vision_models": [],
            "audio_models": []
        },
        "cohere": {
            "env_var": "COHERE_API_KEY",
            "text_models": ["command", "command-light", "command-nightly"],
            "vision_models": [],
            "audio_models": []
        },
        "databricks": {
            "env_var": "DATABRICKS_API_KEY",
            "text_models": ["dolly-v2", "mpt-7b-instruct"],
            "vision_models": [],
            "audio_models": []
        },
        "deepinfra": {
            "env_var": "DEEPINFRA_API_KEY",
            "text_models": ["meta-llama/Llama-2-70b-chat", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
            "vision_models": [],
            "audio_models": []
        },
        "deepseek": {
            "env_var": "DEEPSEEK_API_KEY",
            "text_models": ["deepseek-coder", "deepseek-chat"],
            "vision_models": [],
            "audio_models": []
        },
        "fireworks_ai": {
            "env_var": "FIREWORKS_API_KEY",
            "text_models": ["llama-v2-7b", "mixtral-8x7b"],
            "vision_models": [],
            "audio_models": []
        },
        "gemini": {
            "env_var": "GOOGLE_API_KEY",
            "text_models": ["gemini-pro"],
            "vision_models": ["gemini-pro-vision"],
            "audio_models": []
        },
        "groq": {
            "env_var": "GROQ_API_KEY",
            "text_models": ["mixtral-8x7b-32768", "llama2-70b-4096"],
            "vision_models": [],
            "audio_models": []
        },
        "mistral": {
            "env_var": "MISTRAL_API_KEY",
            "text_models": ["mistral-tiny", "mistral-small", "mistral-medium"],
            "vision_models": [],
            "audio_models": []
        },
        "openrouter": {
            "env_var": "OPENROUTER_API_KEY",
            "text_models": ["openrouter/auto", "anthropic/claude-2.1"],
            "vision_models": [],
            "audio_models": []
        },
        "palm": {
            "env_var": "PALM_API_KEY",
            "text_models": ["palm-2"],
            "vision_models": [],
            "audio_models": []
        },
        "perplexity": {
            "env_var": "PERPLEXITY_API_KEY",
            "text_models": ["pplx-7b-online", "pplx-70b-online"],
            "vision_models": [],
            "audio_models": []
        },
        "replicate": {
            "env_var": "REPLICATE_API_TOKEN",
            "text_models": ["llama-2-70b-chat", "mixtral-8x7b-instruct-v0.1"],
            "vision_models": ["llava-13b"],
            "audio_models": []
        },
        "sagemaker": {
            "env_var": "AWS_ACCESS_KEY_ID",  # Also needs AWS_SECRET_ACCESS_KEY
            "text_models": ["sagemaker-llama-2-70b", "sagemaker-mixtral-8x7b"],
            "vision_models": [],
            "audio_models": []
        },
        "together_ai": {
            "env_var": "TOGETHER_API_KEY",
            "text_models": ["togethercomputer/llama-2-70b", "togethercomputer/falcon-40b"],
            "vision_models": [],
            "audio_models": []
        },
        "voyage": {
            "env_var": "VOYAGE_API_KEY",
            "text_models": ["voyage-01", "voyage-lite-01"],
            "vision_models": [],
            "audio_models": []
        },
        "xai": {
            "env_var": "XAI_API_KEY",
            "text_models": ["xai-large", "xai-medium"],
            "vision_models": [],
            "audio_models": []
        }
    }
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config = None
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file."""
        if not self.CONFIG_FILE.exists():
            return
            
        try:
            with open(self.CONFIG_FILE) as f:
                config_dict = yaml.safe_load(f)
                
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
                    if 'api_base' in model:
                        model['endpoint'] = model.pop('api_base')
                    if 'api_key' in model:
                        model.pop('api_key')
            
            self.config = AigrokConfig(**config_dict)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = None
    
    def _get_providers(self, model_type: str) -> List[str]:
        """Get list of providers that support a specific model type."""
        return [
            provider for provider, config in self.SUPPORTED_PROVIDERS.items()
            if config[f"{model_type}_models"] or provider == "ollama"
        ]
    
    def _get_models(self, provider: str, model_type: str) -> List[str]:
        """Get list of models for a provider and type."""
        try:
            if provider == "ollama":
                models = self._get_ollama_models()
                return models[f"{model_type}_models"]
            else:
                return self.SUPPORTED_PROVIDERS[provider][f"{model_type}_models"]
        except Exception as e:
            logger.error(f"Failed to get {model_type} models for {provider}: {e}")
            return []
    
    def _get_provider_model_count(self, provider: str, model_type: str) -> str:
        """Get model count for a provider."""
        if provider == "ollama":
            return "dynamic models available"
        models = self.SUPPORTED_PROVIDERS[provider][f"{model_type}_models"]
        count = len(models)
        return f"{count} model{'s' if count != 1 else ''} available"

    def _configure_model(self, model_type: str, current_config: Optional[ModelConfig] = None) -> Optional[Dict[str, str]]:
        """Configure a model interactively."""
        print(f"Configuring {model_type} model:\n")
        
        # Show available providers
        providers = self._get_providers(model_type)
        print("Available providers:")
        default_idx = None
        if current_config:
            try:
                default_idx = providers.index(current_config.provider) + 1
            except ValueError:
                pass
        
        for i, provider in enumerate(providers, 1):
            default_marker = " [default]" if i == default_idx else ""
            model_count = self._get_provider_model_count(provider, model_type)
            print(f"{i}. {provider} ({model_count}){default_marker}")
        
        try:
            prompt = f"\nSelect provider (number) [{default_idx}]: " if default_idx else "\nSelect provider (number): "
            choice = input(prompt).strip()
            provider_idx = int(choice) if choice else default_idx
            if not provider_idx or provider_idx < 1 or provider_idx > len(providers):
                print("Invalid provider selection")
                return None
            
            provider_idx -= 1  # Convert to 0-based index
            provider = providers[provider_idx]
            
            # Handle Ollama endpoint
            endpoint = None
            if provider == "ollama":
                default_endpoint = current_config.endpoint if current_config and current_config.provider == "ollama" else "http://localhost:11434"
                endpoint = input(f"\nEnter Ollama endpoint [{default_endpoint}]: ").strip()
                if not endpoint:
                    endpoint = default_endpoint
                    
                # Test Ollama connection
                try:
                    os.environ["OLLAMA_HOST"] = endpoint
                    models = self._get_ollama_models()
                    if not models[f"{model_type}_models"]:
                        print(f"No {model_type} models found at {endpoint}")
                        return None
                except Exception as e:
                    print(f"Failed to connect to Ollama at {endpoint}: {e}")
                    return None
            
            # Get available models
            models = self._get_models(provider, model_type)
            if not models:
                print(f"No {model_type} models available for {provider}")
                return None
                
            print("\nAvailable models:")
            default_idx = None
            if current_config and current_config.provider == provider:
                try:
                    default_idx = models.index(current_config.model_name) + 1
                except ValueError:
                    pass
            
            for i, model in enumerate(models, 1):
                default_marker = " [default]" if i == default_idx else ""
                print(f"{i}. {model}{default_marker}")
            
            prompt = f"\nSelect model (number) [{default_idx}]: " if default_idx else "\nSelect model (number): "
            choice = input(prompt).strip()
            model_idx = int(choice) if choice else default_idx
            if not model_idx or model_idx < 1 or model_idx > len(models):
                print("Invalid model selection")
                return None
            
            model_idx -= 1  # Convert to 0-based index
            model = models[model_idx]
            
            return {
                "provider": provider,
                "model_name": model,
                "endpoint": endpoint
            }
            
        except (ValueError, IndexError):
            print("Invalid selection")
            return None

    def _get_ollama_models(self) -> Dict[str, List[str]]:
        """Get available Ollama models."""
        try:
            # List all models
            models = ollama.list()
            
            # Categorize models
            text_models = []
            vision_models = []
            audio_models = []
            
            for model in models['models']:
                name = model['name']
                # Vision models typically have 'vision' in their name
                if 'vision' in name.lower():
                    vision_models.append(name)
                # Currently no audio models in Ollama
                else:
                    text_models.append(name)
            
            return {
                "text_models": text_models,
                "vision_models": vision_models,
                "audio_models": audio_models
            }
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {e}")
            return {"text_models": [], "vision_models": [], "audio_models": []}

    def configure(self):
        """Configure settings interactively."""
        print("\nConfiguring Aigrok settings...")
        
        # Create default config if none exists
        if not self.config:
            self.config = AigrokConfig(
                ocr_enabled=True,
                ocr_languages=['en'],
                ocr_fallback=False,
                text_model=ModelConfig(
                    provider='ollama',
                    model_name='mistral',
                    endpoint='http://localhost:11434'
                )
            )
            self.save_config()
            print("\nCreated default configuration with OCR enabled.")
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
                print(f"- OCR: enabled={self.config.ocr_enabled}, languages={self.config.ocr_languages}, fallback={self.config.ocr_fallback}")
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
