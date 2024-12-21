  # Release History

## v0.3.3 (2024-12-21)

### Changed
* Improved CLI output formatting with better structure and readability
* Enhanced text output format with configurable filename display
* Simplified JSON output structure for better consistency
* Added markdown output format support
* Version bump for release management

### Testing
* Updated CLI tests to reflect new output formatting changes

## v0.3.2 (2024-12-20)

### Added
* Enhanced logging system with detailed debug information for API requests and responses
* Added verbose mode logging for model configurations and processing results
* New test file `test_basic.py` for core functionality testing
* Added `strategy.md` documentation for development strategy
* Added speech.txt test file for additional test coverage

### Changed
* Improved API error handling with better error messages and logging
* Enhanced PDF processor with more detailed response information
* Updated configuration management with better validation
* Improved test organization and structure
* Updated CI/CD workflow in python-package.yml

### Documentation
* Added comprehensive API documentation updates
* Enhanced configuration documentation
* Updated release process documentation
* Improved test documentation

### Testing
* Current test coverage metrics:
  - Core Components: 58% overall coverage (+5%)
  - High Coverage Components (90%+):
    - API Layer: 100%
    - Type System: 100%
    - Logging: 100%
    - Core Init: 100%
  - Medium Coverage Components (60-89%):
    - CLI Interface: 70% (+5%)
    - Validation: 65% (+3%)
  - Areas for Improvement (< 60%):
    - PDF Processing: 45% (+3%)
    - Configuration: 40% (+4%)
    - Format Handling: 38% (+2%)

## v0.3.1 (2024-12-15)

### Changes
* Renamed HISTORY.md to CHANGELOG.md for better project conventions
* Fixed version numbering to follow semantic versioning
* Updated documentation references to reflect new changelog name
* Improved project organization and documentation consistency

### Testing Improvements
* Added new test files:
  - test_cli.py for CLI interface testing
  - test_logging.py for logging system tests
  - test_ocr.py for OCR functionality tests
  - test_pdf_processor.py for PDF processing tests
* Enhanced test framework with services.py for better test isolation
* Updated conftest.py with improved fixtures and configurations
* Added comprehensive test coverage reporting with pytest-cov
* Current test coverage metrics:
  - Core Components: 53% overall coverage
  - High Coverage Components (90%+):
    - API Layer: 100%
    - Type System: 100%
    - Logging: 100%
    - Core Init: 100%
  - Medium Coverage Components (60-89%):
    - CLI Interface: 65%
    - Validation: 62%
  - Areas for Improvement (< 60%):
    - PDF Processing: 42%
    - Configuration: 36%
    - Format Handling: 36%
* Added pytest-cov integration for coverage reporting
* Added comprehensive test documentation in docs/testing.md
* Improved test organization and cleanup procedures
* Established test coverage targets:
  - Core Components: 90%
  - API Endpoints: 85%
  - CLI Interface: 80%
  - Error Handlers: 95%

## v0.3.0 (2024-12-15)

### Major Features
* Enhanced OCR service with improved error handling
* Added support for multiple image formats in OCR processing
* Improved test isolation and reliability
* Enhanced error handling and validation

### Architecture Improvements
* Improved test suite organization
* Enhanced error handling in OCR service
* Better test isolation with temporary directories
* Improved configuration handling

### Testing Improvements
* Added comprehensive OCR service tests
* Improved test file management
* Enhanced mock and e2e test separation
* Better test cleanup and isolation

### Code Quality
* Removed empty directories and unused files
* Cleaned up build artifacts and cache directories
* Updated .gitignore for better project organization
* Improved test directory structure
* Removed redundant test files and configurations

### Documentation
* Updated README with latest features
* Improved API documentation
* Enhanced testing documentation
* Added detailed error handling documentation

## v0.2.6 (2024-12-15)

### Major Features
* Added interactive configuration management with --configure flag
* Added support for vision models and provider-specific processing
* Enhanced document type detection (text-only, images-only, mixed)
* Added provider-specific endpoint configuration
* Added OCR fallback configuration with graceful degradation
* Added multi-language OCR support with configurable language packs
* Added CLI support for OCR configuration and language selection
* Added support for multiple file processing with batch output

### Configuration Features
* Added ConfigManager class for centralized configuration handling
* Added support for provider-specific model configurations
* Added configuration validation and migration support
* Added environment variable support for sensitive data
* Added configuration persistence and loading
* Added interactive configuration wizard

### Architecture Improvements
* Refactored PDFProcessor for better separation of concerns
* Enhanced model capability validation and selection
* Improved provider-specific LLM response handling
* Added structured response types for better type safety
* Added timeout configuration for model requests (30s for text, 60s for vision)
* Added streaming support for large document processing
* Enhanced error handling with graceful degradation

### CLI Enhancements
* Added --easyocr flag for OCR processing
* Added --ocr-languages flag for language selection
* Added --ocr-fallback flag for graceful degradation
* Improved output formatting for multiple files
* Enhanced verbosity control and logging
* Added support for different output formats (text, json, markdown)

### Bug Fixes
* Fixed OCR processing in PDFProcessor to correctly handle and combine OCR text with PDF text
* Improved error handling in image extraction from PDFs
* Fixed test mocks for PDF document processing with OCR
* Fixed provider endpoint configuration validation
* Fixed handling of timeouts in model requests
* Fixed output formatting for batch processing

### Testing Improvements
* Added comprehensive test suite for OCR and LLM interactions
* Added test coverage for different document types and processing scenarios
* Improved test fixtures and helper functions
* Added mocking infrastructure for external services
* Added timeout and error handling tests

### Code Cleanup (2024-12-15)
* Removed empty directories (tests/logs, docs/spec)
* Cleaned up build artifacts and cache directories
* Updated .gitignore to exclude build artifacts and cache directories
* Improved test directory structure
* Removed redundant test files and configurations

### Documentation
* Updated configuration documentation with new options
* Added examples for vision model usage
* Improved error messages and logging
* Added type hints and docstrings
* Added CLI usage examples for new features

## v0.2.5 (2024-12-14)

### Improvements
* Added comprehensive debug logging throughout the codebase
* Enhanced verbosity output for better troubleshooting
* Improved error reporting and status messages

## v0.2.4 (2024-12-14)

### Bug Fixes
* Fixed format_output to handle both single results and lists of results
* Added proper list handling for multiple file processing outputs
* Fixed imports in cli.py

## v0.2.3 (2024-12-14)

### Bug Fixes
* Fixed CLI output handling for multiple file processing
* Fixed missing sys import in cli.py
* Improved error handling for process_file results

## v0.2.2 (2024-12-14)

### Changes

- Modernized build system:
  - Migrated from setup.py to pyproject.toml
  - Updated all dependencies to latest stable versions
  - Added explicit package configuration
  - Removed requirements.txt in favor of pyproject.toml dependencies

### Improvements

- Restructured and improved test framework:
  - Consolidated test files into a unified test runner
  - Added comprehensive test categories (format, CLI, API, validation, performance)
  - Improved test organization and documentation
  - Added test file management system
  - Enhanced test reporting capabilities

### Dependencies

- Updated setuptools to 69.0.2
- Updated litellm to 1.30.3
- Added pymupdf 1.23.8
- Updated all core dependencies to latest stable versions

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
