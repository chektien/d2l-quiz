#!/usr/bin/env python3
"""
Simple test runner that works without external dependencies.

Usage:
    python3 run_tests.py          # Run all tests
    python3 run_tests.py -v       # Run with verbose output
"""

import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    """Discover and run all tests."""
    loader = unittest.TestLoader()
    start_dir = "tests"
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Check for verbosity flag
    verbosity = 2 if "-v" in sys.argv or "--verbose" in sys.argv else 1

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
