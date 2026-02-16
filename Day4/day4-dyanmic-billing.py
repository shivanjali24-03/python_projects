prices = {
    "apple": 100,
    "banana": 20,
    "orange": 50,
    "kiwi": 80
}

item_qty = {}
total_amount = 0

n = int(input("How many different fruits do you want to buy? "))

for i in range(n):
    item = input("Enter fruit name: ").lower()
    qty = int(input("Enter quantity: "))

    if item not in prices:
        print("Sorry, this fruit is not available.")
        continue

    # Update quantity dictionary
    if item in item_qty:
        item_qty[item] += qty
    else:
        item_qty[item] = qty

    # Update total amount
    total_amount += qty * prices[item]

bucket = total_amount // 100
match bucket:
    case 5 | 6 | 7 | 8 | 9 | 10 :
        discount_rate = 0.10
    case 3| 4:
        discount_rate = 0.05
    case _:
        discount_rate = 0.0

discount_amount = total_amount * discount_rate
final_amount = total_amount - discount_amount
print("\nItem quantities:", item_qty)
print("Discount for you",discount_amount)
print("Total amount:", total_amount)
print("Final amount after discount", final_amount)
