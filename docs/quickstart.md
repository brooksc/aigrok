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
   ollama pull llama3.2-vision:11b
   ```

## Basic Usage

### 1. Process a Document

```bash
# Basic document processing
aigrok "Analyze this document" document.pdf

# Process with specific query
aigrok "Extract main topics" document.pdf

# Save output to file
aigrok "Summarize this document" document.pdf -o results.txt

# Process with OCR enabled for scanned documents
aigrok "Extract text from scanned pages" document.pdf --easyocr
```

### 2. Configure AIGrok

```bash
# Configure the application
aigrok --configure

# Process with specific model
aigrok "Analyze this" document.pdf --model llama3.2-vision:11b

# Enable OCR with multiple languages
aigrok "Extract text" document.pdf --easyocr --ocr-languages "en,fr,de"
```

### 3. Output Formats

```bash
# Get JSON output
aigrok "Analyze this" document.pdf -f json

# Get Markdown output
aigrok "Analyze this" document.pdf -f markdown
```

## Additional Features

### OCR Support
- Use `--easyocr` to enable OCR for scanned documents
- Specify languages with `--ocr-languages` (e.g., 'en,fr,de')
- Enable fallback with `--ocr-fallback` to continue if OCR fails

### Model Selection
- Default model is Ollama's llama3.2-vision:11b
- Change model with `--model` flag
- Supports various Ollama models

## Planned Features

> Note: The following features are planned for future releases.

### Batch Processing

```bash
# Process multiple files
aigrok "Analyze these documents" *.pdf --output-dir results/

# Process with specific format
aigrok "Extract text" documents/*.pdf -f json
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

## Tips and Best Practices

1. **Performance**
   - Use appropriate models for your task
   - Enable OCR only when needed
   - Process files individually for best results

2. **Output Formats**
   - Use `--format text` for plain text
   - Use `--format json` for structured data
   - Use `--format markdown` for formatted output

3. **OCR Usage**
   - Enable for scanned documents
   - Specify correct languages
   - Use fallback for reliability

## Common Issues

1. **Model Not Found**

   ```bash
   # Fix by pulling the model
   ollama pull llama3.2-vision:11b
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
- Check [CLI Documentation](cli.md) for detailed options
- Visit [Configuration Guide](configuration.md) for setup help
