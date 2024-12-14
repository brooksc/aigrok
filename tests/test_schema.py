"""
Test case schema validation.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
from pathlib import Path
import pytest

@dataclass
class TestCaseValidationError(Exception):
    """Custom exception for test case validation errors."""
    message: str
    test_case: Optional[Dict[str, Any]] = None

def validate_test_case(test_case: Dict[str, Any]) -> None:
    """Validate a single test case.
    
    Args:
        test_case: Test case dictionary to validate
    
    Raises:
        TestCaseValidationError: If validation fails
    """
    required_fields = ["name", "category", "file"]
    for field in required_fields:
        if field not in test_case:
            raise TestCaseValidationError(
                f"Missing required field: {field}",
                test_case
            )
    
    # Validate category-specific fields
    category = test_case["category"]
    if category == "performance":
        if "max_slowdown_factor" in test_case:
            factor = test_case["max_slowdown_factor"]
            if not isinstance(factor, (int, float)) or factor <= 0:
                raise TestCaseValidationError(
                    "max_slowdown_factor must be a positive number",
                    test_case
                )
    
    # Validate file exists
    file_path = Path(test_case["file"])
    if not file_path.exists():
        raise TestCaseValidationError(
            f"Test file not found: {file_path}",
            test_case
        )

def validate_test_cases(test_file: str = "tests/test_cases.json") -> None:
    """Validate all test cases in a JSON file.
    
    Args:
        test_file: Path to test cases JSON file
    
    Raises:
        TestCaseValidationError: If validation fails
    """
    try:
        with open(test_file) as f:
            test_cases = json.load(f)
    except Exception as e:
        raise TestCaseValidationError(f"Error loading test cases: {e}")
    
    for test_case in test_cases:
        validate_test_case(test_case)