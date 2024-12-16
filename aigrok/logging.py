"""Logging configuration for aigrok."""
from loguru import logger
import sys

def configure_logging(verbose: bool = False):
    """Configure logging based on verbosity level.
    
    When verbose is False (default), all logging is disabled.
    When verbose is True, debug logging is enabled to stderr.
    """
    logger.remove()  # Remove default handler
    if verbose:
        logger.add(sys.stderr, level="DEBUG")
    # No else clause - logging remains disabled when not verbose
