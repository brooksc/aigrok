# AIGrok Documentation

Welcome to the AIGrok documentation! This directory contains comprehensive documentation for the AIGrok project.

## Core Features

### PDF Processing
- PyMuPDF-based text extraction
- Vision model support for image analysis
- EasyOCR integration for image text extraction
  - Command-line flag: `--easyocr`
  - Language support: English (default)
  - Fallback to standard text LLM processing
  - Configurable via config file

### Processing Flow
1. Document Input
   - PDF file loaded via PyMuPDF
   - Text extraction from PDF
   - Image extraction from PDF (if needed)

2. OCR Processing (when enabled)
   - Initialize EasyOCR with configured languages
   - Process extracted images
   - Combine OCR text with PDF text

3. LLM Processing
   - Process combined text with configured LLM
   - Return structured response

## Documentation Structure

- [Architecture](architecture.md) - System architecture and design principles
- [API Documentation](api.md) - API reference and usage examples
- [Deployment Guide](deployment.md) - Deployment instructions and configurations
- [Testing Guide](testing.md) - Testing procedures and guidelines
- [CLI Reference](cli.md) - Command-line interface documentation
- [Dependencies](dependencies.md) - Detailed dependency information
- [Manual Pages](man/) - Detailed manual pages for each component

## Getting Started

If you're new to AIGrok, we recommend starting with:

1. [CLI Reference](cli.md) for command-line usage
2. [Architecture](architecture.md) for system overview
3. [API Documentation](api.md) for programmatic usage

## Contributing

For information about contributing to AIGrok documentation, please see our [Contributing Guide](../CONTRIBUTING.md).

## Building Documentation

The documentation is written in Markdown format. You can use any Markdown viewer to read it locally, or you can use tools like MkDocs or Sphinx to build a searchable documentation website.

## Documentation Updates

If you find any issues or have suggestions for improving the documentation, please open an issue or submit a pull request on our GitHub repository.
