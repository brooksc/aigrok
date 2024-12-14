# Quick Start Guide

Get up and running with AIGrok in minutes.

## Installation

1. Install AIGrok:

   ```bash
   pip install aigrok
   ```

2. Install Ollama:
   - Visit [Ollama's website](https://ollama.ai)
   - Follow installation instructions for your platform

3. Pull required model:

   ```bash
   ollama pull llama2-vision
   ```

## Basic Usage

### 1. Process a Document

```bash
# Basic document processing
aigrok process document.pdf

# Process with custom prompt
aigrok process --prompt "Extract main topics" document.pdf

# Save output to file
aigrok process document.pdf --output results.txt
```

### 2. Configure AIGrok

```bash
# Create default configuration
aigrok config init

# Set preferred model
aigrok config set model.default llama2-vision

# Enable caching
aigrok config set processing.cache true
```

### 3. Batch Processing

```bash
# Process multiple files
aigrok process *.pdf --output-dir results/

# Process with specific format
aigrok process documents/*.pdf --format json
```

## Common Commands

### Document Processing

```bash
# Extract text
aigrok process document.pdf

# Analyze content
aigrok process --prompt "Summarize this" document.pdf

# Extract specific information
aigrok process --prompt "List all authors" paper.pdf
```

### Cache Management

```bash
# Clear cache
aigrok cache clear

# List cached results
aigrok cache list

# Export cache
aigrok cache export backup.json
```

### Configuration

```bash
# Show current config
aigrok config show

# Edit config
aigrok config edit

# Reset config
aigrok config reset
```

## Next Steps

1. Read the [CLI Reference](cli.md) for detailed command usage
2. Check [Configuration Guide](configuration.md) for advanced settings
3. Visit [API Documentation](api.md) for programmatic usage
4. Review [Troubleshooting Guide](troubleshooting.md) if you encounter issues

## Examples

### 1. Basic Text Extraction

```bash
aigrok process document.pdf --format text
```

### 2. JSON Output

```bash
aigrok process --format json document.pdf > data.json
```

### 3. Custom Analysis

```bash
aigrok process --prompt "Extract and list all citations" paper.pdf
```

### 4. Batch Processing with Progress

```bash
aigrok process --progress documents/*.pdf --output-dir analyzed/
```

## Tips

1. **Performance**
   - Enable caching for repeated processing
   - Use batch processing for multiple files
   - Configure appropriate timeouts

2. **Output Formats**
   - Use `--format text` for plain text
   - Use `--format json` for structured data
   - Use `--format markdown` for formatted output

3. **Resource Usage**
   - Enable low memory mode if needed
   - Monitor cache size
   - Use appropriate batch sizes

## Common Issues

1. **Model Not Found**

   ```bash
   # Fix by pulling the model
   ollama pull llama2-vision
   ```

2. **Connection Issues**

   ```bash
   # Check Ollama service
   ollama serve
   ```

3. **Permission Errors**

   ```bash
   # Check file permissions
   chmod 644 document.pdf
   ```

## Getting Help

- Run `aigrok --help` for command help
- Check [Documentation](README.md) for guides
- Visit [GitHub Issues](https://github.com/yourusername/aigrok/issues) for support
