#Largest of Three Numbers
print("Enter 3 numbers: ")
a = input("First Number : ")
b = input("Second Number : ")
c = input("Third Number : ")

if a >= b and a >= c :
    print("Largest",a)
elif b >=a and b>=c:
    print("Largest",b)
else:
    ("Largest", c)