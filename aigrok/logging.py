"""Logging configuration for aigrok."""
from loguru import logger
import sys

_configured = False
_verbose = False

def configure_logging(verbose: bool = False):
    """Configure logging based on verbosity level.
    
    When verbose is False (default), all logging is disabled.
    When verbose is True, debug logging is enabled to stderr.
    
    This function is idempotent - calling it multiple times with the same
    verbosity level will not change the configuration.
    """
    global _configured, _verbose
    
    # If already configured with same verbosity, do nothing
    if _configured and verbose == _verbose:
        return
        
    # Remove all existing handlers
    logger.remove()
    
    # Update state
    _configured = True
    _verbose = verbose
    
    # Add handler only if verbose
    if verbose:
        logger.add(sys.stderr, level="DEBUG")
