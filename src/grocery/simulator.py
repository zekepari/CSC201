"""
Command processor for the Grocery Stock Management System.

This module handles parsing and executing commands like STOCK, ORDER, EXPIRE, etc.
and maintains the profit/loss calculations.
"""

from collections import defaultdict, deque
from typing import Dict, List
from .models import Batch, SaleComponent, SaleLot, Inventory, DiscountStack, SalesHistory


class GrocerySimulator:
    """Processes grocery store commands and maintains state."""
    
    def __init__(self):
        self.inventory: Inventory = defaultdict(deque)
        self.discounts: DiscountStack = defaultdict(list)
        self.sales: SalesHistory = defaultdict(lambda: defaultdict(list))
        self.profit: float = 0.0
        self.invalid: bool = False
    
    def _active_discount(self, item: str) -> float:
        """Get the active discount percentage for an item."""
        if self.discounts[item]:
            return self.discounts[item][-1]  # Last discount (LIFO)
        return 0.0
    
    def _total_available(self, item: str) -> int:
        """Get total available quantity for an item."""
        return sum(batch.qty for batch in self.inventory[item])
    
    def _money(self, value: float) -> str:
        """Format money value to 2 decimal places."""
        return f"${value:.2f}"
    
    def process_line(self, line: str) -> None:
        """
        Process a single command line.
        
        Rules:
        - STOCK: qty≥0, cost>0, else invalid. qty=0 is no-op.
        - ORDER: qty≥0, sell≥0, else invalid. qty=0 is no-op. Insufficient stock → invalid.
        - EXPIRE: qty≥0, else invalid. qty=0 is no-op. Insufficient stock → invalid.
        - RETURN: qty≥0, else invalid. qty=0 is no-op. Must match exact sell price and quantity.
        - DISCOUNT: Pushes percentage onto LIFO stack for item.
        - DISCOUNT_END: Pops from stack if present, no-op if empty.
        - CHECK: Prints nothing if invalid, otherwise shows all items with current inventory.
        - PROFIT: Shows "Profit/Loss: NA" if invalid, otherwise formatted profit.
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return
            
        try:
            parts = line.split()
            if not parts:
                return
                
            command = parts[0]
            
            # Allow CHECK and PROFIT even when invalid, but block other commands
            if self.invalid and command not in ("CHECK", "PROFIT"):
                return
            
            if command == "STOCK":
                if len(parts) != 4:
                    self.invalid = True
                    return
                item, qty_str, cost_str = parts[1], parts[2], parts[3]
                qty = int(float(qty_str))  # Handle "10.0" format
                cost = float(cost_str)
                
                if qty < 0 or cost <= 0:
                    self.invalid = True
                    return
                    
                if qty > 0:
                    self.inventory[item].append(Batch(qty, cost))
                    
            elif command == "ORDER":
                if len(parts) != 4:
                    self.invalid = True
                    return
                item, qty_str, sell_str = parts[1], parts[2], parts[3]
                qty = int(float(qty_str))  # Handle "10.0" format
                sell = float(sell_str)
                
                if qty < 0 or sell < 0:
                    self.invalid = True
                    return
                    
                if qty > 0:
                    if self._total_available(item) < qty:
                        self.invalid = True
                        return
                        
                    # Apply discount
                    discount_pct = self._active_discount(item)
                    sell_after_discount = sell * (1 - discount_pct / 100)
                    
                    # Consume FIFO batches
                    components = deque()
                    remaining_qty = qty
                    
                    while remaining_qty > 0 and self.inventory[item]:
                        batch = self.inventory[item][0]
                        take_qty = min(remaining_qty, batch.qty)
                        
                        # Add profit for this component
                        self.profit += take_qty * (sell_after_discount - batch.cost)
                        
                        # Record component
                        components.append(SaleComponent(take_qty, batch.cost, sell))
                        
                        # Update batch
                        batch.qty -= take_qty
                        if batch.qty == 0:
                            self.inventory[item].popleft()
                            
                        remaining_qty -= take_qty
                    
                    # Record sale lot
                    sale_lot = SaleLot(sell_after_discount, qty, components)
                    self.sales[item][sell].append(sale_lot)
                    
            elif command == "EXPIRE":
                if len(parts) != 3:
                    self.invalid = True
                    return
                item, qty_str = parts[1], parts[2]
                qty = int(float(qty_str))  # Handle "10.0" format
                
                if qty < 0:
                    self.invalid = True
                    return
                    
                if qty > 0:
                    if self._total_available(item) < qty:
                        self.invalid = True
                        return
                        
                    # Consume FIFO batches and subtract cost from profit
                    remaining_qty = qty
                    while remaining_qty > 0 and self.inventory[item]:
                        batch = self.inventory[item][0]
                        take_qty = min(remaining_qty, batch.qty)
                        
                        self.profit -= take_qty * batch.cost
                        
                        batch.qty -= take_qty
                        if batch.qty == 0:
                            self.inventory[item].popleft()
                            
                        remaining_qty -= take_qty
                        
            elif command == "RETURN":
                if len(parts) != 4:
                    self.invalid = True
                    return
                item, qty_str, sell_str = parts[1], parts[2], parts[3]
                qty = int(float(qty_str))  # Handle "10.0" format
                sell = float(sell_str)
                
                if qty < 0:
                    self.invalid = True
                    return
                    
                if qty > 0:
                    # Check if we have enough sold at this exact price
                    if item not in self.sales or sell not in self.sales[item]:
                        self.invalid = True
                        return
                        
                    total_sold_at_price = sum(lot.total_qty for lot in self.sales[item][sell])
                    total_returned_at_price = sum(lot.total_qty for lot in self.sales[item][sell] if lot.total_qty < 0)
                    available_to_return = total_sold_at_price + total_returned_at_price  # total_returned is negative
                    
                    if available_to_return < qty:
                        self.invalid = True
                        return
                        
                    # Process returns LIFO by lot, FIFO within lot
                    remaining_qty = qty
                    lots_to_process = self.sales[item][sell][::-1]  # Reverse for LIFO
                    
                    for lot in lots_to_process:
                        if remaining_qty <= 0:
                            break
                            
                        if lot.total_qty <= 0:  # Already fully returned
                            continue
                            
                        # Process components FIFO within this lot
                        lot_remaining = remaining_qty
                        while lot_remaining > 0 and lot.components:
                            component = lot.components[0]
                            if component.qty <= 0:
                                lot.components.popleft()
                                continue
                                
                            take_qty = min(lot_remaining, component.qty)
                            
                            # Reverse the profit
                            self.profit -= take_qty * (lot.sell_price_after_discount - component.cost)
                            
                            # Update component
                            component.qty -= take_qty
                            if component.qty == 0:
                                lot.components.popleft()
                                
                            lot_remaining -= take_qty
                            lot.total_qty -= take_qty
                            
                        remaining_qty -= (remaining_qty - lot_remaining)
                        
            elif command == "DISCOUNT":
                if len(parts) != 3:
                    self.invalid = True
                    return
                item, pct_str = parts[1], parts[2]
                pct = float(pct_str)
                self.discounts[item].append(pct)
                
            elif command == "DISCOUNT_END":
                if len(parts) != 2:
                    self.invalid = True
                    return
                item = parts[1]
                if self.discounts[item]:
                    self.discounts[item].pop()
                    
            elif command == "CHECK":
                if len(parts) != 1:
                    self.invalid = True
                    return
                    
                if self.invalid:
                    return
                    
                # Get all distinct item keys from inventory, discounts, and sales
                all_items = set()
                all_items.update(self.inventory.keys())
                all_items.update(self.discounts.keys())
                all_items.update(self.sales.keys())
                
                for item in sorted(all_items):
                    qty = self._total_available(item)
                    print(f"{item}: {qty}")
                    
            elif command == "PROFIT":
                if len(parts) != 1:
                    self.invalid = True
                    return
                    
                if self.invalid:
                    print("Profit/Loss: NA")
                else:
                    print(f"Profit/Loss: ${self.profit:.2f}")
                    
            else:
                # Unknown command
                self.invalid = True
                
        except (ValueError, IndexError, TypeError):
            self.invalid = True
    
    def run_file(self, path: str) -> None:
        """
        Reset state and process each line in the file.
        
        Resets all internal state before processing. Any file I/O errors
        will set the invalid flag, resulting in "Profit/Loss: NA" output.
        """
        # Reset state
        self.__init__()
        
        try:
            with open(path, 'r') as f:
                for line in f:
                    self.process_line(line)
        except (IOError, OSError):
            self.invalid = True
