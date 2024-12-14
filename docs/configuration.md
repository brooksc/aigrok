# Configuration Guide

This guide covers all configuration options available in AIGrok and how to use them effectively.

## Configuration File Location

The default configuration file is located at:
- Unix/Linux/macOS: `~/.config/aigrok/config.yaml`
- Windows: `%APPDATA%\aigrok\config.yaml`

## Configuration Format

AIGrok uses YAML for configuration. Here's a complete example with all available options:

```yaml
# Model Configuration
model:
  default: "llama2-vision"  # Default model to use
  fallback: "gpt-4-vision"  # Fallback model if default fails
  timeout: 30              # Model response timeout in seconds
  max_retries: 3          # Number of retries for failed requests
  
# Processing Options
processing:
  cache: true             # Enable result caching
  cache_ttl: 3600        # Cache TTL in seconds
  format: "text"         # Default output format
  batch_size: 10         # Batch processing size
  low_memory: false      # Enable low memory mode
  
# Logging Configuration
logging:
  level: "info"          # Logging level (debug/info/warn/error)
  file: "~/.local/share/aigrok/aigrok.log"  # Log file location
  max_size: "10MB"       # Maximum log file size
  backup_count: 5        # Number of backup logs to keep
  
# API Configuration
api:
  base_url: "http://localhost:11434"  # Ollama API base URL
  timeout: 30                         # API request timeout
  retry_delay: 1                      # Delay between retries
  max_concurrent: 5                   # Max concurrent requests
  
# Cache Configuration
cache:
  directory: "~/.cache/aigrok"  # Cache directory location
  max_size: "1GB"              # Maximum cache size
  cleanup_interval: 3600       # Cache cleanup interval
  
# Output Configuration
output:
  format: "text"              # Default output format
  colors: true               # Enable colored output
  progress_bar: true        # Show progress bar
  quiet: false              # Suppress non-error output
```

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
export AIGROK_MODEL="llama2-vision"
export AIGROK_CACHE_ENABLED="true"
export AIGROK_LOG_LEVEL="debug"
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
model:
  default: "llama2-vision"
  fallback: "gpt-4-vision"
  timeout: 30
  max_retries: 3
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
| `AIGROK_MODEL` | Default model | `llama2-vision` |
| `AIGROK_CACHE_ENABLED` | Enable caching | `true` |
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