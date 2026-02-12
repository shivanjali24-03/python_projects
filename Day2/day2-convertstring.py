#Problem 4: Convert a Numeric String to int and float
s= input("Enter a value ")

try:
    i=int(s)
    print("Value as int : ",i)
except:
    print("Cannnot be converted to Integer : ",i)

try:
    f=float(s)
    print("Value as float : ",f)
except:
    print("Cannnot be converted to float : ",f)