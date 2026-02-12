#Reverse a string (no slicing)
s = input("Enter a string ")

print(s)
rev=""

for ch in s:
    rev= ch + rev
    print(rev)

print("Reversed String: ",rev)