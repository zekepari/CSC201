"""
End-to-end tests for the Grocery Stock Management System.

Tests verify the complete workflow using only standard library with inline test data.
"""

import unittest
from io import StringIO
import sys
from src.grocery.simulator import GrocerySimulator


def run_sim(lines: list[str]) -> str:
    """Helper function to run simulator and capture stdout."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        simulator = GrocerySimulator()
        for line in lines:
            simulator.process_line(line)
        return captured_output.getvalue().rstrip()
    finally:
        sys.stdout = old_stdout


class TestEndToEnd(unittest.TestCase):
    """End-to-end test cases using only standard library."""
    
    def test_1_example(self):
        """Test the official example from CSC201 Task 1 specification."""
        lines = [
            "STOCK Apple 100 1.00",
            "ORDER Apple 50 2.00",
            "STOCK Peer 20 1.50", 
            "DISCOUNT Apple 10",
            "ORDER Apple 20 2.00",
            "DISCOUNT Apple 5",
            "ORDER Apple 10 2.00",
            "DISCOUNT_END Apple",
            "ORDER Apple 10 2.00",
            "RETURN Apple 5 2.00",
            "EXPIRE Apple 5",
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 5
Peer: 20
Profit/Loss: $74.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_2_invalid(self):
        """Test oversell causes invalid - output is ONLY 'Profit/Loss: NA' (no CHECK lines)."""
        lines = [
            "STOCK Apple 5 2.00",
            "ORDER Apple 10 4.00",  # Oversell - only 5 available but trying to sell 10
            "CHECK",
            "PROFIT"
        ]
        
        # Invalid state suppresses CHECK output, only shows NA at PROFIT
        expected_output = "Profit/Loss: NA"
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_3_returns_lifo_fifo(self):
        """Test returns with LIFO lot selection and FIFO within-lot processing."""
        lines = [
            # Create two batches with different costs
            "STOCK Apple 5 1.00",   # Batch 1: 5 @ $1.00 each
            "STOCK Apple 3 2.00",   # Batch 2: 3 @ $2.00 each
            
            # First ORDER: sell 4 units at $5.00 each (uses 4 from Batch 1 @ $1.00)
            "ORDER Apple 4 5.00",   # Profit: 4*(5.00-1.00) = $16.00
            
            # Second ORDER: sell 2 units at $5.00 each (uses 1 from Batch 1 @ $1.00, 1 from Batch 2 @ $2.00)  
            "ORDER Apple 2 5.00",   # Profit: 1*(5.00-1.00) + 1*(5.00-2.00) = $4.00 + $3.00 = $7.00
            
            # RETURN 3 units at $5.00 (LIFO: return from second order first, then first order)
            # Return from second order: 2 units (1 @ $1.00, 1 @ $2.00) -> reverse profit: -(4.00+3.00) = -$7.00
            # Return from first order: 1 unit @ $1.00 -> reverse profit: -4.00 = -$4.00  
            "RETURN Apple 3 5.00",  # Total return profit: -$7.00 - $4.00 = -$11.00
            
            "CHECK",
            "PROFIT"
        ]
        
        # Final calculation:
        # Initial profit: $16.00 + $7.00 = $23.00
        # Return profit: -$11.00
        # Final profit: $23.00 - $11.00 = $12.00
        # Remaining inventory: 8 - 6 = 2 (returns don't re-add to inventory)
        expected_output = """Apple: 2
Profit/Loss: $12.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
