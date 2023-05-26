import random

# Function to generate a fake dataset
def generate_dataset(rows):
    dataset = []
    for i in range(rows):
        customer_id = i+1
        products = ['A','B','C','D','E','F','G','H','I','J']
        product = random.choice(products)
        revenue = round(random.uniform(10, 500), 2)
        dataset.append([customer_id, product, revenue])
    return dataset

# Generate dataset with 1000 rows
rows = 1000
data = generate_dataset(rows)

# Print first 10 rows of the dataset
for i in range(10):
    print(data[i])
