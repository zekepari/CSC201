#!/usr/bin/env python3
"""
Demo script for the Grocery Stock Management System.

Loads file paths supplied on argv and runs as the CLI does.
For local verification of expected outputs.

Usage:
    python scripts/run_demo.py input_01.txt input_05.txt
"""

import sys
import os
from pathlib import Path

# Add src to path so we can import the grocery module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from grocery.simulator import GrocerySimulator


def main():
    """Main demo entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_demo.py <input_file1> [<input_file2> ...]")
        print()
        print("Expected outputs:")
        print("  input_01.txt:")
        print("    Apple: 5")
        print("    Peer: 20")
        print("    Profit/Loss: $74.00")
        print()
        print("  input_05.txt:")
        print("    Profit/Loss: NA")
        return 1
    
    for file_path in sys.argv[1:]:
        print(f"--- {file_path} ---")
        
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            print()
            continue
            
        try:
            simulator = GrocerySimulator()
            simulator.run_file(file_path)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
