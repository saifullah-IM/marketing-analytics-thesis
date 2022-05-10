import requests

BASE = "http://127.0.0.1:5000/"
search_str = "sunsilk black shine shampoo"

response = requests.get(BASE + f"/search/chaldal/{search_str}")
print(response.json())

response = requests.get(BASE + f"/search/daraz/{search_str}")
print(response.json())
