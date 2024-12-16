# Aigrok Overview

## Core Features

### PDF Processing
- PyMuPDF-based text extraction
- Vision model support for image analysis
- EasyOCR integration for image text extraction (New)
  - Command-line flag: --easyocr
  - Language support: English (default)
  - Fallback to standard text LLM processing
  - Configurable via config file

## Dependencies
### Core Dependencies
- PyMuPDF (fitz) >= 1.23.8: PDF processing
- Pillow >= 10.1.0: Image handling
- pydantic >= 2.5.0: Data validation
- loguru >= 0.7.2: Logging
- litellm >= 1.16.9: LLM interface
- ollama >= 0.1.6: Local model support

### Optional Dependencies
- easyocr >= 1.7.1: OCR support for image text extraction
  - Activated via --easyocr flag
  - Required for processing image-heavy PDFs
  - Additional language packs can be configured

## Configuration
### OCR Configuration
```yaml
ocr:
  enabled: false  # Set to true when using --easyocr flag
  languages: ['en']  # List of language codes
  fallback: true  # Use standard processing if OCR fails
```

## Processing Flow
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

## Error Handling
- Graceful fallback if OCR fails
- Clear error messages for configuration issues
- Logging of processing steps and errors

## Future Enhancements
- Support for additional OCR engines
- Multi-language OCR optimization
- OCR confidence scoring
- Caching of OCR results
