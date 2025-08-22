"""
Core data models for the Grocery Stock Management System.

This module contains the data structures for managing inventory, sales, returns,
and discount tracking with proper FIFO/LIFO semantics.
"""

from typing import Dict, List, Deque
from collections import deque
from dataclasses import dataclass


@dataclass
class Batch:
    """Represents a batch of products with purchase cost."""
    qty: int
    cost: float


@dataclass
class SaleComponent:
    """Represents a component of a sale with unit cost and discounted sell price."""
    qty: int
    unit_cost: float
    unit_sell_after_discount: float


@dataclass
class SaleLot:
    """Represents a lot of sales at a specific price after discount."""
    sell_price_after_discount: float
    total_qty: int
    components: Deque[SaleComponent]


# Type aliases
Inventory = Dict[str, Deque[Batch]]
DiscountStack = Dict[str, List[float]]
SalesHistory = Dict[str, Dict[float, List[SaleLot]]]
