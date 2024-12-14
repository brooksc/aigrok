#!/usr/bin/env python3
"""
Script to run test cases with caching and logging.
"""
import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Set

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add tests directory to Python path
tests_dir = project_root / "tests"
sys.path.insert(0, str(tests_dir))

from test_runner import TestRunner, TestResult

def setup_logging(log_dir: Path) -> logging.Logger:
    """Setup logging configuration."""
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"test_run_{timestamp}.log"
    
    # File handler with detailed format
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    
    # Console handler with simpler format
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', 
                         datefmt='%H:%M:%S')
    )
    
    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class CachedTestRunner(TestRunner):
    """Test runner with caching support."""
    
    def __init__(self, cache_file: Path, logger: logging.Logger):
        super().__init__()
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()
        self.logger = logger
        
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load test results cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading cache: {e}")
        return {}
    
    def _save_cache(self) -> None:
        """Save test results to cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")
    
    def run_test(self, test_case: Dict[str, Any]) -> TestResult:
        """Run a test case with caching."""
        name = test_case.get("name", "unnamed_test")
        method = test_case.get("method", "")
        
        # Create cache key from test name and relevant parameters
        cache_key = f"{name}_{method}"
        
        # Check if we have a cached result and if --force wasn't specified
        if not sys.argv[1:] == ["--force"] and cache_key in self.cache:
            cached = self.cache[cache_key]
            if cached.get("success"):
                self.logger.info(f"Using cached result for {name} (passed)")
                return TestResult(
                    success=True,
                    output=cached.get("output"),
                    expected=cached.get("expected"),
                    actual=cached.get("actual"),
                    duration=cached.get("duration", 0.0)
                )
        
        # Run the test
        self.logger.info(f"Running test: {name}")
        start_time = time.time()
        result = super().run_test(test_case)
        duration = time.time() - start_time
        
        status = "PASSED" if result.success else "FAILED"
        self.logger.info(f"Test {name} {status} in {duration:.2f}s")
        
        # Log detailed failure information
        if not result.success:
            self.logger.error(f"Test {name} failed:")
            if result.error:
                self.logger.error(f"Error: {result.error}")
            self.logger.error(f"Expected: {result.expected}")
            self.logger.error(f"Actual: {result.actual}")
        
        # Cache the result
        self.cache[cache_key] = {
            "success": result.success,
            "output": result.output,
            "expected": result.expected,
            "actual": result.actual,
            "duration": result.duration,
            "timestamp": time.time()
        }
        self._save_cache()
        
        return result

    def run_all(self) -> None:
        """Run all test cases."""
        test_cases_file = self.test_dir / "test_cases.json"
        if not test_cases_file.exists():
            self.logger.error(f"Test cases file not found: {test_cases_file}")
            return
            
        try:
            with open(test_cases_file) as f:
                data = json.load(f)
                
            # Flatten the nested test case structure
            test_cases = []
            for category in data.values():
                for test_group in category.values():
                    if isinstance(test_group, list):
                        test_cases.extend(test_group)
            
            total = len(test_cases)
            self.logger.info(f"Found {total} tests to run")
            self.logger.info("Starting test run...")
            
            for i, test_case in enumerate(test_cases, 1):
                name = test_case.get("name", "unnamed_test")
                self.logger.info(f"Test {i}/{total}: {name}")
                result = self.run_test(test_case)
                self.results[name] = result
                self.stats.update(result)
                
                # Print progress
                passed = self.stats.passed
                failed = self.stats.failed
                remaining = total - (passed + failed)
                self.logger.info(f"Progress: {passed} passed, {failed} failed, {remaining} remaining")
                
            self._print_results()
            
        except Exception as e:
            self.logger.error(f"Error running tests: {e}")
            raise

def main():
    """Run all test cases with caching and logging."""
    # Setup paths
    cache_dir = Path("tests/.cache")
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / "test_results.json"
    
    log_dir = Path("tests/logs")
    logger = setup_logging(log_dir)
    
    try:
        # Initialize runner with logger
        runner = CachedTestRunner(cache_file, logger)
        
        # Run tests
        logger.info("Starting test run")
        start_time = time.time()
        
        runner.run_all()
        
        # Log results
        duration = time.time() - start_time
        logger.info("\nTest Results Summary")
        logger.info("===================")
        logger.info(f"Total Tests: {runner.stats.total}")
        logger.info(f"Passed: {runner.stats.passed}")
        logger.info(f"Failed: {runner.stats.failed}")
        logger.info(f"Skipped: {runner.stats.skipped}")
        logger.info(f"Total Duration: {duration:.2f}s")
        
        if runner.stats.failed > 0:
            logger.info("\nFailed Tests Details")
            logger.info("===================")
            for name, result in runner.results.items():
                if not result.success:
                    logger.info(f"\nTest: {name}")
                    if result.error:
                        logger.error(f"Error: {result.error}")
                    logger.info(f"Expected: {result.expected}")
                    logger.info(f"Actual: {result.actual}")
                    logger.info(f"Duration: {result.duration:.2f}s")
        
        # Exit with appropriate code
        sys.exit(1 if runner.stats.failed > 0 else 0)
        
    except KeyboardInterrupt:
        logger.warning("\nTest run interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 