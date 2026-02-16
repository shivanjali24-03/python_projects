#2️⃣ Number Classification
a = int(input("Enter a number : "))

if a >= 0:
    if a % 2 == 0:
        print("The Number is even Number")
    else:
        print("Number is odd Number")
else:
    print("Number is Negative")
    if a % 2 == 0:
        print("Even")
    else:
        print("Odd")