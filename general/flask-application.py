'''This program imports the Flask class from the flask module and creates a new instance of it.
It then defines a route for the default home page by decorating the home() function with the @app.route decorator.

When the program is run, the development server is started and the app is served at http://localhost:5000/.
You can access the home page by visiting this URL in your web browser.

To build a more fully-featured Flask application, you can add additional routes and functions to handle different HTTP methods
 and URLs, and use templates to render HTML pages with dynamic content. You can also use Flask's built-in support
 for interacting with databases, handling forms, and other common web development tasks.
'''
# import the Flask class from the flask module
from flask import Flask

# create a new instance of the Flask class
app = Flask(__name__)

# define a route for the default home page
@app.route('/')
def home():
  return "Welcome to my Flask app!"

# start the development server using the run() method
if __name__ == '__main__':
  app.run()
