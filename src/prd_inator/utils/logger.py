"""Logging configuration."""
import logging
import os
from typing import Optional


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Setup logger with DEBUG level if DEBUG env var is true."""
    logger = logging.getLogger(name or "prd_inator")
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(levelname)s [%(name)s] %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set level based on DEBUG env var
        debug = os.getenv("DEBUG", "false").lower() == "true"
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    return logger


# Global logger instance
logger = setup_logger()
