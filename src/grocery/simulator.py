"""
Command processor for the Grocery Stock Management System.

Strictly implements CSC201 Task 1 rules with FIFO inventory, LIFO returns,
and per-item discount stacks.
"""

from collections import defaultdict, deque
from typing import Dict, List
from .models import Batch, SaleComponent, SaleLot, Inventory, DiscountStack, SalesHistory


class GrocerySimulator:
    """
    Processes grocery store commands following CSC201 Task 1 specification.
    
    Key Rules:
    - Inventory: FIFO per item using deque of Batch(qty, cost)
    - Discounts: per-item LIFO stack (last one active)
    - ORDER: Apply discount to sell price, consume FIFO, record by original sell price
    - RETURN: Match exact sell price, LIFO by sale lot, FIFO within lot
    - Error handling: Any invalid operation sets invalid=True
    """
    
    def __init__(self):
        self.inventory: Inventory = defaultdict(deque)
        self.discounts: DiscountStack = defaultdict(list)
        self.sales: SalesHistory = defaultdict(lambda: defaultdict(list))
        self.profit: float = 0.0
        self.invalid: bool = False
    
    def _active_discount(self, item: str) -> float:
        """Get active discount percentage for item (last one pushed)."""
        if self.discounts[item]:
            return self.discounts[item][-1]  # LIFO - last discount is active
        return 0.0
    
    def _total_available(self, item: str) -> int:
        """Get total available inventory quantity for item."""
        return sum(batch.qty for batch in self.inventory[item])
    
    def process_line(self, line: str) -> None:
        """
        Process a single command line following CSC201 Task 1 rules exactly.
        
        Strict Rules:
        - STOCK: qty>=0 AND cost>0, else invalid. Append batch if qty>0.
        - ORDER: qty>=0, sell>=0; insufficient stock => invalid. Apply active discount.
        - EXPIRE: qty>=0; insufficient stock => invalid. Consume FIFO batches.
        - RETURN: qty>=0; must not exceed total sold at EXACT sell price. LIFO by lot, FIFO within.
        - DISCOUNT: Push percentage onto per-item LIFO stack.
        - DISCOUNT_END: Pop from stack; popping empty is no-op.
        - CHECK: Only if not invalid, print all items alphabetically.
        - PROFIT: "Profit/Loss: NA" if invalid, else "Profit/Loss: $XX.XX".
        """
        line = line.strip()
        if not line or line.startswith('#'):
            return
            
        try:
            parts = line.split()
            if not parts:
                return
                
            command = parts[0]
            
            # Allow CHECK and PROFIT even when invalid, block others
            if self.invalid and command not in ("CHECK", "PROFIT"):
                return
            
            if command == "STOCK":
                if len(parts) != 4:
                    self.invalid = True
                    return
                item, qty_str, cost_str = parts[1], parts[2], parts[3]
                qty = int(float(qty_str))  # Tolerate "10.0" format
                cost = float(cost_str)
                
                # qty>=0 AND cost>0, else invalid
                if qty < 0 or cost <= 0:
                    self.invalid = True
                    return
                    
                # Append batch if qty>0
                if qty > 0:
                    self.inventory[item].append(Batch(qty, cost))
                    
            elif command == "ORDER":
                if len(parts) != 4:
                    self.invalid = True
                    return
                item, qty_str, sell_str = parts[1], parts[2], parts[3]
                qty = int(float(qty_str))  # Tolerate "10.0" format
                sell = float(sell_str)
                
                # qty>=0, sell>=0, else invalid
                if qty < 0 or sell < 0:
                    self.invalid = True
                    return
                    
                # Zero-qty ORDER is allowed and does nothing
                if qty == 0:
                    return
                    
                # Insufficient stock => invalid
                if self._total_available(item) < qty:
                    self.invalid = True
                    return
                    
                # Apply only the active discount to sell price
                discount_pct = self._active_discount(item)
                sell_after_discount = sell * (1 - discount_pct / 100)
                
                # Consume FIFO batches, record components
                components = deque()
                remaining_qty = qty
                
                while remaining_qty > 0 and self.inventory[item]:
                    batch = self.inventory[item][0]
                    take_qty = min(remaining_qty, batch.qty)
                    
                    # For each component: profit += take*(sell_after_discount - batch.cost)
                    self.profit += take_qty * (sell_after_discount - batch.cost)
                    
                    # Record component with unit_cost and unit_sell_after_discount
                    components.append(SaleComponent(take_qty, batch.cost, sell_after_discount))
                    
                    # Update batch
                    batch.qty -= take_qty
                    if batch.qty == 0:
                        self.inventory[item].popleft()
                        
                    remaining_qty -= take_qty
                
                # Record SaleLot under ORIGINAL sell price key (for returns matching)
                sale_lot = SaleLot(sell_after_discount, qty, components)
                self.sales[item][sell].append(sale_lot)
                    
            elif command == "EXPIRE":
                if len(parts) != 3:
                    self.invalid = True
                    return
                item, qty_str = parts[1], parts[2]
                qty = int(float(qty_str))  # Tolerate "10.0" format
                
                # qty>=0, else invalid
                if qty < 0:
                    self.invalid = True
                    return
                    
                # Zero-qty is no-op
                if qty == 0:
                    return
                    
                # Insufficient stock => invalid
                if self._total_available(item) < qty:
                    self.invalid = True
                    return
                    
                # Consume FIFO batches; profit -= take*batch.cost
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
                qty = int(float(qty_str))  # Tolerate "10.0" format
                sell = float(sell_str)
                
                # qty>=0, else invalid
                if qty < 0:
                    self.invalid = True
                    return
                    
                # Zero-qty is no-op
                if qty == 0:
                    return
                    
                # Must not exceed total units previously sold at EXACT sell price
                if item not in self.sales or sell not in self.sales[item]:
                    self.invalid = True
                    return
                    
                # Calculate available to return (positive total_qty means available)
                total_available_to_return = sum(
                    max(0, lot.total_qty) for lot in self.sales[item][sell]
                )
                
                if total_available_to_return < qty:
                    self.invalid = True
                    return
                    
                # Reverse sales LIFO by sale-lot, FIFO within lot's components
                remaining_qty = qty
                
                # Process lots in reverse order (LIFO by sale-lot)
                for lot in reversed(self.sales[item][sell]):
                    if remaining_qty <= 0:
                        break
                        
                    if lot.total_qty <= 0:  # Already fully returned
                        continue
                        
                    # Within this lot, process components FIFO
                    lot_qty_to_return = min(remaining_qty, lot.total_qty)
                    lot_remaining = lot_qty_to_return
                    
                    while lot_remaining > 0 and lot.components:
                        component = lot.components[0]
                        if component.qty <= 0:
                            lot.components.popleft()
                            continue
                            
                        take_qty = min(lot_remaining, component.qty)
                        
                        # For each returned unit: profit -= (unit_sell_after_discount - unit_cost)
                        self.profit -= take_qty * (component.unit_sell_after_discount - component.unit_cost)
                        
                        # Update component
                        component.qty -= take_qty
                        if component.qty == 0:
                            lot.components.popleft()
                            
                        lot_remaining -= take_qty
                        
                    # Update lot total_qty
                    lot.total_qty -= lot_qty_to_return
                    remaining_qty -= lot_qty_to_return
                        
            elif command == "DISCOUNT":
                if len(parts) != 3:
                    self.invalid = True
                    return
                item, pct_str = parts[1], parts[2]
                pct = float(pct_str)
                # Push onto per-item LIFO stack
                self.discounts[item].append(pct)
                
            elif command == "DISCOUNT_END":
                if len(parts) != 2:
                    self.invalid = True
                    return
                item = parts[1]
                # Pop from stack; popping empty is no-op
                if self.discounts[item]:
                    self.discounts[item].pop()
                    
            elif command == "CHECK":
                if len(parts) != 1:
                    self.invalid = True
                    return
                    
                # Only if run is NOT invalid, print items
                if self.invalid:
                    return
                    
                # Print all items (sorted by item name) from union of keys
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
                # Unknown command => invalid
                self.invalid = True
                
        except (ValueError, IndexError, TypeError):
            # Parsing errors => invalid
            self.invalid = True
    
    def run_file(self, path: str) -> None:
        """
        Reset state and process each line in the file.
        
        Any file I/O errors will set invalid flag.
        """
        # Reset state
        self.__init__()
        
        try:
            with open(path, 'r') as f:
                for line in f:
                    self.process_line(line)
        except (IOError, OSError):
            self.invalid = True
