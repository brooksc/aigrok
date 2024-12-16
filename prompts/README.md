# Aigrok Development Prompts

This directory contains prompts used to guide AI-assisted development of Aigrok. Each prompt is designed to be copied and pasted into a conversation with an AI assistant to guide specific development tasks.

## Development Cycle

1. **Add New Feature** (`feature.md`)
   - Copy the feature prompt into your AI conversation
   - Describe the feature you want to add
   - AI will guide implementation following our guidelines

2. **Test Changes** (`test.md`)
   - After implementation, use test prompt
   - AI will help create/update tests
   - Verify functionality and edge cases

3. **Update Documentation** (`docs.md`)
   - Use docs prompt to ensure all changes are documented
   - Update API documentation
   - Add usage examples
   - Update changelog

4. **Audit Changes** (`audit.md`)
   - Before release, audit all changes
   - Verify implementation matches requirements
   - Check for security issues
   - Ensure performance meets expectations

5. **Release** (`release.md`)
   - Prepare for release
   - Update version numbers
   - Finalize changelog
   - Create release notes

## Using Prompts

1. **Start a new AI conversation**
2. **Copy relevant prompt** into the conversation
3. **Describe your specific needs** related to the prompt
4. **Follow AI guidance** through the process

## Prompts Overview

- `feature.md`: Guide for implementing new features
- `test.md`: Ensure proper test coverage and functionality
- `docs.md`: Keep documentation in sync with changes
- `audit.md`: Review changes before release
- `release.md`: Prepare and publish releases

## Best Practices

1. **One Feature at a Time**
   - Complete the full cycle for each feature
   - Avoid mixing multiple features in one branch

2. **Regular Audits**
   - Run audit prompt after significant changes
   - Don't wait until release time

3. **Documentation First**
   - Update docs as you implement
   - Don't leave documentation for later

4. **Continuous Testing**
   - Add tests with new features
   - Run test suite frequently
