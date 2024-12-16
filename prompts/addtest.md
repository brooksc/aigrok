# Adding New Tests Prompt

This prompt guides you through the process of adding new tests to the Aigrok project.

1. Test Planning
   - Identify test category:
     * CLI functionality
     * Core functionality
     * Provider integration
     * Error handling
     * Performance
     * Security
   - Determine test type:
     * Unit test
     * Integration test
     * End-to-end test
   - Choose test mode:
     * `mock`: Uses mock objects for external dependencies
     * `e2e`: Uses real external services
   - Consider test dependencies:
     * Required test files
     * External services
     * Environment variables
     * Mock objects needed

2. Test Structure
   - Follow naming convention:
     * File: `test_[module].py`
     * Class: `Test[Feature]`
     * Function: `test_[scenario]_[expected_result]`
   - Place in correct directory:
     * Unit tests: `tests/unit/`
     * Integration tests: `tests/integration/`
     * E2E tests: `tests/e2e/`
   - Add test metadata:
     * Test ID (e.g., Test #3.1.4)
     * Description
     * Test mode (mock/e2e)
     * Dependencies
     * Expected outcomes

3. Test Implementation
   - Setup phase:
     * Import required modules
     * Define fixtures
     * Setup test environment
     * Create mock objects if needed
   - Test body:
     * Arrange: Prepare test data
     * Act: Execute functionality
     * Assert: Verify results
   - Cleanup:
     * Remove test files
     * Reset environment
     * Clear mocks
   - Error handling:
     * Test both success and failure cases
     * Verify error messages
     * Check exception types

4. Test Documentation
   - Add test case to `docs/testing.md`:
     * Test ID and title
     * Test inputs
     * Expected output
     * Evaluation criteria
   - Update test coverage report
   - Document any new fixtures
   - Add examples if helpful

5. Test Quality
   - Verify test isolation:
     * No dependencies on other tests
     * Clean setup and teardown
     * No side effects
   - Check performance:
     * Fast execution
     * Efficient resource usage
     * No unnecessary waits
   - Ensure reliability:
     * No flaky tests
     * Deterministic results
     * Proper timeout handling

6. Test Execution
   - Run test in mock mode:
     ```bash
     TEST_MODE=mock pytest tests/test_[module].py -v
     ```
   - Run test in e2e mode if applicable:
     ```bash
     TEST_MODE=e2e pytest tests/test_[module].py -v
     ```
   - Verify test fails when it should
   - Check test output clarity

7. Code Review
   - Self-review checklist:
     * Test naming clarity
     * Code style consistency
     * Error handling completeness
     * Documentation accuracy
     * Mock object fidelity
   - Update related tests if needed
   - Consider edge cases
   - Review performance impact

8. Integration
   - Run full test suite:
     ```bash
     ./scripts/run_tests.py
     ```
   - Check CI pipeline compatibility
   - Verify coverage reports
   - Update test counts in docs

## Test Template
```python
"""Test module for [feature]."""
import pytest
from aigrok import [module]

@pytest.mark.mode("mock")  # or "e2e" or both
class Test[Feature]:
    """Test suite for [feature]."""
    
    @pytest.fixture
    def setup_test_env(self):
        """Setup test environment."""
        # Setup code
        yield
        # Cleanup code
    
    def test_[scenario]_[expected_result](self, setup_test_env):
        """
        Test #X.Y.Z: [Description]
        
        Test inputs: [inputs]
        Expected output: [output]
        Evaluation: [criteria]
        """
        # Arrange
        [setup code]
        
        # Act
        [execution code]
        
        # Assert
        [verification code]
```

## Notes
- Always run tests in both mock and e2e modes when applicable
- Keep test execution time minimal
- Use appropriate fixtures for resource management
- Document all test requirements and dependencies
- Follow the Arrange-Act-Assert pattern
- Consider security implications of test data
- Keep test files and resources in appropriate directories
- Use meaningful test data that covers edge cases
