import requests
import json

response_API = requests.get('https://dummyjson.com/products')
data = response_API.text

data1 = json.loads(data)

for i in data1["products"]:
    if i['price'] >= 500 and i['rating'] > 4:
        print(
            f'Title: {i["title"]} Description:{i["description"]} {i["title"]}    Price : {i["price"]}  Rating: {i["rating"]}')
