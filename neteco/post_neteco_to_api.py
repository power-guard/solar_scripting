from post_config import API_TOKEN, BASE_URL
import requests

# Set up headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token {API_TOKEN}"
}

def post_plant_details(plants_id, plant_name):
    """
    Post plant details to the API.
    
    Parameters:
    plants_id (str): The ID of the plant.
    plant_name (str): The name of the plant.
    """
    post_url = f"{BASE_URL}/core/powerplants/"
    data = {
        "plant_id": plants_id,
        "plant_name": plant_name
    }
    try:
        response = requests.post(post_url, headers=HEADERS, json=data)
        response.raise_for_status()
        
        try:
            response_json = response.json()
            print('Response:', response_json)
        except ValueError:
            print('Error: Response content is not valid JSON')
    except requests.exceptions.RequestException as e:
        print(f"Failed to post plant details: {e}")
        print('Error Response:', response.text)

def post_devicelist_details(plant_id, logger_name, device_id, device_name):
    """
    Post device list details to the API.
    
    Parameters:
    plant_id (str): The ID of the plant.
    logger_name (str): The name of the logger.
    device_id (str): The ID of the device.
    device_name (str): The name of the device.
    """
    post_url = f"{BASE_URL}/core/devices/"
    data = {
        # "plant_id": plant_id,
        # "plant_name": plant_name,
        "logger_name": logger_name,
        "device_id": device_id,
        "device_name": device_name
    }
    try:
        response = requests.post(post_url, headers=HEADERS, json=data)
        response.raise_for_status()
        
        try:
            response_json = response.json()
            print('Response:', response_json)
        except ValueError:
            print('Error: Response content is not valid JSON')
    except requests.exceptions.RequestException as e:
        print(f"Failed to post device list details: {e}")
        print('Error Response:', response.text)

def post_daily_power_generation(device_id, power_gene):
    """
    Post daily power generation details to the API.
    
    Parameters:
    device_id (str): The ID of the device.
    power_gene (int): The power generation value.
    """
    print(f"Searching for device with ID: {device_id}")
    post_url = f"{BASE_URL}/core/device-power-gen/"
    get_url = f"{BASE_URL}/core/devices/"

    try:
        response = requests.get(get_url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        for device in data:
            json_device_id = device.get('device_id')
            if str(json_device_id) == str(device_id):
                print(device)

                if power_gene is None or power_gene == '':
                    power_gene = 0

                device['power_gene'] = power_gene
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
                    response.raise_for_status()
                    
                    try:
                        response_json = response.json()
                        print('Response:', response_json)
                    except ValueError:
                        print('Error: Response content is not valid JSON')
                except requests.exceptions.RequestException as e:
                    print(f"Failed to post power generation data: {e}")
                    print('Error Response:', response.text)

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch device data: {e}")
