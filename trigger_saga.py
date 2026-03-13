import requests
import json

url = "http://localhost:5123/saga/order"
payload = {
    "user_id": 1,
    "items": [
        {
            "product_id": 1,
            "quantity": 1
        }
    ]
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
