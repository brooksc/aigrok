#!/bin/bash
set -e  # Exit on error

# Clean up old builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Upload to PyPI
python -m twine upload dist/*
