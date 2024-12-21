# Configuration Guide

This guide covers all configuration options available in AIGrok and how to use them effectively.

## Interactive Configuration

The easiest way to configure AIGrok is using the interactive configuration wizard:

```bash
aigrok configure
```

This will guide you through setting up:
- Model providers and endpoints
- OCR settings and languages
- Output formats and logging
- Cache and performance settings

## Configuration File Location

The default configuration file is located at:
- Unix/Linux/macOS: `~/.config/aigrok/config.yaml`
- Windows: `%APPDATA%\aigrok\config.yaml`

## Configuration Format

AIGrok uses YAML for configuration. Here's a complete example with all available options:

```yaml
# Model Configuration
models:
  text_model:
    provider: "openai"           # Model provider (openai, ollama)
    model_name: "gpt-4"         # Model to use
    endpoint: null              # Optional provider endpoint
    timeout: 30                 # Model response timeout in seconds
    
  vision_model:
    provider: "openai"           # Vision model provider
    model_name: "gpt-4-vision-preview"  # Vision model to use
    endpoint: null              # Optional provider endpoint
    timeout: 60                 # Vision model timeout in seconds

# OCR Configuration
ocr:
  enabled: true                # Enable OCR processing
  languages: ["en"]            # List of language codes
  fallback: true              # Continue if OCR fails
  confidence_threshold: 0.8    # Minimum confidence score
  
# Processing Options
processing:
  cache_enabled: true          # Enable result caching
  cache_ttl: 3600             # Cache TTL in seconds
  max_retries: 3              # Max retries on failure
  batch_size: 10              # Batch size for processing
  timeout: 300                # Global timeout in seconds

# Output Options
output:
  format: "text"              # Default output format (text, json, markdown)
  include_metadata: true      # Include processing metadata
  pretty_print: true          # Pretty print JSON output
  max_tokens: 4096           # Max output tokens

# Logging
logging:
  level: "INFO"               # Logging level
  file: "aigrok.log"         # Log file location
  rotation: "1 week"         # Log rotation period
  retention: "1 month"       # Log retention period
  format: "{time} {level} {message}"  # Log format
```

## Environment Variables

AIGrok supports the following environment variables:

- `OPENAI_API_KEY`: OpenAI API key
- `OLLAMA_HOST`: Ollama host address (default: http://localhost:11434)
- `AIGROK_CONFIG`: Custom config file location
- `AIGROK_CACHE_DIR`: Custom cache directory
- `AIGROK_LOG_LEVEL`: Override logging level
- `AIGROK_VERBOSE`: Enable verbose logging (set to "1")

## Provider Configuration

### OpenAI

1. Set your API key:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

2. Available models will be automatically discovered and filtered by capability (text/vision).

### Ollama

1. Install Ollama from https://ollama.ai

2. Start the Ollama service:
   ```bash
   ollama serve
   ```

3. Pull required models:
   ```bash
   ollama pull llama2
   ollama pull llama2-vision
   ```

4. Optional: Set custom endpoint:
   ```bash
   export OLLAMA_HOST="http://custom-host:11434"
   ```

## Advanced Configuration

### Custom Model Selection

You can specify different models for different tasks:

```python
from aigrok import process_document

# Use GPT-4 for text analysis
result = process_document("doc.txt", provider="openai", model="gpt-4")

# Use GPT-4 Vision for image analysis
result = process_document("doc.pdf", provider="openai", model="gpt-4-vision-preview")

# Use Ollama for local processing
result = process_document("doc.pdf", provider="ollama", model="llama2-vision")
```

### Structured Output

Configure JSON schema for structured output:

```python
schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "topics": {"type": "array", "items": {"type": "string"}}
    }
}

result = process_document("doc.pdf", format="json", schema=schema)
```

### Logging Configuration

Configure detailed logging:

```python
import logging
from aigrok.logging import configure_logging

# Enable debug logging
configure_logging(level="DEBUG", file="aigrok.log")

# Enable verbose mode for specific operations
result = process_document("doc.pdf", verbose=True)
```

## Validation

To validate your configuration:

```bash
aigrok configure --validate
```

This will check:
- Required fields are present
- Values are of correct type
- Endpoints are accessible
- API keys are valid
- Models are available

## Configuration Methods

### 1. Using Configuration File

Create or edit the configuration file:

```bash
# Create default config
aigrok config init

# Edit config
aigrok config edit
```

### 2. Using Environment Variables

Environment variables override file configuration:

```bash
export AIGROK_MODELS_TEXT_MODEL_PROVIDER="openai"
export AIGROK_OCR_ENABLED="true"
export AIGROK_LOGGING_LEVEL="debug"
```

### 3. Using Command Line Options

Command line options override both file and environment configurations:

```bash
aigrok process --model llama2-vision --no-cache document.pdf
```

## Configuration Sections

### Model Configuration

Controls AI model behavior:

```yaml
models:
  text_model:
    provider: "openai"
    model_name: "gpt-4"
    endpoint: null
    timeout: 30
    
  vision_model:
    provider: "openai"
    model_name: "gpt-4-vision-preview"
    endpoint: null
    timeout: 60
```

### Processing Configuration

Controls document processing:

```yaml
processing:
  cache_enabled: true
  format: "text"
  batch_size: 10
```

### Logging Configuration

Controls logging behavior:

```yaml
logging:
  level: "INFO"
  file: "aigrok.log"
  max_size: "10MB"
```

## Best Practices

1. **Version Control**
   - Keep configuration in version control
   - Use environment-specific config files
   - Document configuration changes

2. **Security**
   - Don't store sensitive data in config files
   - Use environment variables for secrets
   - Set appropriate file permissions

3. **Performance**
   - Enable caching for better performance
   - Configure appropriate timeouts
   - Use batch processing for multiple files

4. **Troubleshooting**
   - Enable debug logging when needed
   - Monitor cache usage
   - Check log files for issues