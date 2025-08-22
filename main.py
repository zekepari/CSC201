#!/usr/bin/env python3
"""
Main entry point for the Grocery Stock Management System.

This is a thin wrapper that delegates to the CLI module.
"""

import sys
from src.grocery.cli import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
