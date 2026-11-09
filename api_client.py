import requests

name = input("Enter your first name: ")

url = "https://labrador-clark-vincent.onrender.com/skills"

params = {"name": name}

try:
    response = requests.get(url, params=params, timeout=30)

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print(data.get("message", data))
    else:
        print("Request failed:", response.text)

except requests.exceptions.RequestException as error:
    print("Connection error:", error)
