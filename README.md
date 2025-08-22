# CSC201 Task 1 – Grocery Stock Management System

A Python implementation that processes grocery store commands from text files and calculates profit/loss using FIFO inventory management, LIFO return policies, and per-item discount stacks.

## Overview

Simulates grocery store operations: stocking goods, processing orders, handling returns, applying discounts, expiring items, and calculating final profit/loss. Follows strict CSC201 Task 1 specification with exact output formatting requirements.

## How to Run

### Single File

```bash
python main.py commands.txt
```

### Multiple Files

```bash
python main.py file1.txt file2.txt file3.txt
```

Each file produces independent output with `--- filename ---` headers.

## Exact Output Contract

### CHECK Command

- Prints `<Item>: <quantity>` for all items (alphabetically sorted)
- Only shows current inventory quantities
- Suppressed if invalid state occurred

### PROFIT Command

- Valid: `Profit/Loss: $XX.XX` (exactly 2 decimal places)
- Invalid: `Profit/Loss: NA`

### Example

```
--- inputs/input_01.txt ---
Apple: 5
Peer: 20
Profit/Loss: $74.00

```

## Command Rules

- `STOCK item qty cost` - Add inventory (qty≥0, cost>0)
- `ORDER item qty sell` - Sell items (qty≥0, sell≥0, FIFO consumption)
- `EXPIRE item qty` - Remove inventory (qty≥0, FIFO removal)
- `RETURN item qty sell` - Return items (qty≥0, exact sell price match, LIFO by sale lot)
- `DISCOUNT item pct` - Push discount onto per-item stack
- `DISCOUNT_END item` - Pop discount from stack (no-op if empty)
- `CHECK` - Display inventory for all tracked items
- `PROFIT` - Display final profit/loss

### Key Algorithms

- **Inventory**: FIFO per item using deque of batches
- **Returns**: LIFO by sale lot, FIFO within lot components
- **Discounts**: Per-item LIFO stack (last discount is active)

## Invalid Triggers

Any of these conditions sets invalid state (→ `Profit/Loss: NA`):

- Insufficient inventory for ORDER/EXPIRE
- RETURN exceeding sold quantity at exact sell price
- STOCK with qty<0 or cost≤0
- ORDER with qty<0 or sell<0
- EXPIRE/RETURN with qty<0
- Command syntax errors
- Unknown commands

## Notes

- **Python**: 3.10+ required (modern type hints, dataclasses)
- **Dependencies**: Standard library only
- **Precision**: All monetary values formatted to exactly 2 decimal places
- **Input**: Tolerates "10.0" format for quantities via `int(float(x))`
- **Zero Operations**: qty=0 commands are valid no-ops
