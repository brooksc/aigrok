# Test Directory Specification

## Overview

The test suite uses a hybrid approach:

- JSON-based test cases for application functionality
- Python-based tests for test infrastructure

## Core Test Files

### Primary Test Files

- `test_cases.json` - Central repository of all application test cases
- `test_runner.py` - Test runner implementation and infrastructure tests
- `test_performance.py` - Performance testing utilities
- `test_schema.py` - Schema validation for test cases
- `conftest.py` - Test fixtures and configuration
- `__init__.py` - Makes the tests directory a Python package

### Test Files Directory (`files/`)

- `invoice.pdf` - Valid PDF file for invoice extraction tests
- `ai-paper.pdf` - Valid PDF file for academic paper extraction tests
- `simple.pdf` - Simple PDF for basic tests
- `empty.pdf` - Empty PDF for edge cases
- `not_a_pdf.txt` - Text file used for invalid file type testing

## Test Categories (in test_cases.json)

### API Tests

Tests API functionality including:

- Invoice data extraction
- Request/response validation
- Error handling
- Client behavior

### CLI Tests

Tests command-line interface including:

- Paper extraction
- Parser functionality
- Output formatting
- Multiple file handling

### Format Tests

Tests file format handling including:

- Format validation
- Supported format detection
- Path handling
- Case sensitivity

### Performance Tests

Tests performance aspects including:

- API response time
- PDF processing speed
- Large file handling

### Error Cases

Tests error handling including:

- Invalid file types
- Missing files
- Invalid prompts
- Malformed requests

### Edge Cases

Tests boundary conditions including:

- Special character handling
- File size limits
- Empty files

### Schema Tests

Tests JSON schema validation including:

- Valid test cases
- Missing required fields
- Invalid field values

## Infrastructure Tests (in Python)

### Test Runner Tests

Located in `test_runner.py`:

- Test runner initialization
- Test statistics tracking
- Category-based test running
- Result reporting
- Error handling
- Test environment verification

### Performance Utilities

Located in `test_performance.py`:

- Performance measurement tools
- Baseline establishment
- Performance test decorators
- Warmup functionality

### Schema Validation

Located in `test_schema.py`:

- Test case validation logic
- Required field checking
- Category-specific validation
- File existence validation

## Test Execution and Reporting

### Test Runner Features

- JSON-based test case execution
- Detailed test result reporting including:
  - Pass/fail status
  - Execution time tracking
  - Detailed failure analysis
  - Expected vs actual results
  - Test case details for failures

### Test Statistics

The test runner provides:

- Total tests executed
- Pass/fail counts
- Total execution time
- Skipped test tracking
- Per-category results

### Failure Reporting

Failed test reports include:

- Test case details
- Expected vs actual results
- Error messages
- Test execution context
- Duration information

## Best Practices

1. Application Tests
   - Write all application tests in test_cases.json
   - Use appropriate test categories
   - Include clear expected results
   - Test both success and failure cases

2. Infrastructure Tests
   - Keep in Python
   - Focus on test runner functionality
   - Verify test environment
   - Test reporting accuracy

3. Test Data
   - Keep minimal test files
   - Use appropriate file types
   - Include edge cases
   - Clean up after tests

4. Documentation
   - Keep spec.md updated
   - Document test categories
   - Explain test organization
   - Include usage examples
