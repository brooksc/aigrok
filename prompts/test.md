# Testing Prompt

This prompt guides you through comprehensive testing of the codebase, including both unit and integration tests.

1. Environment Setup
   - Verify required credentials
   - Check environment variables
   - Configure test environments (mock/e2e)
   - Verify service endpoints
   - Set up test data and fixtures

2. Test Coverage Analysis
   - Run pytest with coverage report
   - Identify untested code paths
   - Compare against test specification
   - Document coverage gaps
   - Set coverage improvement targets

3. Unit Test Suite
   - Run unit tests in mock mode
   - For each failing test:
     * Analyze error messages
     * Review test implementation
     * Fix identified issues
     * Re-run failed tests
     * Continue until all pass
   - Document any stability issues

4. Integration Test Suite
   - Run e2e tests with real services
   - Test provider integrations
   - Verify API interactions
   - Test under various configurations
   - For each failing test:
     * Debug service interactions
     * Check configuration
     * Fix integration issues
     * Verify fixes
     * Document service dependencies

5. Performance Testing
   - Measure response times
   - Check resource usage
   - Test under load conditions
   - Verify timing constraints
   - Document performance baselines

6. Error Handling
   - Test service failures
   - Verify error messages
   - Check recovery procedures
   - Test timeout scenarios
   - Validate error responses

7. Security Testing
   - Test authentication flows
   - Verify access controls
   - Check data handling
   - Test input validation
   - Verify secure configurations

8. Documentation Updates
   - Update test specifications
   - Document configuration changes
   - Update test examples
   - Add notes about limitations
   - Document test dependencies

9. Final Verification
   - Run complete test suite
   - Verify all tests pass
   - Check coverage meets targets
   - Ensure changes are documented
   - Update test status
