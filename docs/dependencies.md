# Dependencies

This document outlines all the dependencies used in the Aigrok project, their purposes, and how they are used in the codebase.

## Core Dependencies

### Document Processing
- **pypdf** (>=5.1.0)
  - Used for PDF file parsing and manipulation
  - Handles PDF metadata extraction
  - Manages PDF text extraction

- **pymupdf** (>=1.23.8)
  - Advanced PDF processing capabilities
  - Image extraction from PDFs
  - PDF rendering and visualization
  - Used for high-quality text extraction

### OCR and Image Processing
- **easyocr** (>=1.7.1)
  - Optical Character Recognition (OCR)
  - Extracts text from images
  - Supports multiple languages
  - Used for processing scanned documents

- **pillow** (>=10.1.0)
  - Image processing and manipulation
  - Format conversion
  - Image optimization
  - Used by OCR pipeline

### LLM Integration
- **litellm** (>=1.30.3)
  - LLM provider integration
  - Unified interface for multiple LLM providers
  - Handles API calls to various LLM services
  - Manages model selection and fallbacks

- **ollama** (>=0.1.6)
  - Local LLM integration
  - Manages local model deployment
  - Handles local inference
  - Used for offline processing capabilities

### Configuration and Environment
- **python-dotenv** (>=1.0.0)
  - Environment variable management
  - Secure credential storage
  - Configuration loading
  - Used for managing API keys and settings

- **pyyaml** (>=6.0.1)
  - YAML configuration parsing
  - Configuration file management
  - Used for storing and loading settings

### Data Validation and Models
- **pydantic** (>=2.5.2)
  - Data validation
  - Type checking
  - Schema definition
  - Configuration management
  - Used throughout for robust data handling

### Networking and APIs
- **requests** (>=2.31.0)
  - HTTP client for API interactions
  - File downloads
  - Web service integration
  - Used for external API communication

### Logging and Debugging
- **loguru** (>=0.7.2)
  - Advanced logging capabilities
  - Error tracking
  - Debug information
  - Used for comprehensive logging throughout the application

## Development Dependencies

### Testing
- **pytest** (>=7.4.3)
  - Test framework
  - Test discovery and execution
  - Fixture management
  - Used for all testing needs

### Code Quality Tools
- **ruff**
  - Fast Python linter
  - Code style checking
  - Static analysis
  - Used for maintaining code quality

- **black**
  - Code formatting
  - Style consistency
  - Used for automatic code formatting

- **isort**
  - Import sorting
  - Import organization
  - Used for maintaining clean imports

## Version Requirements

- Python >= 3.8
- Supports Python versions: 3.8, 3.9, 3.10, 3.11

## Optional Dependencies

Some features may require additional dependencies based on usage:

1. **Vision Models**
   - Required for processing images and diagrams
   - Activated when using vision-capable models

2. **Audio Processing**
   - Required for audio transcription
   - Activated when using audio-capable models

## Installation

### Basic Installation
```bash
pip install aigrok
```

### Development Installation
```bash
pip install aigrok[dev]
```

## Dependency Management

We follow these principles for dependency management:

1. **Version Pinning**
   - All dependencies have minimum version requirements
   - Regular updates for security and features
   - Careful testing of version upgrades

2. **Security**
   - Regular vulnerability scanning
   - Automated dependency updates
   - Security patches prioritized

3. **Compatibility**
   - Cross-platform testing
   - Python version compatibility checks
   - Regular integration testing

4. **Performance**
   - Dependency impact monitoring
   - Optimization of heavy dependencies
   - Regular performance testing

## Updating Dependencies

When updating dependencies:

1. Check the changelog of the updated package
2. Run the test suite
3. Test all affected functionality
4. Update documentation if needed
5. Update version constraints in pyproject.toml
