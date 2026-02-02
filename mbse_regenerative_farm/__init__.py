"""
MBSE Regenerative Farm Framework

A comprehensive Model-Based Systems Engineering framework for regenerative agriculture,
capable of simulating ecosystem services, carbon sequestration, and nutrient cycling.
"""

__version__ = "1.0.0"
__author__ = "Edison Bros Systems Engineering"

from .regenerative_farm_system import RegenerativeFarmSystem
from .regenerative_index import calculate_regenerative_index

__all__ = [
    "RegenerativeFarmSystem",
    "calculate_regenerative_index",
]
