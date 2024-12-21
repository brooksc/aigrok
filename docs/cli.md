# Command Line Interface

AIGrok provides a powerful command-line interface for processing and analyzing documents. This guide covers all available commands, options, and usage examples.

## Basic Usage

The basic syntax for AIGrok commands is:

```bash
aigrok [options] PROMPT file ...
```

Where:
- `PROMPT` is the instruction for processing the documents (required)
- `file` is one or more files to process (required)

## Currently Implemented Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format, -f` | Output format (text/json/markdown) | `text` |
| `--configure` | Configure the application | - |
| `--model` | Model to use for analysis | `llama3.2-vision:11b` |
| `--output, -o` | Path to save output (defaults to stdout) | stdout |
| `--type` | Input file type (pdf/txt) | auto-detect |
| `--metadata-only` | Only extract document metadata | `false` |
| `--verbose, -v` | Enable verbose logging | `false` |
| `--version` | Show version information | - |
| `--help` | Show help message | - |

### OCR Options

| Option | Description | Default |
|--------|-------------|---------|
| `--easyocr` | Enable OCR for scanned documents | `false` |
| `--ocr-languages` | EasyOCR language codes (comma-separated) | `en` |
| `--ocr-fallback` | Continue if OCR fails | `false` |

## Examples

### Basic Usage

```bash
# Process a single document
aigrok "Analyze this document" document.pdf

# Process with specific model
aigrok "Extract text" document.pdf --model llama3.2-vision:11b

# Save output to file
aigrok "Summarize" document.pdf -o summary.txt
```

### OCR Processing

```bash
# Enable OCR for scanned documents
aigrok "Extract text" scan.pdf --easyocr

# OCR with multiple languages
aigrok "Extract text" scan.pdf --easyocr --ocr-languages "en,fr,de"

# OCR with fallback
aigrok "Extract text" scan.pdf --easyocr --ocr-fallback
```

### Output Formats

```bash
# Get plain text output (default)
aigrok "Analyze" doc.pdf

# Get text output with filenames
aigrok "Analyze" *.pdf --format text

# Get JSON output with metadata
aigrok "Analyze" doc.pdf --format json

# Get markdown formatted output
aigrok "Analyze" doc.pdf --format markdown

# Process multiple files with filename prefixes
aigrok "Analyze" *.pdf --format text --show-filenames
```

The output formats support the following features:
- `text`: Clean text output with optional filename prefixes
- `json`: Structured output with full metadata and processing results
- `markdown`: Rich text format with document sections and formatting

## Planned Features

> Note: The following features are planned for future releases.

### Batch Processing

```bash
# Process multiple files (planned)
aigrok "Analyze these documents" *.pdf -o results/

# Process with progress tracking (planned)
aigrok "Extract text" docs/*.pdf --progress
```

### Cache Management (Planned)

```bash
# Clear cache
aigrok cache clear

# List cached results
aigrok cache list

# Export cache
aigrok cache export backup.json
```

### Configuration Management (Planned)

```bash
# Show current config
aigrok config show

# Set configuration values
aigrok config set model.default llama3.2-vision:11b

# Reset to defaults
aigrok config reset
```

## Environment Variables (Planned)

| Variable | Description | Default |
|----------|-------------|---------|
| `AIGROK_CONFIG` | Configuration file path | `~/.config/aigrok/config.yaml` |
| `AIGROK_MODEL` | Default model | `llama3.2-vision:11b` |
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

## Configuration File Format (Planned)

The configuration file (default: `~/.config/aigrok/config.yaml`) will support:

```yaml
model:
  default: llama3.2-vision:11b
  fallback: llama2

processing:
  timeout: 30
  cache: true
  format: text

ocr:
  enabled: false
  languages: ["en"]
  fallback: true

logging:
  level: info
  file: ~/.local/share/aigrok/aigrok.log
```

## Common Issues

1. "Model not found":
   - Ensure Ollama is installed and running
   - Pull the required model: `ollama pull llama3.2-vision:11b`

2. "OCR initialization failed":
   - Install EasyOCR dependencies
   - Use `--ocr-fallback` for graceful degradation

3. "File not found":
   - Check file path and permissions
   - Ensure file exists and is readable

## Tips and Tricks

1. Use `--verbose` for debugging issues
2. Specify OCR languages for better accuracy
3. Use markdown output for formatted results
4. Enable OCR fallback for reliable processing

## See Also

- [Quickstart Guide](quickstart.md)
- [Configuration Guide](configuration.md)
- [API Documentation](api.md)
