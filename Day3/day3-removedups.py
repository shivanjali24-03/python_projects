#Problem L1: Remove Duplicates (Keep Order) 

nums = [1, 2, 2, 3, 1, 4]

result = []

for x in nums:
    if x not in result:
        result.append(x)

print(result)
