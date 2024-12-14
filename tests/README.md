# Test Suite Documentation

## Overview

This directory contains the test suite for the project. Tests are primarily defined in `test_cases.json` and executed through various test runners.

## Structure

```text
tests/
├── README.md              # This file
├── test_cases.json       # Main test case definitions
├── test_runner.py        # Unified test execution engine
├── setup_test_files.py   # Test file setup and validation
├── test_api.py           # API-specific test implementations
├── test_cli.py           # CLI-specific test implementations
├── test_formats.py       # Format handling tests
├── test_pdf_processor.py # PDF processing tests
└── files/               # Test file directory
    ├── simple.pdf
    ├── complex.pdf
    ├── large.pdf
    └── ...
```

## Test Categories

The test suite includes the following categories:

1. **API Tests** (`api_tests`)
   - Basic API functionality
   - Response validation
   - Error handling

2. **Validation Tests** (`validation`)
   - Input validation
   - Request/response format validation
   - Schema validation

3. **Performance Tests** (`performance`)
   - API response time
   - PDF processing speed
   - Resource usage

4. **Error Cases** (`error_cases`)
   - Invalid inputs
   - Missing files
   - Malformed requests

5. **Edge Cases** (`edge_cases`)
   - Special character handling
   - Large files
   - Empty files

## Adding New Tests

### 1. Add Test Case to JSON

Add your test case to the appropriate category in `test_cases.json`:

```json
{
    "category_name": {
        "group_name": [
            {
                "name": "test_name",
                "method": "api|cli|validation_test|performance_test|error_test",
                "file": "tests/files/example.pdf",  # if needed
                "prompt": "Your prompt",            # if needed
                "expected": "Expected result",
                "error_margin": null                # for numeric comparisons
            }
        ]
    }
}
```

### 2. Add Test Files

1. Place any required test files in the `files/` directory
2. Run `python setup_test_files.py` to validate file presence
3. Update sample file creation if needed

### 3. Test Implementation

The test runner will automatically execute your test case. If you need custom test logic:

1. Add implementation to appropriate test file (e.g., `test_api.py`)
2. Update test runner if needed

## Running Tests

### All Tests

```bash
pytest
```

### Specific Categories

```bash
pytest -k "api"  # Run API tests
pytest -k "performance"  # Run performance tests
```

### Parallel Execution

```bash
pytest -n auto  # Run tests in parallel
```

## Test Configuration

- Test timeout: 30 seconds per test
- Performance thresholds defined in test cases
- File size limits:
  - Normal PDFs: 10MB
  - Large file tests: 100MB

## Best Practices

1. **Test Case Names**
   - Use descriptive names
   - Follow `category_action_expected` pattern
   - Keep names unique within categories

2. **Test Data**
   - Use minimal test files
   - Include edge cases
   - Document data dependencies

3. **Validation**
   - Include both positive and negative tests
   - Validate all error conditions
   - Check boundary conditions

4. **Performance Tests**
   - Set realistic thresholds
   - Account for system variations
   - Include cleanup in teardown

## Troubleshooting

1. **Missing Files**
   - Run `python setup_test_files.py`
   - Check file permissions
   - Verify file paths in test cases

2. **Failed Tests**
   - Check test logs
   - Verify test file contents
   - Check for system dependencies

3. **Performance Issues**
   - Review resource usage
   - Check system load
   - Adjust timeouts if needed
