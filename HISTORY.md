# Release History

## v0.2.1 (2024-12-12)

### Changes
- Published package to PyPI

## v0.2 (2024-12-11)

### Breaking Changes
- Changed CLI interface to require prompt as first positional argument
- Removed `--prompt` flag from command line options
- Removed auto-generated prompt logic from PDF processor

### New Features
- Added support for multiple LLM providers:
  - OpenAI models (GPT-4, GPT-3.5)
  - Anthropic models (Claude)
  - Local models via Ollama
- Added model configuration in `~/.config/aigrok/config.yaml`
- Added support for processing multiple input files (like grep)
  - Files are processed sequentially
  - Output includes filename prefixes for multiple files
  - Continues processing if one file fails

### Improvements
- Updated Pydantic models to use ConfigDict instead of class-based config
- Renamed schema field to schema_def to avoid BaseModel attribute shadowing
- Added warning filters for external package deprecation notices
- Improved error handling in PDF processor
- Simplified prompt handling in document processing

### Documentation
- Updated README.md with new CLI interface examples
- Updated spec.md to reflect new command structure
- Added HISTORY.md to track version changes
- Enhanced testing documentation in spec.md:
  - Added comprehensive test reporting requirements
  - Documented current test coverage
  - Outlined planned testing improvements
  - Added test organization guidelines
  - Specified test data management approach

## v0.1 (2024-12-10)

### Initial Release
- Basic PDF and text file processing
- Single LLM integration for document analysis
- Multiple output formats:
  - Text (default)
  - JSON with schema validation
  - CSV with headers
  - Markdown with sections
- Document analysis features:
  - Text extraction
  - Metadata extraction
  - Author name parsing
  - Title extraction
- Command line interface with options:
  - Model selection
  - Output format control
  - File type validation
  - Metadata-only mode
  - Verbose logging
- Python API for programmatic access
- Comprehensive test suite
- Format validation for supported file types
- Error handling and logging system 