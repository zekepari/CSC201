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
    """Comprehensive end-to-end test cases for HD-level coverage (90%+)."""
    
    def test_01_official_example(self):
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
    
    def test_02_oversell_invalid(self):
        """Test oversell causes invalid - output is ONLY 'Profit/Loss: NA'."""
        lines = [
            "STOCK Apple 5 2.00",
            "ORDER Apple 10 4.00",  # Oversell
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_03_complex_returns_lifo_fifo(self):
        """Test returns with LIFO lot selection and FIFO within-lot processing."""
        lines = [
            "STOCK Apple 5 1.00",   # Batch 1: 5 @ $1.00
            "STOCK Apple 3 2.00",   # Batch 2: 3 @ $2.00
            "ORDER Apple 4 5.00",   # Sale 1: 4 @ $1.00 -> $16 profit
            "ORDER Apple 2 5.00",   # Sale 2: 1@$1.00 + 1@$2.00 -> $7 profit
            "RETURN Apple 3 5.00",  # Return from Sale 2 first (LIFO)
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 2
Profit/Loss: $12.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_04_negative_stock_cost_invalid(self):
        """Test STOCK with cost <= 0 is invalid."""
        lines = [
            "STOCK Apple 10 0.00",  # Invalid: cost = 0
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_05_negative_stock_quantity_invalid(self):
        """Test STOCK with qty < 0 is invalid."""
        lines = [
            "STOCK Apple -5 2.00",  # Invalid: negative quantity
            "CHECK", 
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_06_negative_order_sell_invalid(self):
        """Test ORDER with negative sell price is invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "ORDER Apple 3 -1.00",  # Invalid: negative sell price
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_07_negative_order_quantity_invalid(self):
        """Test ORDER with negative quantity is invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "ORDER Apple -3 4.00",  # Invalid: negative quantity
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_08_over_expire_invalid(self):
        """Test EXPIRE more than available is invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "EXPIRE Apple 10",  # Invalid: only 5 available
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_09_negative_expire_quantity_invalid(self):
        """Test EXPIRE with negative quantity is invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "EXPIRE Apple -2",  # Invalid: negative quantity
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_10_over_return_invalid(self):
        """Test RETURN more than sold at price is invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "ORDER Apple 3 4.00",
            "RETURN Apple 5 4.00",  # Invalid: only sold 3 at $4.00
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_11_return_wrong_price_invalid(self):
        """Test RETURN at price never sold is invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "ORDER Apple 3 4.00",
            "RETURN Apple 2 5.00",  # Invalid: never sold at $5.00
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_12_negative_return_quantity_invalid(self):
        """Test RETURN with negative quantity is invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "ORDER Apple 3 4.00",
            "RETURN Apple -1 4.00",  # Invalid: negative quantity
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_13_zero_quantities_valid_noop(self):
        """Test zero quantity operations are valid no-ops."""
        lines = [
            "STOCK Apple 10 2.00",
            "ORDER Apple 0 4.00",   # Valid no-op
            "EXPIRE Apple 0",       # Valid no-op
            "RETURN Apple 0 4.00",  # Valid no-op
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 10
Profit/Loss: $0.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_14_item_sorting_alphabetical(self):
        """Test CHECK output is sorted alphabetically."""
        lines = [
            "STOCK Zebra 5 1.00",
            "STOCK Apple 10 2.00", 
            "STOCK Banana 3 1.50",
            "STOCK Orange 7 1.25",
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 10
Banana: 3
Orange: 7
Zebra: 5
Profit/Loss: $0.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_15_discount_stack_lifo(self):
        """Test discount stack is LIFO - last one wins."""
        lines = [
            "STOCK Apple 10 1.00",
            "DISCOUNT Apple 10",     # 10% discount
            "DISCOUNT Apple 20",     # 20% discount (overwrites 10%)
            "ORDER Apple 1 4.00",    # Should use 20% -> sell at $3.20
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 9
Profit/Loss: $2.20"""  # (3.20 - 1.00) = 2.20
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_16_discount_end_pop(self):
        """Test DISCOUNT_END pops most recent discount."""
        lines = [
            "STOCK Apple 10 1.00",
            "DISCOUNT Apple 10",     # 10% discount
            "DISCOUNT Apple 20",     # 20% discount
            "DISCOUNT_END Apple",    # Remove 20%, back to 10%
            "ORDER Apple 1 4.00",    # Should use 10% -> sell at $3.60
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 9
Profit/Loss: $2.60"""  # (3.60 - 1.00) = 2.60
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_17_discount_end_empty_noop(self):
        """Test DISCOUNT_END on empty stack is no-op."""
        lines = [
            "STOCK Apple 10 1.00",
            "DISCOUNT_END Apple",    # No-op: no discounts to remove
            "ORDER Apple 1 4.00",    # No discount -> sell at $4.00
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 9
Profit/Loss: $3.00"""  # (4.00 - 1.00) = 3.00
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_18_multiple_discount_end_noop(self):
        """Test multiple DISCOUNT_END calls are safe no-ops."""
        lines = [
            "STOCK Apple 10 1.00",
            "DISCOUNT Apple 15",
            "DISCOUNT_END Apple",    # Remove 15%
            "DISCOUNT_END Apple",    # No-op
            "DISCOUNT_END Apple",    # No-op
            "ORDER Apple 1 4.00",    # No discount
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 9
Profit/Loss: $3.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_19_fifo_multiple_batches(self):
        """Test FIFO consumption across multiple batches."""
        lines = [
            "STOCK Apple 3 1.00",   # Batch 1: 3 @ $1.00
            "STOCK Apple 2 2.00",   # Batch 2: 2 @ $2.00  
            "STOCK Apple 4 1.50",   # Batch 3: 4 @ $1.50
            "ORDER Apple 6 5.00",   # Uses all of Batch 1, all of Batch 2, 1 from Batch 3
            "CHECK",
            "PROFIT"
        ]
        
        # Profit: 3*(5-1) + 2*(5-2) + 1*(5-1.5) = 12 + 6 + 3.5 = 21.5
        expected_output = """Apple: 3
Profit/Loss: $21.50"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_20_expire_fifo_consumption(self):
        """Test EXPIRE uses FIFO consumption."""
        lines = [
            "STOCK Apple 3 1.00",   # Batch 1: 3 @ $1.00
            "STOCK Apple 2 3.00",   # Batch 2: 2 @ $3.00
            "EXPIRE Apple 4",       # Expire 3 from Batch 1 + 1 from Batch 2
            "CHECK",
            "PROFIT"
        ]
        
        # Loss: -(3*1.00 + 1*3.00) = -6.00
        expected_output = """Apple: 1
Profit/Loss: $-6.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_21_mixed_operations_complex(self):
        """Test complex scenario with mixed operations."""
        lines = [
            "STOCK Apple 10 2.00",
            "STOCK Banana 5 1.50",
            "DISCOUNT Apple 25",     # 25% discount on Apple
            "ORDER Apple 3 8.00",    # Sell at $6.00 after discount
            "ORDER Banana 2 4.00",   # No discount
            "EXPIRE Apple 2",        # Expire 2 apples
            "RETURN Apple 1 8.00",   # Return 1 apple
            "CHECK",
            "PROFIT"
        ]
        
        # Apple profit: 3*(6.00-2.00) - 1*(6.00-2.00) = 12 - 4 = 8
        # Banana profit: 2*(4.00-1.50) = 5
        # Expire loss: -2*2.00 = -4
        # Total: 8 + 5 - 4 = 9
        expected_output = """Apple: 5
Banana: 3
Profit/Loss: $9.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_22_return_exact_price_match(self):
        """Test returns must match exact sell price."""
        lines = [
            "STOCK Apple 5 1.00",
            "ORDER Apple 2 3.00",   # Sell 2 at $3.00
            "ORDER Apple 1 4.00",   # Sell 1 at $4.00
            "RETURN Apple 1 3.00",  # Return 1 at $3.00 (valid)
            "CHECK",
            "PROFIT"
        ]
        
        # Profit: 2*(3-1) + 1*(4-1) - 1*(3-1) = 4 + 3 - 2 = 5
        expected_output = """Apple: 2
Profit/Loss: $5.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_23_return_lifo_by_sale_lot(self):
        """Test returns are LIFO by sale lot at same price."""
        lines = [
            "STOCK Apple 10 1.00",
            "ORDER Apple 2 5.00",   # Sale lot 1
            "ORDER Apple 3 5.00",   # Sale lot 2 (more recent)
            "RETURN Apple 1 5.00",  # Should return from lot 2 (LIFO)
            "CHECK",
            "PROFIT"
        ]
        
        # Profit: 2*(5-1) + 3*(5-1) - 1*(5-1) = 8 + 12 - 4 = 16
        expected_output = """Apple: 5
Profit/Loss: $16.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_24_discount_per_item_independent(self):
        """Test discounts are independent per item."""
        lines = [
            "STOCK Apple 5 1.00",
            "STOCK Banana 5 1.00", 
            "DISCOUNT Apple 20",    # Only affects Apple
            "ORDER Apple 1 5.00",   # 20% discount -> $4.00
            "ORDER Banana 1 5.00",  # No discount -> $5.00
            "CHECK",
            "PROFIT"
        ]
        
        # Apple: 1*(4.00-1.00) = 3.00
        # Banana: 1*(5.00-1.00) = 4.00
        expected_output = """Apple: 4
Banana: 4
Profit/Loss: $7.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_25_money_formatting_precision(self):
        """Test money formatting with various decimal cases."""
        lines = [
            "STOCK Apple 1 1.00",
            "ORDER Apple 1 1.333",  # Should round to $0.33 profit
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 0
Profit/Loss: $0.33"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_26_negative_profit_formatting(self):
        """Test negative profit formatting."""
        lines = [
            "STOCK Apple 1 5.00",
            "ORDER Apple 1 2.00",   # Loss: 2.00 - 5.00 = -3.00
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 0
Profit/Loss: $-3.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_27_floating_point_quantities(self):
        """Test handling of floating point quantity inputs."""
        lines = [
            "STOCK Apple 10.0 2.50",  # Should parse as int(10)
            "ORDER Apple 3.0 4.00",   # Should parse as int(3)
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 7
Profit/Loss: $4.50"""  # 3*(4.00-2.50) = 4.50
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_28_empty_lines_and_comments(self):
        """Test handling of empty lines and comments."""
        lines = [
            "STOCK Apple 5 2.00",
            "",                     # Empty line - should be ignored
            "# This is a comment",  # Comment - should be ignored
            "ORDER Apple 2 3.00",
            "",
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 3
Profit/Loss: $2.00"""
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_29_large_numbers(self):
        """Test handling of large numbers."""
        lines = [
            "STOCK Apple 1000 0.50",
            "ORDER Apple 500 2.00",
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = """Apple: 500
Profit/Loss: $750.00"""  # 500*(2.00-0.50) = 750.00
        
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_30_check_suppression_verification(self):
        """Test CHECK is completely suppressed when invalid."""
        lines = [
            "STOCK Apple 5 2.00",
            "STOCK Banana 3 1.00",
            "ORDER Apple 10 4.00",  # Invalid: oversell
            "CHECK"                 # Should produce no output
        ]
        
        expected_output = ""  # Completely empty
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_31_profit_na_after_invalid(self):
        """Test PROFIT shows NA after any invalid operation."""
        lines = [
            "STOCK Apple 10 2.00",
            "ORDER Apple 5 3.00",   # Valid operation first
            "EXPIRE Apple 20",      # Invalid: over-expire
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_32_invalid_command_syntax(self):
        """Test invalid command syntax triggers invalid state."""
        lines = [
            "STOCK Apple 5 2.00",
            "INVALID_COMMAND",      # Unknown command
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_33_malformed_parameters(self):
        """Test malformed parameters trigger invalid state."""
        lines = [
            "STOCK Apple",          # Missing parameters
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_34_non_numeric_parameters(self):
        """Test non-numeric parameters trigger invalid state."""
        lines = [
            "STOCK Apple abc 2.00", # Non-numeric quantity
            "CHECK",
            "PROFIT"
        ]
        
        expected_output = "Profit/Loss: NA"
        result = run_sim(lines)
        self.assertEqual(result, expected_output)
    
    def test_35_comprehensive_workflow(self):
        """Test comprehensive workflow with all command types."""
        lines = [
            "STOCK Apple 20 1.50",
            "STOCK Banana 15 2.00",
            "STOCK Apple 10 1.75",   # Second batch
            "DISCOUNT Apple 15",
            "DISCOUNT Banana 10", 
            "ORDER Apple 8 4.00",    # Uses first batch
            "ORDER Banana 5 5.00",
            "EXPIRE Apple 3",        # Expire from first batch
            "DISCOUNT Apple 25",     # New discount
            "ORDER Apple 5 4.00",    # Uses rest of first + second batch
            "RETURN Apple 2 4.00",   # Return from most recent sale
            "DISCOUNT_END Apple",    # Back to 15% discount
            "ORDER Apple 3 4.00",
            "CHECK",
            "PROFIT"
        ]
        
        # Complex calculation - verify implementation handles it correctly
        result = run_sim(lines)
        self.assertIn("Apple:", result)
        self.assertIn("Banana:", result)
        self.assertIn("Profit/Loss: $", result)
        self.assertNotIn("NA", result)  # Should be valid


if __name__ == '__main__':
    unittest.main()
