# Command Line Interface

AIGrok provides a powerful command-line interface for processing and analyzing documents. This guide covers all available commands, options, and usage examples.

## Basic Usage

The basic syntax for AIGrok commands is:

```bash
aigrok [OPTIONS] COMMAND [ARGS]
```

## Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config FILE` | Path to config file | `~/.config/aigrok/config.yaml` |
| `--verbose` | Enable verbose output | `false` |
| `--quiet` | Suppress all output except errors | `false` |
| `--log-level LEVEL` | Set logging level (debug/info/warn/error) | `info` |
| `--version` | Show version information | - |
| `--help` | Show help message | - |
| `--configure` | Run interactive configuration wizard | - |

## Commands

### process

Process one or more documents with AI analysis.

```bash
aigrok process [OPTIONS] [FILES...]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--model NAME` | AI model to use | `gpt-4-vision` |
| `--prompt TEXT` | Custom processing prompt | - |
| `--format FORMAT` | Output format (text/json/markdown) | `text` |
| `--output FILE` | Output file path | stdout |
| `--cache` | Enable result caching | `false` |
| `--timeout SECONDS` | Processing timeout | `30` |
| `--easyocr` | Enable OCR processing of images in PDFs | `false` |
| `--ocr-languages LANGS` | Comma-separated list of OCR languages | `en` |
| `--ocr-fallback` | Continue processing if OCR fails | `false` |

#### Examples

```bash
# Basic document processing
aigrok process document.pdf

# Process multiple documents
aigrok process doc1.pdf doc2.pdf doc3.pdf

# Custom prompt with specific model
aigrok process --model llama2-vision --prompt "Summarize this document" document.pdf

# Enable OCR with multiple languages
aigrok process --easyocr --ocr-languages "en,fr,de" document.pdf

# Process with OCR fallback
aigrok process --easyocr --ocr-fallback document.pdf
```

### validate

Validate document format and compatibility.

```bash
aigrok validate [OPTIONS] FILE
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--strict` | Enable strict validation | `false` |
| `--report` | Generate validation report | `false` |

#### Examples

```bash
# Basic validation
aigrok validate document.pdf

# Strict validation with report
aigrok validate --strict --report document.pdf
```

### cache

Manage the processing cache.

```bash
aigrok cache COMMAND [OPTIONS]
```

#### Subcommands

- `list`: List cached results
- `clear`: Clear the cache
- `info`: Show cache information
- `export`: Export cache to file

#### Examples

```bash
# List cached results
aigrok cache list

# Clear entire cache
aigrok cache clear

# Export cache to file
aigrok cache export --output cache-backup.json
```

### config

Manage AIGrok configuration.

```bash
aigrok config COMMAND [OPTIONS]
```

#### Subcommands

- `show`: Show current configuration
- `set`: Set configuration value
- `reset`: Reset to default configuration

#### Examples

```bash
# Show current configuration
aigrok config show

# Set model preference
aigrok config set model.default gpt-4-vision

# Reset configuration
aigrok config reset
```

### configure

Run the interactive configuration wizard.

```bash
aigrok configure [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--reset` | Reset configuration to defaults | `false` |
| `--show` | Show current configuration | `false` |
| `--validate` | Validate current configuration | `false` |

#### Examples

```bash
# Configure aigrok
aigrok configure

# Show current configuration
aigrok configure --show
```

## Environment Variables

AIGrok respects the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AIGROK_CONFIG` | Configuration file path | `~/.config/aigrok/config.yaml` |
| `AIGROK_MODEL` | Default model | `gpt-4-vision` |
| `AIGROK_CACHE_DIR` | Cache directory | `~/.cache/aigrok` |
| `AIGROK_LOG_LEVEL` | Logging level | `info` |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Configuration error |
| 4 | Processing error |
| 5 | Timeout error |

## Configuration File

The configuration file (default: `~/.config/aigrok/config.yaml`) can be used to set default values for all command-line options. Example:

```yaml
model:
  default: gpt-4-vision
  fallback: llama2-vision

processing:
  timeout: 30
  cache: true
  format: text

logging:
  level: info
  file: ~/.local/share/aigrok/aigrok.log
```

## Tips and Tricks

1. Use `--verbose` for debugging issues
2. Enable caching for faster repeated processing
3. Use environment variables in scripts
4. Create aliases for common commands

## Common Issues

1. **Timeout Errors**
   - Increase timeout with `--timeout`
   - Use a faster model
   - Check network connection

2. **Memory Issues**
   - Process smaller documents
   - Use `--low-memory` option
   - Clear cache regularly

3. **Model Errors**
   - Verify model availability
   - Check API credentials
   - Try fallback model

## See Also

- [API Documentation](api.md) for programmatic usage
- [Configuration Guide](configuration.md) for detailed config options
- [Troubleshooting Guide](troubleshooting.md) for common issues
