import requests

# Fetch the content of the HTTPS link
url = "https://www.example.com"
response = requests.get(url)

# Write the content to a file
with open("output.txt", "w") as f:
    f.write(response.text)

# Display the first 20 lines of the file
with open("output.txt", "r") as f:
    for i, line in enumerate(f):
        if i == 20:
            break
        print(line)
