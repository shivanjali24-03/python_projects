nums = [1, 0, 3, 0, 5, 2]
"""
result = []
zero_count = 0

for x in nums:
    if x != 0:
        result.append(x)
    else:
        zero_count += 1

for _ in range(zero_count):
    result.append(0)

print(result)
"""

nonzero = []
zero = []

for x in nums:
    if x == 0:
        zero.append(x)
    else:
        nonzero.append(x)

result = nonzero + zero

print(result)
