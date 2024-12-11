# AIGrok Specification

## Current Implementation

### Core Features

1. PDF Processing
   - Text extraction using pypdf
   - First-page optimization for title/author extraction
   - Metadata extraction
   - Page count tracking

2. LLM Integration
   - Ollama integration for AI analysis
   - Vision model support for PDF analysis
   - Configurable model selection
   - Prompt-based information extraction

3. Output Formats
   - Text: Simple text output, ideal for basic information
   - JSON: Structured data output with schema support
   - CSV: Tabular data with headers
   - Markdown: Rich formatted output with sections

### Command Line Interface

```bash
aigrok <input.pdf> [options]
```

Options:
- `--prompt`: LLM analysis prompt
- `--model`: Ollama model name
- `--format`: Output format (text/json/csv/markdown)
- `--output`: Output file path
- `--metadata-only`: Extract only metadata
- `--verbose`: Enable debug logging

### Python API

```python
from aigrok import PDFProcessor

processor = PDFProcessor()
result = processor.process_file(
    file_path="document.pdf",
    prompt="Extract information",
    model="llama3.2-vision:11b"
)
```

## Future Roadmap

### Phase 1: Enhanced Document Support
- [ ] Add support for more document formats:
  - [ ] Word documents (.docx)
  - [ ] PowerPoint (.pptx)
  - [ ] Plain text (.txt)
  - [ ] Markdown (.md)
  - [ ] HTML files
- [ ] Implement document conversion pipeline
- [ ] Add image extraction and processing

### Phase 2: Advanced LLM Features
- [ ] Multiple LLM provider support:
  - [ ] OpenAI
  - [ ] Anthropic
  - [ ] Local models (already supported via Ollama)
- [ ] Prompt templating system
- [ ] Result caching and persistence
- [ ] Batch processing support

### Phase 3: Output Enhancement
- [ ] Additional output formats:
  - [ ] XML
  - [ ] YAML
  - [ ] SQL
  - [ ] Custom templates
- [ ] Schema validation for structured outputs
- [ ] Output filtering and transformation
- [ ] Custom formatter plugins

### Phase 4: Integration Features
- [ ] REST API service
- [ ] WebSocket support for streaming
- [ ] Docker container
- [ ] CI/CD pipeline
- [ ] API documentation
- [ ] Integration examples

## Architecture

### Current Structure
```
aigrok/
├── pdf_processor.py   # Core PDF processing
├── cli.py            # Command line interface
└── __init__.py       # Package initialization
```

### Planned Structure
```
aigrok/
├── core/
│   ├── processor.py    # Abstract processor
│   ├── llm.py         # LLM integration
│   └── config.py      # Configuration
├── formats/
│   ├── pdf.py         # PDF handler
│   ├── docx.py        # Word handler
│   └── text.py        # Text handler
├── output/
│   ├── text.py        # Text formatter
│   ├── json.py        # JSON formatter
│   └── csv.py         # CSV formatter
├── api/
│   ├── rest.py        # REST API
│   └── websocket.py   # WebSocket API
└── cli/
    └── main.py        # CLI implementation
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions focused
- Test all features

### Testing Strategy
- Unit tests for all components
- Integration tests for workflows
- Performance benchmarks
- Coverage requirements

### Documentation
- API documentation
- Usage examples
- Architecture overview
- Contributing guidelines

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