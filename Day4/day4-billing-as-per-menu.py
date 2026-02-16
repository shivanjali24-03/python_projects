fruits_menu ={
    1:("apples",100),
    2:("kiwi",50),
    3:("oranges",20),
    4:("banana",10)
}
cart = {}
total_amount = 0
for key, (name, price) in fruits_menu.items():
    print(f"{key}. {name} - Rs. {price}")

n = int(input("How many Fruits you want  add to cart ? - "))
for i in range(n):
    choice = int(input("Enter fruit number: "))
    if choice not in fruits_menu:
        print("Not In Menu")    
    else:
        qty = int(input("Enter quantity: "))
        name, price  = fruits_menu[choice]
        if name in cart:
            cart[name] += qty
        else:
            cart[name] = qty
        total_amount += qty * price    


price_lookup ={}
for _, (name, price) in fruits_menu.items():
    price_lookup[name] = price

print("Items in Cart :  \n")

for item_name in sorted(cart):
    qty = cart[item_name]
    price = price_lookup[item_name]
    item_total = qty * price
    print(f"{item_name} - {qty} x {price} = {item_total}")

print("Total Amount : ",total_amount)

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

print("Discount for you",discount_amount)
print("Total amount:", total_amount)
print("Final amount after discount", final_amount)