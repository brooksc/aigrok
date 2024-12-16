# Release Prompt

This prompt guides you through the process of releasing a new version.

1. Version Management
   - Review current version number
   - Determine appropriate version bump (major/minor/patch)
   - Update version in setup.py and __init__.py
   - Update any version-dependent documentation

2. Change Analysis
   - Review staged changes
   - Compare against last release
   - Document breaking changes
   - Update HISTORY.md with changes

3. Documentation Review
   - Verify README is up to date
   - Check API documentation accuracy
   - Update changelog
   - Review example code

4. Pre-release Checks
   - Run full test suite
   - Check code coverage
   - Verify all changes are committed
   - Review open issues and PRs

5. Git Operations
   - Review changes with `git status`
   - Stage changes:
     * Version updates
     * Documentation changes
     * Test updates
     * New features and fixes
   - Commit changes with descriptive message:
     * Include version number
     * List major changes
     * Reference relevant issues
   - Create version tag
   - Push to remote:
     * Push commits
     * Push tags
     * Verify push success

6. Package Release
   - Build distribution packages
   - Push to TestPyPI
   - Test installation from TestPyPI
   - Push to production PyPI

7. Post-release Tasks
   - Verify package installation
   - Update release documentation
   - Announce release if needed
   - Plan next version

8. Release Verification
   - Check GitHub release page
   - Verify package on PyPI
   - Test fresh installation
   - Review documentation links
