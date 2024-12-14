# API Documentation

## Python API

### Core Functions

#### Document Processing

```python
from aigrok import process_document, ProcessingResult

def process_document(
    file_path: str,
    prompt: Optional[str] = None,
    *,
    model: str = "default",
    format: str = "text"
) -> ProcessingResult:
    """Process a document using the specified model.

    Args:
        file_path: Path to the document file
        prompt: Optional processing prompt
        model: Model name to use for processing
        format: Output format (text/json/csv/markdown)

    Returns:
        ProcessingResult containing the processed output

    Raises:
        ValueError: If parameters are invalid
        ProcessingError: If processing fails
    """
```

#### Format Validation

```python
from aigrok import validate_format

def validate_format(file_path: str) -> bool:
    """Validate if a file format is supported.

    Args:
        file_path: Path to the file to validate

    Returns:
        bool: True if format is supported, False otherwise
    """
```

#### Configuration Management

```python
from aigrok import Config

class Config:
    """Configuration management for AIGrok."""
    
    @classmethod
    def load(cls, path: Optional[str] = None) -> "Config":
        """Load configuration from file."""
        
    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file."""
        
    def update(self, **kwargs) -> None:
        """Update configuration values."""
```

### Response Types

#### ProcessingResult

```python
@dataclass
class ProcessingResult:
    """Result of document processing."""
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    page_count: Optional[int] = None
    llm_response: Optional[str] = None
```

### Usage Examples

#### Basic Document Processing

```python
from aigrok import process_document

# Process a PDF file
result = process_document(
    "document.pdf",
    prompt="Extract the main title",
    model="gpt-4-vision"
)

if result.success:
    print(f"Title: {result.text}")
else:
    print(f"Error: {result.error}")
```

#### Batch Processing

```python
from aigrok import process_documents

# Process multiple files
results = process_documents(
    ["doc1.pdf", "doc2.pdf"],
    prompt="Summarize the content",
    format="json"
)

for file_path, result in results.items():
    print(f"{file_path}: {result.text}")
```

#### Custom Configuration

```python
from aigrok import Config

# Load and update configuration
config = Config.load()
config.update(
    model="claude-3",
    format="markdown",
    timeout=30
)
config.save()
```

## CLI Reference

### Command Syntax

```bash
aigrok [OPTIONS] PROMPT FILE
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| --model | Model to use | gpt-3.5-turbo |
| --format | Output format | text |
| --output | Output file | stdout |
| --verbose | Enable debug logging | False |
| --metadata-only | Extract only metadata | False |

### Examples

1. Basic Usage

   ```bash
   aigrok "Extract the title" document.pdf
   ```

2. Custom Model

   ```bash
   aigrok --model gpt-4-vision "Analyze the image" image.pdf
   ```

3. JSON Output

   ```bash
   aigrok --format json "Extract authors" paper.pdf
   ```

4. Save to File

   ```bash
   aigrok --output results.md "Summarize" document.pdf
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
from aigrok import process_document, ProcessingError

try:
    result = process_document("file.pdf")
except ProcessingError as e:
    print(f"Processing failed: {e}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
```

## Configuration

### Configuration File

Location: `~/.config/aigrok/config.yaml`

```yaml
models:
  text:
    default: "gpt-3.5-turbo"
    fallback: "ollama/llama2"
  vision:
    default: "gpt-4-vision"
    fallback: "claude-3-opus"

formats:
  - ".pdf"
  - ".txt"

api:
  timeout: 30
  max_retries: 3
  batch_size: 10
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| AIGROK_CONFIG | Config file path | ~/.config/aigrok/config.yaml |
| AIGROK_MODEL | Default model | gpt-3.5-turbo |
| AIGROK_FORMAT | Default format | text |
| AIGROK_TIMEOUT | API timeout | 30 |

## Rate Limiting

### Default Limits

- Requests per minute: 60
- Concurrent requests: 10
- Tokens per request: 4000

### Custom Rate Limiting

```python
from aigrok import RateLimit

# Configure custom rate limits
RateLimit.configure(
    requests_per_minute=100,
    concurrent_requests=20,
    tokens_per_request=8000
)
```

## Webhook Integration

### Webhook Configuration

```python
from aigrok import register_webhook

# Register webhook for processing events
register_webhook(
    url="https://api.example.com/webhook",
    events=["processing.complete", "processing.error"],
    secret="webhook_secret"
)
```

### Webhook Payload Example

```json
{
    "event": "processing.complete",
    "timestamp": "2023-12-14T12:00:00Z",
    "data": {
        "file": "document.pdf",
        "success": true,
        "result": "Extracted text..."
    }
}
``` 