"""
Output management module.

Contains classes for managing simulation outputs including files, plots, and reports.
"""

from .manager import OutputManager
from .result import Result

__all__ = ['OutputManager', 'Result']