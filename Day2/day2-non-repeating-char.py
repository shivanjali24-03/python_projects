#Problem 6: First Non-Repeating Character

s= input("Enter a String : ")
freq={}

for ch in s:
    if ch in freq:
        freq[ch] += 1
    else:
        freq[ch] = 1
print(freq)

found= False
for ch in s:
    if freq[ch] == 1:
        print(ch, end=" ")
        found = True
   
if not found:
    print("No non-repeating character found")