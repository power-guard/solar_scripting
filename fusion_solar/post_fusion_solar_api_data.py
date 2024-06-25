from post_config import API_TOKEN, BASE_URL
import requests

# Set up headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Token {API_TOKEN}"
}

def post_plant_details(plant_name):
    """
    Post plant details to the API.
    
    Parameters:
    plants_id (str): The ID of the plant.
    plant_name (str): The name of the plant.
    """
    post_url = f"{BASE_URL}/core/powerplants/"
    data = {
        "plant_id": plant_name,
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


def post_daily_power_generation(plant_name, power_gene):
    """
    Post daily power generation details to the API.
    
    Parameters:
    plant_name (str): The ID of the device.
    power_gene (int): The power generation value.
    """
    print(f"Searching for device with ID: {plant_name}")
    #this is use to create a loger powergen
    logger_power_gen_url = f"{BASE_URL}/core/logger-power-gen/"

    

    logger_power_gen_data = {
        'logger_name': plant_name,
        'power_gen': power_gene
    }

    try:
        
        response = requests.post(logger_power_gen_url, headers=HEADERS, json=logger_power_gen_data)
        response.raise_for_status()
        
        try:
            response_json = response.json()
            print('Logger Power Generation Response:', response_json)
        except ValueError:
            print('Error: One or both response contents are not valid JSON')

    except requests.exceptions.RequestException as e:
        print(f"Failed to post device list details: {e}")