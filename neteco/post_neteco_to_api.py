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


def post_daily_power_generation(device_id, power_gene):
    print(f"Searching for device with ID: {device_id}")
    post_url = "http://127.0.0.1:8000/api/core/device-power-gen/"
    get_url = "http://127.0.0.1:8000/api/core/devices/"
    try:
        response = requests.get(get_url, headers=HEADERS)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        data = response.json()  # Parse response JSON data

      
        for device in data:
            json_device_id = device.get('device_id')
            if str(json_device_id) == str(device_id):
                print(device)
                
                if power_gene is None or power_gene == '':
                    power_gene = 0  # Assign 0 if power_gene is None or empty
                
                device['power_gene'] = power_gene  # Append the power_gene
                print(device)
                devices = device['id']
                logger = device['logger_name']
                power_gen = device['power_gene']
                data = {
                    "device_id": devices,
                    "logger_name": logger,
                    "power_gen": power_gen
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
                    

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data: {e}")


    
