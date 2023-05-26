
def binary_search(list1,number):
    low = 0
    mid = 0
    high = len(list1) - 1
    while low < high:
        mid = (high + low) // 2
        if number < list1[mid]:
            high = mid
        elif number > list1[mid]:
            low = mid
        else:
            return mid
    return -1
list1 = [1,3,6,9,11]
number = 19
result=binary_search(list1,number)
if result != -1:
    print("Element is present at index", str(result))
else:
    print("Element is not present in array")
