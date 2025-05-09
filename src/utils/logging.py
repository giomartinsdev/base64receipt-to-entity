"""
Logging Configuration Module

This module provides utilities for setting up and configuring logging
throughout the application.
"""

import logging
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger with the specified name and level.
    
    This function configures a logger with appropriate formatting for
    consistent logging across the application.
    
    Args:
        name (str): The name of the logger
        level (int, optional): The logging level. Defaults to logging.INFO
        
    Returns:
        logging.Logger: A configured logger instance
    """
    # Configure basic logging format
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger(name)
