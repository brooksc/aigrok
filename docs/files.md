# File Structure

This document provides a comprehensive overview of all files in the AIGrok repository.

## Root Directory

### Core Files

- `README.md` - Project overview, features, and getting started guide
- `CONTRIBUTING.md` - Contribution guidelines and development setup
- `LICENSE` - MIT license file
- `HISTORY.md` - Project changelog and version history
- `pyproject.toml` - Project metadata and build system requirements
- `setup.py` - Package installation configuration
- `requirements.txt` - Project dependencies

### Scripts Directory (`scripts/`)

- `install_test.sh` - Script for testing package installation
- `push-test-pypi.sh` - Script for pushing to test PyPI
- `run_tests.py` - Simple test runner script
- `run_cached_tests.py` - Test runner with caching support

### Configuration

- `.gitignore` - Git ignore patterns
- `.envrc` - Direnv configuration

## Main Package (`aigrok/`)

### Core Modules

- `__init__.py` - Package initialization and version info
- `api.py` - API client implementation
- `cli.py` - Command-line interface implementation
- `pdf_processor.py` - PDF processing functionality
- `validation.py` - Input validation utilities
- `formats.py` - File format handling
- `types.py` - Type definitions and data classes

## Tests (`tests/`)

### Test Infrastructure

- `__init__.py` - Makes tests a Python package
- `conftest.py` - Pytest fixtures and configuration
- `test_runner.py` - Main test execution engine
- `test_schema.py` - Schema validation for test cases
- `test_performance.py` - Performance testing utilities

### Test Data

- `test_cases.json` - Main test case definitions
- `archived_test_cases.json` - Archived/historical test cases
- `files/` - Directory containing test files
  - `invoice.pdf` - Sample invoice for testing
  - `ai-paper.pdf` - Sample academic paper
  - `empty.pdf` - Empty PDF for edge cases
  - `not_a_pdf.txt` - Invalid file for testing

### Test Documentation

- `README.md` - Test suite documentation

## Documentation (`docs/`)

### Core Documentation

- `README.md` - Documentation overview
- `architecture.md` - System architecture and design
- `api.md` - API reference
- `cli.md` - CLI usage guide
- `configuration.md` - Configuration guide
- `deployment.md` - Deployment instructions
- `files.md` - This file inventory
- `quickstart.md` - Getting started guide
- `testing.md` - Testing guide
- `troubleshooting.md` - Troubleshooting guide

### Manual Pages

- `man/aigrok.1.md` - Main command manual page

## File Organization

The repository follows a standard Python project structure:

- Core package code in `aigrok/`
- Tests and test data in `tests/`
- Documentation in `docs/`
- Scripts in `scripts/`
- Build and package files in root directory

This organization makes it easy to:

1. Find and maintain code
2. Run tests independently
3. Build and distribute the package
4. Access documentation
