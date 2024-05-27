from .post_config import API_TOKEN
import requests

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token {API_TOKEN}"
}




def post_plant_details(plants_id, plany_name):
    
    post_url = "http://127.0.0.1:8000/api/core/powerplants/"
    data ={
        "plant_id": plants_id,
        "plant_name": plany_name
    }
    response = requests.post(post_url, headers=HEADERS, json=data)
    # Check response status code
    if response.status_code == 201:
        # Request was successful
        try:
            # Attempt to parse response JSON
            response_json = response.json()
            print('Response:', response_json)
        except ValueError:
            # Failed to parse response JSON
            print('Error: Response content is not valid JSON')

    else:
        # Request failed, print error message
        print('Failed to post data. Status Code:', response.status_code)
        print('Error Response:', response.text)


def post_devicelist_details(plant_id, logger_name, device_id, device_name):
    plant_name = "unknown"
    post_url = "http://127.0.0.1:8000/api/core/devices/"
    data = {
        "plant_id": plant_id,
        "plant_name": plant_name,
        "logger_name": logger_name,
        "device_id": device_id,
        "device_name": device_name
    }

    try:
        response = requests.post(post_url, headers=HEADERS, json=data)
    except requests.exceptions.RequestException as e:
        print(f"Failed to post data: {e}")
        return

    # Check response status code
    if response.status_code == 201:
        # Request was successful
        try:
            # Attempt to parse response JSON
            response_json = response.json()
            print('Response:', response_json)
        except ValueError:
            # Failed to parse response JSON
            print('Error: Response content is not valid JSON')
    else:
        # Request failed, print error message
        print('Failed to post data. Status Code:', response.status_code)
        print('Error Response:', response.text)