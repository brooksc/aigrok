# Release Prompt

This prompt guides you through the process of releasing a new version.

1. Version Management
   - Review current version number
   - Determine appropriate version bump (major/minor/patch)
   - Update version in setup.py and __init__.py
   - Update any version-dependent documentation

2. Pre-release Checks
   - Run full test suite
   - Check code coverage
   - Verify all changes are committed
   - Review open issues and PRs
   - Run installation test:
     ```bash
     ./scripts/install_test.sh
     ```
   - Verify CLI functionality works

3. Change Analysis
   - Review staged changes
   - Compare against last release
   - Document breaking changes
   - Update CHANGELOG.md with changes

4. Documentation Review
   - Verify README is up to date
   - Check API documentation accuracy
   - Review example code


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

6. GitHub Release
   - Create GitHub release using `gh release create`:
     * Use version tag (e.g., v0.3.0)
     * Add descriptive title
     * Include detailed release notes:
       - Major changes
       - Documentation updates
       - Code quality improvements
       - Breaking changes (if any)
       - Migration guides (if needed)
   - Verify release page
   - Check release assets

7. Package Release
   - Deploy to TestPyPI first:
     ```bash
     ./scripts/deploy_testpypi.sh
     ```
   - Test installation from TestPyPI
   - Deploy to production PyPI:
     ```bash
     ./scripts/deploy_pypi.sh
     ```
   - Verify package upload

8. Post-release Tasks
   - Create fresh virtual environment
   - Test package installation:
     ```bash
     python -m pip install aigrok
     ```
   - Verify CLI functionality
   - Update release documentation
   - Announce release if needed
   - Plan next version

9. Release Verification
   - Check GitHub release page
   - Verify package on PyPI
   - Test fresh installation
   - Review documentation links

## Notes
- All scripts are located in the `scripts/` directory
- Scripts require appropriate permissions (`chmod +x scripts/*.sh`)
- TestPyPI deployment requires TestPyPI credentials
- PyPI deployment requires PyPI credentials
- Installation test requires a clean virtual environment
