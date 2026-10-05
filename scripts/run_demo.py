"""
Single-Command Demonstration Runner for Capstone Review 1.

Usage:
    python scripts/run_demo.py
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cloud_m7.cli import run_full_pipeline_demo

if __name__ == "__main__":
    run_full_pipeline_demo()
