"""
Tasks:
Create a dictionary: item -> total_quantity
Calculate total bill amount,  Use match to apply discount:,Total ≥ 500 → 10% off,Total ≥ 300 → 5% off
Else → No discount,
Print: Item-wise quantities, Original total,Discounted total
"""
purchases = [
    ("apple", 2, 100),
    ("banana", 5, 20),
    ("apple", 1, 100),
    ("orange", 3, 50),
]

item_qty = {}
total_amount = 0

# Step 1 & 2: Build dict and total
for item, qty, price in purchases:
    if item in item_qty:
        item_qty[item] += qty
    else:
        item_qty[item] = qty

    total_amount += qty * price

# Step 3: Apply discount using match
bucket = total_amount // 100

match bucket:
    case 5 | 6 | 7 | 8 | 9 | 10:
        discount = 0.10
    case 3 | 4:
        discount = 0.05
    case _:
        discount = 0.0


final_amount = total_amount - (total_amount * discount)

print("Item quantities:", item_qty)
print("Original total:", total_amount)
print("Final amount after discount:", final_amount)
