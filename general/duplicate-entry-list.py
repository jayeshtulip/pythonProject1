# define the list
lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 3, 4, 5]

# create an empty dictionary to store the index values of the duplicates
duplicates = {}

# iterate over the list
for i, item in enumerate(lst):
  # check if the item is already in the dictionary
  if item in duplicates:
    # add the index value to the list of index values for this item
    duplicates[item].append(i)
  else:
    # add the item and its index value to the dictionary
    duplicates[item] = [i]

# print the items and their index values
for item, indices in duplicates.items():
  if len(indices) > 1:
    print(f"{item} has duplicate indices: {indices}")
