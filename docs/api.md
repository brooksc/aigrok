# API Documentation

## Overview

Aigrok provides a powerful Python API for document processing and analysis. The API is designed to be:
- Simple to use for basic cases
- Flexible for advanced scenarios
- Provider-agnostic with consistent interfaces
- Well-typed with comprehensive error handling

## Installation

```bash
pip install aigrok
```

## Quick Start

```python
from aigrok import process_document

# Basic usage
result = process_document("document.pdf", prompt="Summarize the content")
print(result.text)
```

## Core API

### Document Processing

#### process_document

```python
def process_document(
    file_path: str,
    prompt: Optional[str] = None,
    *,
    model: str = "default",
    format: str = "text",
    schema: Optional[Dict[str, Any]] = None,
    stream: bool = False,
    timeout: Optional[int] = None,
    retries: int = 3,
    **model_kwargs: Any
) -> Union[ProcessingResult, AsyncIterator[ProcessingResult]]:
    """Process a document using the specified model.

    Args:
        file_path: Path to the document file
        prompt: Optional processing prompt
        model: Model name to use for processing
        format: Output format (text/json/csv/markdown)
        schema: Optional schema for structured output
        stream: Enable streaming output
        timeout: Operation timeout in seconds
        retries: Number of retry attempts
        **model_kwargs: Provider-specific model parameters

    Returns:
        ProcessingResult or AsyncIterator[ProcessingResult] if streaming

    Raises:
        ValueError: If parameters are invalid
        ProcessingError: If processing fails
        TimeoutError: If operation times out
    """
```

#### process_documents

```python
async def process_documents(
    file_paths: List[str],
    prompt: Optional[str] = None,
    *,
    max_concurrent: int = 5,
    **kwargs: Any
) -> Dict[str, ProcessingResult]:
    """Process multiple documents concurrently.

    Args:
        file_paths: List of paths to process
        prompt: Optional processing prompt
        max_concurrent: Maximum concurrent operations
        **kwargs: Additional arguments passed to process_document

    Returns:
        Dictionary mapping file paths to results
    """
```

### Configuration

#### Config Class

```python
class Config:
    """Configuration management for aigrok."""
    
    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load configuration from file."""
        
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file."""
        
    def update(self, **kwargs) -> None:
        """Update configuration values."""
        
    @property
    def text_model(self) -> str:
        """Get current text model."""
        
    @property
    def vision_model(self) -> str:
        """Get current vision model."""
```

## Examples

### Basic Examples

See [basic_usage.py](examples/basic_usage.py) for complete examples.

#### Text Extraction

```python
from aigrok import process_document

# Basic text extraction
result = process_document(
    "document.pdf",
    prompt="Extract the main content"
)

if result.success:
    print(f"Content: {result.text}")
    print(f"Pages: {result.page_count}")
```

#### Structured Data

```python
# Extract structured data
result = process_document(
    "paper.pdf",
    prompt="Extract paper metadata",
    format="json",
    schema={
        "title": "string",
        "authors": ["string"],
        "publication_date": "string"
    }
)

if result.success:
    metadata = result.metadata
    print(f"Title: {metadata['title']}")
```

### Advanced Examples

See [advanced_usage.py](examples/advanced_usage.py) for complete examples.

#### Batch Processing

```python
import asyncio
from aigrok import process_documents

async def process_batch():
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    results = await process_documents(
        files,
        prompt="Summarize the content",
        max_concurrent=5
    )
    
    for file_path, result in results.items():
        print(f"{file_path}: {result.text}")

asyncio.run(process_batch())
```

#### Streaming Output

```python
async def stream_process():
    async for chunk in process_document(
        "large_doc.pdf",
        prompt="Analyze the content",
        stream=True
    ):
        print(f"Chunk: {chunk.text}")
```

#### Provider-Specific Options

```python
# OpenAI
result = process_document(
    "doc.pdf",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000
)

# Anthropic
result = process_document(
    "doc.pdf",
    model="claude-3",
    max_tokens_to_sample=2000
)

# Gemini
result = process_document(
    "doc.pdf",
    model="gemini-pro",
    candidate_count=3
)
```

## Error Handling

### Error Types

```python
class ProcessingError(Exception):
    """Base error for processing failures."""

class ValidationError(Exception):
    """Error for validation failures."""

class ConfigurationError(Exception):
    """Error for configuration issues."""
```

### Error Handling Examples

```python
try:
    result = process_document(
        "large_file.pdf",
        timeout=60,
        retries=3
    )
except ValueError as e:
    print(f"Invalid parameters: {e}")
except TimeoutError:
    print("Processing timed out")
except ProcessingError as e:
    print(f"Processing failed: {e}")
```

## Rate Limiting

```python
from aigrok import RateLimit

# Configure rate limits
RateLimit.configure(
    requests_per_minute=100,
    concurrent_requests=20,
    tokens_per_request=8000
)
```

## Best Practices

1. **Error Handling**: Always handle potential errors, especially for production use
2. **Configuration**: Use the Config class for managing settings
3. **Rate Limits**: Set appropriate rate limits for your use case
4. **Streaming**: Use streaming for large documents
5. **Batching**: Use process_documents for multiple files
6. **Schemas**: Define schemas for structured output
7. **Models**: Choose appropriate models for your task
8. **Testing**: Test with sample documents before production use