nums = [10, 5, 20, 8, 15]

largest = nums[0]
second_largest = float("-inf")

for x in nums:
    print("Number",x)
    if x > largest:
        print(largest)
        second_largest = largest
        largest = x
        print("Second Largest",second_largest)
        print("Largest",largest)

    elif x != largest and x > second_largest:
        print("L and SL",largest, second_largest)
        second_largest = x
        print("else -Second Largest",second_largest)

print("Largest:", largest)
print("Second largest:", second_largest)
