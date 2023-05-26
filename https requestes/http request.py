import requests
import sqlite3

# URL of the website to access
url = "https://www.example.com"

# Send a request to the website and get the response
response = requests.get(url)

# Check the response status code to make sure the request was successful
if response.status_code == 200:
  # Get the website's content
  content = response.text

  # Connect to the SQL database
  conn = sqlite3.connect("website_content.db")
  c = conn.cursor()

  # Create a table to store the website's content
  c.execute("CREATE TABLE website_content (content TEXT)")

  # Insert the content into the table
  c.execute("INSERT INTO website_content VALUES (?)", (content,))

  # Save the changes and close the connection
  conn.commit()
  conn.close()

else:
  print("Failed to access the website")
