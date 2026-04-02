#!/usr/bin/env python3
"""
Desktop App GUI Module Init
"""

try:
    from .simple_gui import (
        ConfigInterface,
        GUIConfig,
        ConsoleConfig,
        ConfigurationService
    )
except ImportError:
    pass

__all__ = [
    'ConfigInterface',
    'GUIConfig',
    'ConsoleConfig',
    'ConfigurationService'
]
