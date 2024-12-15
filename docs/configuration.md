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
    provider: "ollama"          # Model provider (ollama, openai, anthropic)
    model_name: "llama2"        # Model to use
    endpoint: "localhost:11434" # Provider endpoint
    timeout: 30                # Model response timeout in seconds
    
  vision_model:
    provider: "ollama"          # Vision model provider
    model_name: "llama2-vision" # Vision model to use
    endpoint: "localhost:11434" # Provider endpoint
    timeout: 60                # Vision model timeout in seconds

# OCR Configuration
ocr:
  enabled: true                # Enable OCR processing
  languages: ["en"]           # List of language codes
  fallback: true              # Continue if OCR fails
  confidence_threshold: 0.8   # Minimum confidence score
  
# Processing Options
processing:
  cache: true                 # Enable result caching
  cache_ttl: 3600            # Cache TTL in seconds
  format: "text"             # Default output format
  batch_size: 10             # Batch processing size
  low_memory: false          # Enable low memory mode
  
# Logging Configuration
logging:
  level: "info"              # Logging level (debug/info/warn/error)
  file: "~/.local/share/aigrok/aigrok.log"  # Log file location
  max_size: "10MB"           # Maximum log file size
  backup_count: 5            # Number of backup logs to keep
  
# API Configuration
api:
  base_url: "http://localhost:11434"  # Default API base URL
  timeout: 30                         # API request timeout
  retry_delay: 1                      # Delay between retries
  max_concurrent: 5                   # Max concurrent requests
  
# Cache Configuration
cache:
  directory: "~/.cache/aigrok"  # Cache directory location
  max_size: "1GB"              # Maximum cache size
  cleanup_interval: 3600       # Cache cleanup interval
```

## Environment Variables

Configuration values can also be set via environment variables. The format is `AIGROK_SECTION_KEY`. For example:

- `AIGROK_MODELS_TEXT_MODEL_PROVIDER=ollama`
- `AIGROK_OCR_ENABLED=true`
- `AIGROK_LOGGING_LEVEL=debug`

Environment variables take precedence over configuration file values.

## Provider-Specific Configuration

### Ollama Configuration
```yaml
models:
  text_model:
    provider: "ollama"
    model_name: "llama2"
    endpoint: "localhost:11434"
    timeout: 30
    context_window: 4096
    temperature: 0.7
    
  vision_model:
    provider: "ollama"
    model_name: "llama2-vision"
    endpoint: "localhost:11434"
    timeout: 60
    max_tokens: 1024
    temperature: 0.7
```

### OpenAI Configuration
```yaml
models:
  text_model:
    provider: "openai"
    model_name: "gpt-4"
    api_key: "${OPENAI_API_KEY}"  # Use environment variable
    timeout: 30
    
  vision_model:
    provider: "openai"
    model_name: "gpt-4-vision-preview"
    api_key: "${OPENAI_API_KEY}"
    timeout: 60
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
export AIGROK_MODELS_TEXT_MODEL_PROVIDER="ollama"
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
    provider: "ollama"
    model_name: "llama2"
    endpoint: "localhost:11434"
    timeout: 30
    
  vision_model:
    provider: "ollama"
    model_name: "llama2-vision"
    endpoint: "localhost:11434"
    timeout: 60
```

### Processing Configuration

Controls document processing:

```yaml
processing:
  cache: true
  format: "text"
  batch_size: 10
```

### Logging Configuration

Controls logging behavior:

```yaml
logging:
  level: "info"
  file: "aigrok.log"
  max_size: "10MB"
```

## Advanced Configuration

### Custom Model Configuration

Configure specific models:

```yaml
models:
  llama2-vision:
    temperature: 0.7
    max_tokens: 2000
    context_window: 4096
    
  gpt-4-vision:
    temperature: 0.5
    max_tokens: 1000
    context_window: 8192
```

### Cache Configuration

Configure caching behavior:

```yaml
cache:
  directory: "~/.cache/aigrok"
  max_size: "1GB"
  cleanup_interval: 3600
  
  strategies:
    pdf_cache:
      ttl: 86400
      max_entries: 1000
    
    image_cache:
      ttl: 3600
      max_entries: 500
```

## Environment Variables Reference

Complete list of supported environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AIGROK_CONFIG` | Config file path | `~/.config/aigrok/config.yaml` |
| `AIGROK_MODELS_TEXT_MODEL_PROVIDER` | Text model provider | `ollama` |
| `AIGROK_MODELS_VISION_MODEL_PROVIDER` | Vision model provider | `ollama` |
| `AIGROK_OCR_ENABLED` | Enable OCR processing | `true` |
| `AIGROK_CACHE_DIR` | Cache directory | `~/.cache/aigrok` |
| `AIGROK_LOG_LEVEL` | Log level | `info` |
| `AIGROK_LOG_FILE` | Log file path | `aigrok.log` |
| `AIGROK_API_URL` | API base URL | `http://localhost:11434` |
| `AIGROK_API_TIMEOUT` | API timeout | `30` |
| `AIGROK_OUTPUT_FORMAT` | Output format | `text` |

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