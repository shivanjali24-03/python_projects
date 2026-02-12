#Vowel String

s= input("Enter your letter to cehck Vowel ")

vowel = 0
consonents = 0

for ch in s:
    print("Current Character",ch)
    if ch.isalpha():
        if ch in "aeiouAEIOU":
            vowel +=1
        else:
            consonents += 1

print("Vowels : ",vowel)
print("Consonents : ",consonents)