#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .

# Test command-line tool
echo "Testing aigrok command-line tool..."
aigrok --help

# Deactivate virtual environment
deactivate 