# AIGrok

AIGrok is an advanced document analysis tool that uses AI to process, analyze, and extract information from documents.

## Features

- 📄 Process multiple document formats (PDF, TXT, etc.)
- 🤖 Advanced AI-powered analysis
- 🔍 Smart content extraction
- 💾 Result caching for performance
- 🛠️ Extensible plugin system
- 📊 Comprehensive reporting

## Quick Start

1. Install AIGrok:

   ```bash
   pip install aigrok
   ```

2. Set up your configuration:

   ```bash
   aigrok config init
   ```

3. Process a document:

   ```bash
   aigrok process document.pdf
   ```

## Documentation

For detailed documentation, please see the [docs](docs/) directory:

- [CLI Reference](docs/cli.md) - Command-line interface guide
- [API Documentation](docs/api.md) - API reference
- [Configuration](docs/configuration.md) - Configuration guide
- [Deployment](docs/deployment.md) - Deployment instructions
- [Architecture](docs/architecture.md) - System architecture
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

## Requirements

- Python 3.9+
- Ollama with vision models installed
- 4GB RAM minimum
- Internet connection for API access

## Installation

### From PyPI

```bash
pip install aigrok
```

### From Source

```bash
git clone https://github.com/yourusername/aigrok.git
cd aigrok
pip install -e .
```

## Basic Usage

```python
from aigrok import process_document

# Process a document
result = process_document("document.pdf")
print(result.text)

# Process with custom prompt
result = process_document(
    "document.pdf",
    prompt="Extract main topics",
    model="llama2-vision"
)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](docs/)
- 💬 [Discussions](https://github.com/yourusername/aigrok/discussions)
- 🐛 [Issue Tracker](https://github.com/yourusername/aigrok/issues)

## Acknowledgments

- Thanks to all contributors
- Built with [Ollama](https://ollama.ai/)
- Inspired by the need for better document analysis tools
