"""
Pytest configuration and shared fixtures.

This file is automatically loaded by pytest and sets up the test environment.
"""

import sys
import os

# Add the parent directory to Python path so tests can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
