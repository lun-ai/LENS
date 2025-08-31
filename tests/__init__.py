"""
Test suite for Advanced Meta Strategy Learning Framework

This package contains comprehensive unit tests and integration tests for all
framework components.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path for imports
test_dir = Path(__file__).parent
src_dir = test_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# Test configuration
TEST_DATA_DIR = test_dir / "test_data"
TEST_RESULTS_DIR = test_dir / "test_results"

# Ensure test directories exist
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_RESULTS_DIR.mkdir(exist_ok=True)

__version__ = "1.0.0"
