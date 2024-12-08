import requests

# Define the Rasa Action Server host and endpoint
rasa_host = "http://localhost:5055/webhook"

# Define the message/query you want to send to the server
query_text = "tôi muốn đi du lịch cần thơ"

# Send a POST request to the Rasa Action Server
response = requests.post(rasa_host, json={"sender": "test", "message": query_text})

# Check the response from the server
if response.status_code == 200:
    print("Response from Rasa Action Server:", response.json())
else:
    print(f"Failed to get a response. Status code: {response.status_code}")