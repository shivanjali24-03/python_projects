#index looping 
"""
range(start, stop, step) =>range(len(s) - 1, -1, -1)=>range(4, -1, -1) =>4, 3, 2, 1, 0
Which means:
Start at index 4 (last character: 'o')
Stop before -1 (so last included is 0)
Step = -1 → go backwards
"""

s = input("Enter a String : ")

rev=""

for i in range(len(s)-1,-1,-1):
    print(s[i])
    rev = rev + s[i]
    print(rev)
    print(s[i])

