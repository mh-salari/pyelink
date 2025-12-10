"""Display window management for multiple backends.

This module provides backend-agnostic window management for pygame, psychopy,
and pyglet. The tracker creates and owns the display window, which users can
access directly or through helper methods.

Backend classes are imported lazily to avoid ImportError when backend not installed.
"""

from .base import BaseDisplay

__all__ = [
    "BaseDisplay",
]
