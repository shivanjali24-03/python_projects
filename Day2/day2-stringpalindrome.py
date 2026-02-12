#string Palindrome

s=input("Enter a Plaindrome string : ")

rev=""

for ch in s:
    rev = ch + rev

if s==rev :
    print("String is Plaindrome String", s)
else:
    print("String Not a palindrome",s)
