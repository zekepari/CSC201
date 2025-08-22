"""
Command-line interface for the Grocery Stock Management System.

Handles file processing, output formatting, and multiple file processing.
"""

from .simulator import GrocerySimulator

__all__ = ["main"]


def main(argv: list[str]) -> int:
    """Main CLI entry point."""
    if len(argv) < 2:
        print("Usage: python main.py <input_file1> [<input_file2> ...]")
        return 1
    
    for path in argv[1:]:
        print(f"--- {path} ---")
        simulator = GrocerySimulator()
        simulator.run_file(path)
        print()
    
    return 0
