# Audit Prompt

This prompt guides you through auditing changes since the last checkpoint.

1. Get last checkpoint state
   - Review previous session summary
   - Note key features and changes
   - List known issues and TODOs

2. Analyze current state
   - Check git status for changes
   - Review modified files
   - List new files added

3. Compare implementations
   - Check each feature mentioned in last checkpoint
   - Verify functionality is preserved
   - Note any regressions or changes

4. Review documentation sync
   - Check if README is up to date
   - Verify HISTORY.md reflects changes
   - Update API documentation if needed

5. Security audit
   - Check for exposed credentials
   - Verify proper error handling
   - Review input validation

6. Performance check
   - Note any performance changes
   - Check resource usage
   - Verify timing constraints

7. Cleanup opportunities
   - Check for empty directories
   - Identify unused cache directories
   - Look for deprecated files
   - Check for:
     * Empty directories that can be removed
     * Unused test fixtures
     * Old cache files
     * Temporary files
     * Duplicate files
     * Orphaned documentation
     * Deprecated code paths
     * Unused dependencies
     * Old build artifacts
   - For each item found:
     * Document its location
     * Explain why it's no longer needed
     * Suggest appropriate cleanup action
     * Note any dependencies to consider
     * List potential risks of removal

8. Cleanup verification
   - Before removing any files:
     * Verify they are not referenced elsewhere
     * Check for hidden dependencies
     * Ensure no active features depend on them
     * Document the removal in HISTORY.md
     * Create a backup if needed
   - After cleanup:
     * Run all tests to verify no regressions
     * Check all builds still work
     * Verify documentation is still accurate
     * Update any relevant paths or references
