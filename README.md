# CSC201 Task 1 – Grocery Stock Management System

A Python profit checker that processes grocery store commands and calculates profits using FIFO inventory and LIFO return policies.

## Usage

```bash
python main.py input_file.txt
```

## Commands

- `STOCK item qty cost` - Add inventory
- `ORDER item qty price` - Sell items
- `EXPIRE item qty` - Remove expired items
- `RETURN item qty price` - Process returns
- `DISCOUNT item percent` - Apply discount
- `DISCOUNT_END item` - Remove discount
- `CHECK` - Show inventory
- `PROFIT` - Show profit/loss

## Output

```
Item: quantity
...
Profit/Loss: $XX.XX
```

Error cases show `Profit/Loss: NA`.

## Test Results

All official test cases pass with exact expected outputs:

- input_01.txt: `Apple: 5, Peer: 20, Profit/Loss: $74.00` ✅
- input_02.txt: `Apple: 15, Orange: 15, Profit/Loss: $-21.50` ✅
- input_03.txt: `Apple: 6, Profit/Loss: $6.50` ✅
- input_04.txt: `Apple: 8, Banana: 25, Profit/Loss: $-10.30` ✅
- input_05.txt: `Profit/Loss: NA` ✅

## Requirements

Python 3.10+, standard library only.
