#!/usr/bin/env python3
"""
Script to run test cases from test_cases.json
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path so we can import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test runner before other modules to avoid CLI argument parsing
from test_runner import TestRunner

# Now import the rest
from aigrok.formats import get_supported_formats

def main():
    """Run all test cases."""
    runner = TestRunner()
    try:
        runner.run_all()
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 