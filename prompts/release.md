# Release Process

This document outlines the step-by-step process for releasing a new version of aigrok.

## Pre-Release Checklist

1. Version Management
   ```bash
   # Review current version
   cat aigrok/__init__.py
   
   # Update version in __init__.py (single source of truth)
   # Replace X.Y.Z with actual version number, e.g., "0.3.2"
   # __version__ = "X.Y.Z"
   ```
   - Determine appropriate version bump (major/minor/patch)
   - If in doubt, make it a patch or minor. Only increment major if explicitly directed.

2. Testing
   ```bash
   # Run all tests
   python scripts/run_tests.py
   
   # Run cached tests for performance
   python scripts/run_cached_tests.py
   
   # Run installation test
   ./scripts/install_test.sh
   ```
   - Fix any failing tests before proceeding

3. Code Review
   ```bash
   # Show all uncommitted and staged changes
   git status
   git diff HEAD
   git diff --cached
   
   # Review specific files
   git diff HEAD -- aigrok/ tests/ docs/
   
   # Get list of changes since last tag
   git log --oneline $(git describe --tags --abbrev=0)..HEAD
   
   # Get detailed changes for specific components
   git log -p $(git describe --tags --abbrev=0)..HEAD -- aigrok/
   git log -p $(git describe --tags --abbrev=0)..HEAD -- tests/
   ```
   Review for:
   - Code changes: bug fixes, features, breaking changes
   - Documentation updates
   - Test coverage
   - Version consistency

3a. Update CHANGELOG.md
   ```bash
   # Open CHANGELOG.md and add new version section at the top
   # Format (replace X.Y.Z with actual version number):
   
   ## [X.Y.Z] (YYYY-MM-DD)
   
   ### Major Features
   # Add if there are significant new features or breaking changes
   * Feature description
   * Breaking change description with migration notes
   
   ### Added
   # New features and capabilities
   * New feature X added with capabilities A, B, C
   * New API endpoint for feature Y
   * New CLI command for operation Z
   
   ### Changed
   # Modified functionality and improvements
   * Enhanced component X with better performance
   * Updated dependency Y to version Z
   * Improved error handling in module A
   
   ### Fixed
   # Bug fixes and corrections
   * Fixed issue #123: Description of the fix
   * Resolved performance bottleneck in X
   * Corrected error handling in Y
   
   ### Testing
   # Test improvements and coverage
   * Added tests for new feature X
   * Improved test coverage for module Y
   * Current coverage metrics:
     - Core Components: XX%
     - API Layer: XX%
     - CLI Interface: XX%
   
   ### Documentation
   # Documentation updates
   * Updated API documentation for new features
   * Added migration guide for breaking changes
   * Improved installation instructions
   ```
   
   Guidelines for CHANGELOG updates:
   - Keep entries clear and concise
   - Include issue/PR numbers where relevant
   - Group related changes together
   - Highlight breaking changes prominently
   - Include migration guides if needed
   - Update coverage metrics if significant changes
   - Add any new dependencies or requirements
   - Document API changes thoroughly

4. Documentation Updates
   ```bash
   # Review and update README.md if needed
   ```

## Release Process

5. Git Operations
   ```bash
   # Stage changes
   git status
   # generate git add and git rm based on what is not staged
   git add .
   
   # Commit with version (replace X.Y.Z with actual version number)
   git commit -m "Release version X.Y.Z

   - Added: description of new features
   - Changed: description of changes
   - Fixed: description of bug fixes"
   
   # Create and push tag (replace X.Y.Z with actual version number)
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   git push origin main
   git push origin vX.Y.Z
   ```

6. GitHub Release
   ```bash
   # Create GitHub release (replace X.Y.Z with actual version number)
   gh release create vX.Y.Z \
     --title "aigrok vX.Y.Z" \
     --notes "## What's New
   
   ### Added
   - Description of new features
   
   ### Changed
   - Description of changes
   
   ### Fixed
   - Description of bug fixes
   
   For full details, see [CHANGELOG.md](CHANGELOG.md)"
   
   # Verify release page
   gh release view vX.Y.Z
   ```

7. Package Preparation
   ```bash
   # Clean old builds
   rm -rf dist/ build/ *.egg-info/
   
   # Build package
   python -m build
   
   # Verify package structure
   tar tzf dist/*.tar.gz
   unzip -l dist/*.whl
   ```


8. Test Release
   ```bash
   # Deploy to TestPyPI
   ./scripts/deploy_testpypi.sh
   
   # Test installation from TestPyPI (replace X.Y.Z with actual version)
   python -m pip install --index-url https://test.pypi.org/simple/ aigrok==X.Y.Z
   
   # Verify functionality
   python -c "import aigrok; print(aigrok.__version__)"
   ```

9. Production Release
   ```bash
   # Deploy to PyPI
   ./scripts/deploy_pypi.sh
   
   # Verify installation (replace X.Y.Z with actual version)
   python -m pip install --upgrade aigrok==X.Y.Z
   python -c "import aigrok; print(aigrok.__version__)"
   ```

## Post-Release Tasks

10. Verification
    ```bash
    # Verify PyPI package (replace X.Y.Z with actual version)
    python -m pip install --no-cache-dir aigrok==X.Y.Z
    
    # Run basic smoke test
    python -c "import aigrok; print(aigrok.__version__)"
    ```

11. Cleanup and Documentation
    - Close related GitHub issues and milestones
    - Update external documentation if needed
    - Announce release if appropriate

## Notes
- All scripts are in `scripts/` directory
- Ensure scripts are executable: `chmod +x scripts/*.sh`
- TestPyPI/PyPI deployments require appropriate credentials
- Installation tests require clean virtual environments
- Version numbers follow [Semantic Versioning](https://semver.org/)

## Troubleshooting

If deployment fails:
1. Check credentials are properly configured
2. Verify package builds correctly
3. Ensure version number is unique
4. Check PyPI/TestPyPI service status
