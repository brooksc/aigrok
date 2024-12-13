# aigrok

A Python package for document processing and analysis, with initial support for PDF files and LLM integration.

## Why "grok"?

Ever wondered why we chose the name "aigrok"? Well, "grok" is a term coined by Robert A. Heinlein in his 1961 science fiction novel "Stranger in a Strange Land". It means to understand something so thoroughly that you become one with it. Or as a Martian would say, "to drink it all in" (literally in their case - Martians were quite... thorough in their understanding).

We thought it was the perfect name for our tool because:
1. It's doing deep document analysis (groking the content)
2. It's using AI to understand documents (artificial groking, if you will)
3. It sounds like a noise a PDF would make if you squeezed it too hard

Plus, let's be honest, "aigrok" is way cooler than "ai_document_analyzer_v2_final_FINAL_really_final.py"

## Installation

### Using pip

You can install aigrok directly from PyPI:
```bash
pip install aigrok
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aigrok.git
cd aigrok
```

2. Install in development mode:
```bash
pip install -e .
```

3. Install Ollama (required for LLM integration):
   - Follow instructions at [Ollama's website](https://ollama.ai)
   - Pull the model you want to use (e.g., `ollama pull llama3.2-vision:11b`)

## Usage

### Command Line Interface

Process PDFs directly from the command line using the `aigrok` command:

```bash
# Basic PDF text extraction
aigrok "Extract the text" input.pdf

# Analyze PDF with LLM
aigrok "Summarize this document" input.pdf --model llama3.2-vision:11b

# Extract specific information with different output formats
aigrok "Extract author names" input.pdf --format text  # Comma-separated list
aigrok "Extract author names" input.pdf --format json  # JSON array of objects
aigrok "Extract author names" input.pdf --format csv   # CSV with headers

# Extract metadata only
aigrok "Extract metadata" input.pdf --metadata-only

# Save output to file
aigrok "Extract the text" input.pdf -o output.txt

# Enable verbose logging
aigrok "Extract the text" input.pdf -v
```

Available options:
- `input`: Path to the PDF file
- `--model`: Name of the Ollama model to use
- `--output, -o`: Save output to file
- `--format`: Output format (text, json, csv, markdown)
- `--metadata-only`: Only extract metadata
- `--verbose, -v`: Enable verbose logging

### Output Formats

The tool supports multiple output formats:

1. Text (default):
```
Lanxiang Hu, Qiyu Li, Anze Xie, Nan Jiang, Haojian Jin, Hao Zhang
```

2. JSON:
```json
[
  {"first_name": "Lanxiang", "last_name": "Hu"},
  {"first_name": "Qiyu", "last_name": "Li"},
  {"first_name": "Anze", "last_name": "Xie"}
]
```

3. CSV:
```csv
first_name,last_name
Lanxiang,Hu
Qiyu,Li
Anze,Xie
```

4. Markdown:
```markdown
# Document Analysis Results

## Metadata
- Pages: 1
- Author: Example Author

## Extracted Text
[Document text here]

## LLM Analysis
[Analysis results here]
```

### Python API

```python
from aigrok import PDFProcessor

# Initialize the processor
processor = PDFProcessor()

# Process a PDF file with LLM analysis
result = processor.process_file(
    "path/to/your/document.pdf",
    prompt="Extract the author names",
    model="llama3.2-vision:11b"
)

if result.success:
    # Access LLM's analysis
    print(result.llm_response)
    
    # Access other data
    print(result.text)
    print(result.metadata)
    print(f"Document has {result.page_count} pages")
else:
    print(f"Error: {result.error}")
```

## Development

### Running Tests

```bash
pytest
```

### Project Structure

- `aigrok/` - Main package directory
  - `pdf_processor.py` - PDF processing with LLM integration
  - `cli.py` - Command-line interface
- `tests/` - Test files
- `requirements.txt` - Project dependencies
- `setup.py` - Package installation configuration
- `pyproject.toml` - Build system requirements

## Contributing

We welcome contributions! Whether you want to fix a bug, add a feature, or improve documentation, please feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

And remember, as a wise Martian once said, "thou art god" (that's more Heinlein humor for you). 

# Postscript

90% of this project was written by AI using Cursor and Claude.