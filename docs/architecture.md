# AIGrok Specification

## Current Implementation

### Core Features

1. File Format Support
   Currently supported formats:
   - [x] PDF (.pdf)
   - [x] Plain text (.txt)

   Format detection:
   - [x] Extension-based detection (required)
   - [ ] Content-based detection (planned)
   - [x] Type hints via `--type` flag:

     ```bash
     aigrok --type pdf 'extract title' file  # Override extension detection
     ```

   All other formats are rejected with:

   ```
   Error: Unsupported file format. Currently supported formats: .pdf, .txt
   ```

2. LLM Integration
   - [x] litellm integration for multi-provider support:
     - [x] OpenAI models (GPT-4, GPT-3.5)
     - [x] Anthropic models (Claude)
     - [x] Local models via Ollama
   - [x] Vision model support for PDF analysis
     - [x] Text extraction with fallback to OCR
     - [x] Mixed content handling (text + images)
   - [x] Configurable model selection
   - [x] Prompt-based information extraction
   - [x] Environment-based API key configuration

3. Output Formats
   - [x] Text: Simple text output
   - [x] JSON: Structured data output
     - [x] Author extraction with first/last name parsing
     - [x] Title extraction
     - [x] Metadata extraction
   - [x] CSV: Tabular data
     - [x] Author lists with headers
     - [x] Structured data export
   - [x] Markdown: Rich formatted output
     - [x] Document metadata sections
     - [x] Content sections
     - [x] Analysis results

### Command Line Interface

```bash
aigrok 'prompt' input [options]
```

Required Arguments:

- `prompt`: The prompt for LLM analysis
- `input`: Path to the input file

Options:

- [x] `--model`: model name (overrides defaults from configuration)
- [x] `--format`: Output format (text/json/csv/markdown)
- [x] `--output`: Output file path
- [x] `--metadata-only`: Extract only metadata
- [x] `--verbose`: Enable debug logging
- [ ] `--configure`: Interactive configuration (planned)
  - [ ] Configuration profiles
  - [ ] Default output formats
  - [ ] Model preferences

#### STDIN Handling

- [ ] Support for reading from stdin (planned)
  - [ ] Format handling:
    - [ ] Auto-detection from content (future enhancement)
    - [x] Optional `--type` flag to hint input format
    - [x] Proceed with best-effort detection if no type specified
  - [ ] Implementation details:
    - [ ] Buffer management for random access formats
    - [ ] Streaming support for text-based formats
  - Example usage:

    ```bash
    # With type hint
    cat document.pdf | aigrok --type pdf 'extract the title'
    
    # Without type hint (uses auto-detection)
    cat document.txt | aigrok 'summarize this'
    ```

- [x] Currently rejects stdin (temporary until implementation complete)

### Configuration

Configuration will be stored in `~/.config/aigrok/config.yaml`:

```yaml
models:
  text:
    default: "gpt-3.5-turbo"
    fallback: "ollama/llama2"
  vision:
    default: "gpt-4-vision"
    fallback: "claude-3-opus"

supported_formats:
  - ".pdf"
  - ".txt"
```

#### Multiple File Output

- [x] Text Format with filename prefixes
- [x] CSV Format with filename column
- [x] JSON Format with filename field
- [x] Markdown Format with filename headers

### Python API

- [x] Basic file processing API
  - [x] Document processing
  - [x] Format validation
  - [x] LLM integration
  - [x] Output formatting
- [ ] Async support planned
- [ ] Streaming support planned
- [ ] Batch processing support planned

## Architecture

### Current Structure

```
aigrok/
├── pdf_processor.py   # Core PDF processing
├── formats.py        # Format validation
├── cli.py           # Command line interface
└── __init__.py      # Package initialization
```

[x] = Implemented
[ ] = Not yet implemented

## Future Roadmap

### Phase 1: Enhanced Document Support

- [ ] Add support for more document formats:
  - [ ] Word documents (.docx)
  - [ ] PowerPoint (.pptx)
  - [ ] Markdown (.md)
  - [ ] HTML files
- [ ] Implement document conversion pipeline
- [ ] Add image extraction and processing

### Phase 2: Advanced LLM Features

- [x] Multiple LLM provider support:
  - [x] OpenAI
  - [x] Anthropic
  - [x] Local models (via Ollama)
- [ ] Prompt templating system
- [ ] Result caching and persistence
- [ ] Batch processing support

### Phase 3: Output Enhancement

- [ ] Additional output formats:
  - [ ] XML
  - [ ] YAML
  - [ ] SQL
  - [ ] Custom templates
- [x] Schema validation for structured outputs
- [x] Output filtering and transformation
- [ ] Custom formatter plugins

### Phase 4: Integration Features

- [ ] REST API service
- [ ] WebSocket support for streaming
- [ ] Docker container
- [ ] CI/CD pipeline
- [ ] API documentation
- [ ] Integration examples

## Development Guidelines

### Code Style

- [x] Follow PEP 8
- [x] Use type hints
- [x] Write docstrings
- [x] Keep functions focused
- [x] Test all features

### Documentation

- [x] API documentation
- [x] Usage examples
- [ ] Architecture overview
- [ ] Contributing guidelines

## Why "grok"?

The name "aigrok" combines "AI" with Heinlein's concept of "grok" - to understand so thoroughly that the observer becomes a part of the observed. In our context:

1. Document Understanding
   - Deep content analysis
   - Context awareness
   - Metadata extraction

2. AI Integration
   - LLM-powered analysis
   - Vision model support
   - Natural language interaction

3. User Experience
   - Simple interface
   - Multiple output formats
   - Flexible configuration

Just as Martians would "grok" their water-brothers, our tool aims to thoroughly understand and process documents, making their content accessible and useful. 