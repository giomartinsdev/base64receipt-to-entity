"""
Text Processing Utility Module

This module provides utility functions for text processing,
such as applying regular expression patterns to extract information.
"""

import re
from typing import Optional, Pattern, Union


def apply_regex(text: str, pattern: Union[str, Pattern]) -> Optional[str]:
    """
    Apply a regular expression pattern to text and return the first match.
    
    Args:
        text (str): The text to search for pattern matches
        pattern (Union[str, Pattern]): Regular expression pattern to match
        
    Returns:
        Optional[str]: The first matching string, or None if no matches found
    """
    matches = re.findall(pattern, text)
    return matches[0] if matches else None
