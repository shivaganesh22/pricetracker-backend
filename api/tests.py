from django.test import TestCase
import requests
# Create your tests here.
req=requests.get("http://127.0.0.1:8000/api/test/?link=amazonz")
import json

# JSON string representation containing HTML content
json_string = req.json()
# Parse the JSON string
data_dict = json.loads(json_string)

# Extract the HTML content
html_content = data_dict['html_content']

# Now you can use the HTML content as needed
print(html_content)
