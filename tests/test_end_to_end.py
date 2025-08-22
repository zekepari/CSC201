"""
End-to-end tests for the Grocery Stock Management System.

These tests verify the complete workflow from command file processing
to profit calculation and output formatting.
"""

import unittest
from io import StringIO
import sys
from src.grocery.simulator import GrocerySimulator


def run_sim(text: str) -> str:
    """Helper function to run simulator and capture stdout."""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        simulator = GrocerySimulator()
        for line in text.strip().split('\n'):
            simulator.process_line(line)
        return captured_output.getvalue().rstrip()
    finally:
        sys.stdout = old_stdout


class TestEndToEnd(unittest.TestCase):
    """End-to-end test cases for the grocery management system."""
    
    def test_example_scenario(self):
        """Test the main example scenario matching task requirements."""
        # This creates a scenario that results in $74.00 profit as specified
        commands = """
STOCK Apple 10 2.00
STOCK Peer 25 1.00
ORDER Apple 5 16.00
ORDER Peer 5 1.80
CHECK
PROFIT
        """
        
        # Apple: 5 @ $16.00, cost $2.00 -> profit = 5*($16.00-$2.00) = $70.00  
        # Peer: 5 @ $1.80, cost $1.00 -> profit = 5*($1.80-$1.00) = $4.00
        # Total: $74.00
        expected_output = """Apple: 5
Peer: 20
Profit/Loss: $74.00"""
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_insufficient_stock_error(self):
        """Test error case - ordering more than available stock."""
        commands = """
STOCK Apple 5 2.00
ORDER Apple 10 4.00
CHECK
PROFIT
        """
        
        expected_output = "Profit/Loss: NA"
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_lifo_returns_scenario(self):
        """Test LIFO returns by sale lot and FIFO within lot."""
        commands = """
STOCK Apple 10 2.00
ORDER Apple 3 4.00
ORDER Apple 2 4.00
RETURN Apple 1 4.00
CHECK
PROFIT
        """
        
        # Should return from the most recent sale (2 units) first
        # Profit: 3*(4-2) + 2*(4-2) - 1*(4-2) = 6 + 4 - 2 = 8
        # Inventory remains 5 (returns don't re-add to inventory)
        expected_output = """Apple: 5
Profit/Loss: $8.00"""
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_discount_stack_behavior(self):
        """Test LIFO discount stack behavior."""
        commands = """
STOCK Apple 10 2.00
DISCOUNT Apple 10
DISCOUNT Apple 20
ORDER Apple 2 4.00
DISCOUNT_END Apple
ORDER Apple 2 4.00
CHECK
PROFIT
        """
        
        # First order: 20% discount -> sell at 3.20, profit = 2*(3.20-2.00) = 2.40
        # Second order: 10% discount -> sell at 3.60, profit = 2*(3.60-2.00) = 3.20
        # Total profit = 2.40 + 3.20 = 5.60
        expected_output = """Apple: 6
Profit/Loss: $5.60"""
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_invalid_return_more_than_sold(self):
        """Test error case - returning more than sold at specific price."""
        commands = """
STOCK Apple 5 2.00
ORDER Apple 3 4.00
RETURN Apple 5 4.00
CHECK
PROFIT
        """
        
        expected_output = "Profit/Loss: NA"
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_expire_operation(self):
        """Test EXPIRE command reduces inventory and profit."""
        commands = """
STOCK Apple 10 2.00
EXPIRE Apple 3
CHECK
PROFIT
        """
        
        # Expiring 3 units costs 3*2.00 = 6.00 in profit
        expected_output = """Apple: 7
Profit/Loss: $-6.00"""
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_zero_quantity_operations(self):
        """Test zero quantity operations are no-ops and not invalid."""
        commands = """
STOCK Apple 10 2.00
ORDER Apple 0 4.00
RETURN Apple 0 4.00
EXPIRE Apple 0
CHECK
PROFIT
        """
        
        expected_output = """Apple: 10
Profit/Loss: $0.00"""
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_negative_values_invalid(self):
        """Test negative quantities and prices make operations invalid."""
        commands = """
STOCK Apple -1 2.00
CHECK
PROFIT
        """
        
        expected_output = "Profit/Loss: NA"
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_zero_cost_invalid(self):
        """Test zero or negative cost makes STOCK invalid."""
        commands = """
STOCK Apple 10 0.00
CHECK
PROFIT
        """
        
        expected_output = "Profit/Loss: NA"
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)
    
    def test_multiple_items_sorted_output(self):
        """Test CHECK output is sorted by item name."""
        commands = """
STOCK Zebra 5 1.00
STOCK Apple 10 2.00
STOCK Banana 3 1.50
CHECK
PROFIT
        """
        
        expected_output = """Apple: 10
Banana: 3
Zebra: 5
Profit/Loss: $0.00"""
        
        result = run_sim(commands)
        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
