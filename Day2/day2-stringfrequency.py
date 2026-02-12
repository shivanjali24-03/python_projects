#Problem 5: Character Frequency in a String

s= input("Enter a String ")

freq={}

for ch in s:
    if ch in freq:
        freq[ch] +=1
    else:
        freq[ch] = 1

print(freq)