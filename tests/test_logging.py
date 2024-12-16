"""Test cases for logging configuration."""
import sys
import io
from loguru import logger
from aigrok.logging import configure_logging

def test_logging_disabled_by_default():
    """Test that logging is disabled when verbose=False."""
    # Capture stderr
    stderr = io.StringIO()
    sys.stderr = stderr
    
    # Configure logging with verbose=False
    configure_logging(verbose=False)
    
    # Try to log something
    logger.debug("This should not appear")
    logger.info("This should not appear")
    logger.error("This should not appear")
    
    # Check that nothing was logged
    assert stderr.getvalue() == ""
    
    # Reset stderr
    sys.stderr = sys.__stderr__

def test_logging_enabled_with_verbose():
    """Test that debug logging is enabled when verbose=True."""
    # Capture stderr
    stderr = io.StringIO()
    sys.stderr = stderr
    
    # Configure logging with verbose=True
    configure_logging(verbose=True)
    
    # Try to log something
    logger.debug("Debug message")
    
    # Check that debug message was logged
    output = stderr.getvalue()
    assert "DEBUG" in output
    assert "Debug message" in output
    
    # Reset stderr
    sys.stderr = sys.__stderr__
