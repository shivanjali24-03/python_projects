#Problem 7: Remove All Spaces from a String

s = input("Enter String : ")
result=""

for ch in s:
    if ch != " ":
        result += ch
print("String without Spaces", result)

