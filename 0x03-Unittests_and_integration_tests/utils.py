#!/usr/bin/env python3
"""
Utility functions
"""
from typing import Dict, Tuple, Any


def access_nested_map(nested_map: Dict, path: Tuple[str]) -> Any:
    """
    Access nested map with key path
    
    Args:
        nested_map: A nested dictionary
        path: A tuple representing the path of keys to access
        
    Returns:
        The value at the nested path
        
    Example:
        >>> access_nested_map({"a": 1}, ("a",))
        1
        >>> access_nested_map({"a": {"b": 2}}, ("a",))
        {"b": 2}
        >>> access_nested_map({"a": {"b": 2}}, ("a", "b"))
        2
    """
    result = nested_map
    for key in path:
        result = result[key]
    return result
