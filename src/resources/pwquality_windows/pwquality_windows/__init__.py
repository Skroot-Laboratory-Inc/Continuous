"""
PWQuality Windows - Ubuntu python-pwquality compatible interface for Windows
"""

from .core import PWQSettings, PWQError, check_password, generate_password

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Windows-compatible interface replicating Ubuntu python-pwquality package"

__all__ = [
    'PWQSettings',
    'PWQError',
    'check_password',
    'generate_password'
]