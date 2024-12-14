# Contributing to AIGrok

Thank you for your interest in contributing to AIGrok! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- git
- virtualenv or conda (recommended)

### Local Development Environment

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/aigrok.git
   cd aigrok
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:

   ```bash
   pre-commit install
   ```

## Development Workflow

### 1. Code Style

We follow strict PEP 8 guidelines with these additional requirements:

- Use type hints for all function parameters and return values
- Write docstrings for all public functions, classes, and methods
- Keep functions focused and single-purpose
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable names

Example:

```python
def process_document(
    file_path: str,
    prompt: Optional[str] = None,
    *,
    model: str = "default"
) -> ProcessingResult:
    """Process a document using the specified model.

    Args:
        file_path: Path to the document file
        prompt: Optional processing prompt
        model: Model name to use for processing

    Returns:
        ProcessingResult containing the processed output

    Raises:
        ValueError: If file_path is invalid
        ProcessingError: If processing fails
    """
    # Implementation
```

### 2. Git Workflow

1. Create a new branch for your feature/fix:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes:
   - Write tests for new functionality
   - Update documentation as needed
   - Follow code style guidelines

3. Commit your changes:

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Commit message format:
   - feat: New feature
   - fix: Bug fix
   - docs: Documentation changes
   - test: Test additions/modifications
   - refactor: Code refactoring
   - style: Code style changes
   - chore: Maintenance tasks

4. Push your branch and create a pull request:

   ```bash
   git push origin feature/your-feature-name
   ```

### 3. Testing

- Write tests for all new functionality
- Maintain or improve code coverage
- Run the full test suite before submitting PR:

  ```bash
  python -m pytest tests/
  ```

### 4. Documentation

- Update relevant documentation for any changes
- Include docstrings for new functions/classes
- Add examples for new features
- Update README.md if needed

## Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Run code formatting: `black .`
   - Run type checking: `mypy .`
   - Run linting: `ruff .`
   - Update documentation

2. **PR Template**

   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Refactoring

   ## Testing
   - [ ] Added new tests
   - [ ] Updated existing tests
   - [ ] All tests passing

   ## Documentation
   - [ ] Updated relevant documentation
   - [ ] Added/updated docstrings
   - [ ] Updated README if needed
   ```

3. **Review Process**
   - Address reviewer comments
   - Keep PR focused and single-purpose
   - Maintain clear communication

## Release Process

1. Version Bumping
   - Follow semantic versioning
   - Update version in setup.py
   - Update CHANGELOG.md

2. Release Checklist
   - [ ] All tests passing
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] Version bumped
   - [ ] Release notes prepared

3. Release Steps

   ```bash
   # Update version
   bump2version patch  # or minor, or major

   # Create release branch
   git checkout -b release/v1.0.0

   # Create release commit
   git commit -am "chore: release v1.0.0"

   # Tag release
   git tag -a v1.0.0 -m "Release v1.0.0"

   # Push release
   git push origin release/v1.0.0 --tags
   ```

## Getting Help

- Open an issue for bugs or feature requests
- Join our community discussions
- Check existing documentation and issues
- Contact maintainers if needed

## Code of Conduct

Please note that AIGrok has a Code of Conduct. By participating in this project, you agree to abide by its terms.

## License

By contributing to AIGrok, you agree that your contributions will be licensed under its MIT license.
