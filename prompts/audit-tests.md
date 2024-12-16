# Test Audit Prompt

This prompt guides you through auditing existing tests to ensure they are valid, comprehensive, and accurately reflect real-world usage.

## 1. Test Isolation
- Does the test depend on global state?
- Could multiple test runs interfere with each other?
- Are resources properly cleaned up after each test?
- Does the test modify any system state (files, env vars, etc.)?
- Are external services properly mocked?

## 2. Test Coverage vs Reality
- Does the test only verify the "happy path"?
- Are edge cases and error conditions tested?
- Does the test match actual usage patterns?
- Are all code paths exercised?
- Are async operations properly handled?
- Does the test verify persistence across multiple calls?

## 3. Test Environment
- Does the test assume specific environment settings?
- Are environment variables properly mocked/controlled?
- Does the test work across different platforms?
- Are file paths handled properly?
- Are permissions and access controls tested?

## 4. Test Dependencies
- Does the test have hidden dependencies?
- Are all dependencies properly documented?
- Are dependencies properly mocked?
- Could dependency changes break the test?
- Is the test order-dependent?

## 5. Test Assumptions
- What assumptions does the test make about the system?
- Are these assumptions documented?
- Are these assumptions valid?
- Could these assumptions change?
- Are assumptions tested explicitly?

## 6. Test Completeness
- Does the test verify all relevant outputs?
- Are side effects checked?
- Is error handling fully tested?
- Are all configuration options tested?
- Are all API endpoints/functions covered?

## 7. Test Isolation from Implementation
- Does the test verify behavior or implementation?
- Would refactoring break the test?
- Is the test too tightly coupled to current code?
- Does the test allow for alternative implementations?
- Are implementation details leaked in the test?

## 8. Test Reliability
- Is the test flaky?
- Are timeouts handled properly?
- Are race conditions possible?
- Are external resources properly mocked?
- Is the test deterministic?

## 9. Test Documentation
- Is the test purpose clear?
- Are prerequisites documented?
- Are test inputs and outputs documented?
- Are edge cases documented?
- Is the test name descriptive?

## 10. Integration Points
- Are module boundaries tested?
- Are API contracts verified?
- Are data formats validated?
- Are protocol implementations tested?
- Are version compatibilities checked?

## 11. State Management
- How is state initialized?
- How is state cleaned up?
- Are state changes tracked?
- Is concurrent state access handled?
- Is persistent state tested?

## 12. Real World Scenarios
- Does the test reflect real usage?
- Are realistic data volumes tested?
- Are performance characteristics verified?
- Are resource constraints considered?
- Are error scenarios realistic?

## Example Test Audit Checklist

For each test file:

1. Basic Information:
   - [ ] Test name and purpose clear
   - [ ] Test dependencies listed
   - [ ] Required setup documented
   - [ ] Expected outcomes specified

2. Test Quality:
   - [ ] Verifies behavior not implementation
   - [ ] Handles edge cases
   - [ ] Tests error conditions
   - [ ] Is deterministic
   - [ ] Cleans up after itself

3. Coverage Analysis:
   - [ ] All code paths exercised
   - [ ] All configurations tested
   - [ ] All error conditions covered
   - [ ] All side effects verified
   - [ ] All outputs validated

4. Implementation Review:
   - [ ] No global state dependencies
   - [ ] Proper resource cleanup
   - [ ] Appropriate mocking
   - [ ] Clear assertions
   - [ ] Efficient execution

5. Documentation Check:
   - [ ] Purpose documented
   - [ ] Inputs described
   - [ ] Outputs specified
   - [ ] Assumptions listed
   - [ ] Edge cases noted

## Common Issues to Look For

1. False Positives:
   - Test passes but behavior is wrong
   - Test verifies wrong thing
   - Test doesn't check all outputs
   - Test makes invalid assumptions

2. Incomplete Testing:
   - Missing error cases
   - Untested configurations
   - Ignored edge cases
   - Unchecked side effects

3. Fragile Tests:
   - Implementation-dependent
   - Order-dependent
   - Environment-dependent
   - Timing-dependent

4. Resource Issues:
   - Leaks resources
   - Doesn't clean up
   - Race conditions
   - Deadlocks

5. Documentation Gaps:
   - Unclear purpose
   - Missing prerequisites
   - Undocumented assumptions
   - Incomplete specifications

## Action Items Template

For each issue found:

```markdown
## Test: [test_name]
### Issue
- Description: [what's wrong]
- Impact: [why it matters]
- Risk: [consequences]

### Resolution
- [ ] Action 1: [specific step]
- [ ] Action 2: [specific step]
- [ ] Verification: [how to confirm fix]

### Prevention
- [ ] Update guidelines
- [ ] Add checks
- [ ] Improve documentation
```

## Notes
- Run tests in isolation and in combination
- Verify both positive and negative cases
- Check resource cleanup
- Validate error handling
- Consider performance impact
- Document all assumptions
- Test realistic scenarios
- Consider security implications
