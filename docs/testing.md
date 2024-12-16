# Testing Specification

## Test Cases

### Test Types
Tests that interact with external services can be run in either mode:
- **mock**: Uses mock objects for external dependencies (OCR, LLM, etc.)
- **e2e**: Uses real external services and dependencies

Run tests with: `TEST_MODE=mock|e2e pytest`

### 1. Command Line Interface Tests

#### 1.1 Basic CLI Functionality

Test #1.1.1: Verify help command output [TODO]
- Test inputs: `aigrok -h`
- Expected output: Help text containing usage instructions, available commands, and options
- Evaluation: String comparison of help text sections and command descriptions

Test #1.1.2: Verify version output [TODO]
- Test inputs: `aigrok --version`
- Expected output: Version string in format "x.y.z"
- Evaluation: Regex match against version pattern

#### 1.2 Output Formatting

Test #1.2.1: Single file text output without filename prefix [mock, e2e]
- Test inputs: `aigrok summarize tests/files/invoice.pdf`
- Expected output: Summary text without filename prefix
- Evaluation: Assert no "filename:" prefix in output

Test #1.2.2: Multiple files text output with filename prefixes [mock, e2e]
- Test inputs: `aigrok summarize tests/files/*.pdf`
- Expected output: Each line prefixed with corresponding filename
- Evaluation: Assert each line starts with "filename:"

Test #1.2.3: JSON output format [mock, e2e]
- Test inputs: `aigrok summarize --format json tests/files/invoice.pdf`
- Expected output: Valid JSON with metadata and content
- Evaluation: JSON schema validation

Test #1.2.4: Markdown output format [mock, e2e]
- Test inputs: `aigrok summarize --format markdown tests/files/invoice.pdf`
- Expected output: Markdown formatted text with headers and sections
- Evaluation: Markdown structure validation

### 2. Logging Tests

Test #2.1.1: Verify logging disabled by default
- Test inputs: Configure logging with verbose=False
- Expected output: No log output to stderr
- Evaluation: Assert stderr is empty

Test #2.2.1: Verify debug logging with verbose flag
- Test inputs: Configure logging with verbose=True
- Expected output: Debug level messages in stderr
- Evaluation: Assert debug messages present in stderr

### 3. PDF Processing Tests

#### 3.1 OCR Functionality

Test #3.1.1: OCR initialization without reader [mock, e2e]
- Test inputs: Process image without initialized OCR reader
- Expected output: Error indicating OCR not initialized
- Evaluation: Exception type and message validation

Test #3.1.2: OCR processing success [mock, e2e]
- Test inputs: Process image with valid OCR configuration
- Expected output: Extracted text with confidence score
- Evaluation: Assert OCR text present and confidence > 0

Test #3.1.3: OCR processing error handling [mock, e2e]
- Test inputs: Process invalid image data
- Expected output: Error with appropriate message
- Evaluation: Exception handling validation

#### 3.2 Text Processing

Test #3.2.1: Text combination
- Test inputs: Multiple text segments from different sources
- Expected output: Combined text maintaining order and structure
- Evaluation: String comparison of combined text

Test #3.2.2: Document processing with OCR [mock, e2e]
- Test inputs: PDF with text and images
- Expected output: Combined text from PDF text and OCR
- Evaluation: Content presence validation

Test #3.2.3: Document processing without OCR [mock, e2e]
- Test inputs: PDF with OCR disabled
- Expected output: Only extracted PDF text
- Evaluation: Assert no OCR processing occurred

### 4. Test Runner Tests

Test #4.1.1: Runner initialization [TODO]
- Test inputs: Initialize runner with configuration
- Expected output: Runner instance with correct settings
- Evaluation: Object attribute validation

Test #4.2.1: Stats update verification [TODO]
- Test inputs: Run tests and update statistics
- Expected output: Accurate test statistics
- Evaluation: Numeric comparison of stats

Test #4.2.2: Category execution [TODO]
- Test inputs: Run specific test category
- Expected output: Only tests in category executed
- Evaluation: Test execution count validation

Test #4.3.1: Results reporting [TODO]
- Test inputs: Complete test run
- Expected output: Formatted test results
- Evaluation: Report format validation

Test #4.4.1: Error handling in runner [TODO]
- Test inputs: Inject test errors
- Expected output: Proper error capture and reporting
- Evaluation: Error handling validation

Test #4.5.1: Test cases JSON validation [TODO]
- Test inputs: Verify test_cases.json
- Expected output: Valid test configuration
- Evaluation: JSON schema validation

Test #4.5.2: Test files directory check [TODO]
- Test inputs: Verify test files directory
- Expected output: Required test files present
- Evaluation: Directory structure validation

### 5. Performance Tests [TODO]

Test #5.1.1: Resource usage limits [TODO]
- Test inputs: Process large PDF files
- Expected output: Memory and CPU usage within specified limits
- Evaluation: Resource monitoring metrics

Test #5.1.2: Processing time limits [TODO]
- Test inputs: Process multiple PDFs in parallel
- Expected output: Processing time within specified limits
- Evaluation: Timing measurements

### 6. Security Tests [TODO]

Test #6.1.1: API key validation [TODO]
- Test inputs: Various API key formats and values
- Expected output: Proper validation and error handling
- Evaluation: Security validation checks

Test #6.1.2: File access restrictions [TODO]
- Test inputs: Attempts to access files outside allowed paths
- Expected output: Access denied errors
- Evaluation: Security boundary checks

## Test Implementation

### Test Structure

```
tests/
├── test_cases.json       # Test case definitions
├── test_runner.py        # Test execution engine
├── run_cached_tests.py   # Cached test runner
├── files/               # Test file directory
│   ├── invoice.pdf      # Sample invoice
│   ├── ai-paper.pdf     # Academic paper
│   └── empty.pdf        # Edge case file
└── logs/                # Test execution logs
```

### Test Case Format

```json
{
    "name": "test_name",
    "method": "api|cli|validation",
    "file": "path/to/test/file",
    "prompt": "test prompt",
    "expected": {
        "success": true,
        "text": "expected output",
        "error": null
    },
    "test_type": "dual-mode"
}
```

### Running Tests

```bash
# Run all tests
python tests/run_cached_tests.py

# Run specific test category
python tests/run_cached_tests.py --category api_tests

# Run with debug logging
python tests/run_cached_tests.py --verbose
```

## Test Coverage Requirements

### Minimum Coverage Targets

- Core Components: 90%
- API Endpoints: 85%
- CLI Interface: 80%
- Error Handlers: 95%

### Coverage Reporting

```bash
# Generate coverage report
pytest --cov=aigrok tests/

# Generate HTML report
pytest --cov=aigrok --cov-report=html tests/
```


## Test Data Management

### Test Files

- Sample Documents
  - [x] Basic PDF (1-2 pages)
  - [x] Large PDF (50+ pages)
  - [x] Text Files
  - [x] Invalid Files

- Edge Cases
  - [x] Empty Files
  - [x] Unicode Content
  - [x] Special Characters
  - [x] Maximum Size Files

### Test Environment

- Configuration
  - [x] Mock API Keys
  - [x] Test Endpoints
  - [x] Rate Limits
  - [x] Timeouts

- Dependencies
  - [x] Minimal Requirements
  - [x] Optional Features
  - [x] Version Compatibility

## Continuous Integration

### CI Pipeline

- Pre-commit Checks
  - [x] Code Formatting
  - [x] Type Checking
  - [x] Linting
  - [x] Basic Tests

- Full Test Suite
  - [x] Unit Tests
  - [x] Integration Tests
  - [x] Performance Tests
  - [x] Coverage Report

### Test Automation

- Scheduled Tests
  - [x] Daily Full Suite
  - [x] Weekly Performance
  - [x] Monthly Compatibility

- Event-Triggered Tests
  - [x] Pull Requests
  - [x] Version Tags
  - [x] Configuration Changes

## Test Maintenance

### Documentation

- Test Plans
  - [x] Test Strategy
  - [x] Test Cases
  - [x] Coverage Goals
  - [x] Performance Targets

- Procedures
  - [x] Setup Instructions
  - [x] Running Tests
  - [x] Debugging Guide
  - [x] Maintenance Tasks

### Quality Assurance

- Code Review
  - [x] Test Code Review
  - [x] Coverage Review
  - [x] Performance Review
  - [x] Documentation Review

- Test Quality
  - [x] Test Case Validation
  - [x] Edge Case Coverage
  - [x] Error Scenario Coverage
  - [x] Performance Metrics

## Future Test Enhancements

### Planned Improvements

1. Enhanced Coverage
   - [ ] Additional Edge Cases
   - [ ] More File Formats
   - [ ] Complex Workflows
   - [ ] Security Testing

2. Automation
   - [ ] Automated Test Generation
   - [ ] Performance Regression Detection
   - [ ] Test Data Generation
   - [ ] Result Analysis

3. Reporting
   - [ ] Interactive Dashboards
   - [ ] Trend Analysis
   - [ ] Failure Analysis
   - [ ] Performance Metrics

4. Infrastructure
   - [ ] Containerized Testing
   - [ ] Parallel Execution
   - [ ] Cloud Integration
   - [ ] Load Testing 