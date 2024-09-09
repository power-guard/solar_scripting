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
    power_gene (float/int): The power generation value.
    """
    print(f"Searching for device with ID: {plant_name}")
    # Logger power generation URL
    logger_power_gen_url = f"{BASE_URL}/core/logger-power-gen/"
    
    # Ensure that power_gen has no more than 10 digits in total
    if len(str(int(power_gene))) > 7:  # 7 digits before the decimal point
        print(f"Error: The power_gen value exceeds the allowed limit of 10 digits: {power_gene}")
        return
    
    # Round power_gene to 3 decimal places
    logger_power_gen_data = {
        'logger_name': plant_name,
        'power_gen': round(power_gene, 3)  # Round off to 3 decimal places
    }

    print(f"Sending power generation data: {logger_power_gen_data}")

    try:
        response = requests.post(logger_power_gen_url, headers=HEADERS, json=logger_power_gen_data)
        response.raise_for_status()
        
        try:
            response_json = response.json()
            print('Logger Power Generation Response:', response_json)
        except ValueError:
            print('Error: Response content is not valid JSON')

    except requests.exceptions.RequestException as e:
        print(f"Failed to post power generation details: {e}")
        print('Error Response:', response.text)
