import requests

url = "https://neca-mae-herbaliga.onrender.com/student"

try:
    response = requests.get(url, timeout=30)

    print("Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)
    else:
        print("Request failed:", response.text)

except requests.exceptions.RequestException as error:
    print("Connection error:", error)
