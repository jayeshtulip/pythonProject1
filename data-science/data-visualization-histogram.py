import matplotlib.pyplot as plt

# example data
data = [2, 4, 6, 8, 10, 4, 3, 7, 8, 9, 5, 7, 6, 4, 5, 3, 2, 4, 5, 6, 7, 8, 9, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10, 4, 5, 6, 7, 8, 9, 10]

# create the histogram
plt.hist(data, bins=12, color='blue', edgecolor='red')

# add labels to the axes
plt.xlabel('Data values')
plt.ylabel('Frequency')

# display the plot
plt.show()
