"""
physimlab - A comprehensive physics simulation framework for scientific research and engineering analysis.

physimlab provides a flexible, extensible platform for simulating physical systems
with support for various physics models, numerical methods, and output formats.
"""

__version__ = "0.1.0"
__author__ = "physimlab Development Team"
__license__ = "Apache 2.0"

from .core import run_simulation, batch_simulation, compare_results
from .cli import app

__all__ = [
    "run_simulation",
    "batch_simulation", 
    "compare_results",
    "app"
]