import os
import time
import requests
import json
import logging
from requests.exceptions import RequestException, HTTPError
from .post_neteco_to_api import (
    post_plant_details, 
    post_devicelist_details,
    post_daily_power_generation
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Session
session = requests.Session()
session.verify = False  # Disabling SSL certificate verification

def read_credentials_from_json(file_path):
    """Read credentials from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            credentials_data = json.load(f)
        return credentials_data['credentials']
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error reading credentials: {e}")
        raise

def login(base_url, user, password):
    """Login to the API and return the token."""
    url = f'{base_url}/login'
    params = {'userName': user, 'password': password}
    try:
        response = session.post(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logging.error(f"Login request failed: {e}")
        raise
    except HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise

def get_plant_list(base_url, token):
    """Retrieve the list of plants from the API."""
    url = f'{base_url}/queryPlantList'
    params = {'openApiroarand': token}
    try:
        response = session.post(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logging.error(f"Get plant list request failed: {e}")
        raise
    except HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise

def handle_plant_list(plant_list_response, base_url, token):
    """
    Process the plant list response:
    - Extract plant IDs and names.
    - Send plant details to the API.
    - Handle device list and real-time data for each plant.
    """
    result_data = plant_list_response.get('resultData', [])
    plant_ids = []

    if result_data:
        for plant in result_data:
            plants_id = plant.get('plantid')
            plant_name = plant.get('plantName')

            if plants_id and plant_name:
                post_plant_details(plants_id, plant_name)
                plant_ids.append(plants_id)
            else:
                logging.warning(f"Invalid plant data: {plant}")

    else:
        logging.warning('Received empty plant list.')

    handle_device_list(base_url, plant_ids, token)
    get_realtime_data(base_url, plant_ids, token)


def handle_device_list(base_url, plant_ids, token):
    """
    Handle the device list for each plant:
    - Process plant IDs in quarters to avoid overloading the server.
    - Send device details to the API.
    """
    quarter_size = max(1, len(plant_ids) // 4)
    quarters = [plant_ids[i:i + quarter_size] for i in range(0, len(plant_ids), quarter_size)]

    for quarter in quarters:
        for plant_id in quarter:
            logging.info(f"Processing devices for plant ID: {plant_id}")
            url = f'{base_url}/queryDeviceList'
            params = {'openApiroarand': token, 'plantid': plant_id}

            try:
                response = session.post(url, params=params, verify=False)
                response.raise_for_status()
                device_list = response.json()

                for data in device_list.get('resultData', []):
                    plant_id = data.get('plantid')
                    logger_name = data.get('SmartLogger')
                    device_id = data.get('deviceid')
                    device_name = data.get('deviceName')

                    if plant_id and logger_name and device_id and device_name:
                        post_devicelist_details(plant_id, logger_name, device_id, device_name)
                    else:
                        logging.warning(f"Invalid device data: {data}")

            except RequestException as e:
                logging.error(f"Device list request failed for plant ID {plant_id}: {e}")
            except HTTPError as e:
                logging.error(f"HTTP error occurred for plant ID {plant_id}: {e}")

        time.sleep(10)

def get_realtime_data(base_url, plant_ids, token):
    """
    Retrieve real-time data for each plant:
    - Process plant IDs in quarters to avoid overloading the server.
    - Send daily power generation data to the API.
    """
    
    quarter_size = max(1, len(plant_ids) // 4)
    quarters = [plant_ids[i:i + quarter_size] for i in range(0, len(plant_ids), quarter_size)]

    for quarter in quarters:
        for plant_id in quarter:
            logging.info(f"Fetching real-time data for plant ID: {plant_id}")
            url = f'{base_url}/queryDeviceDetail'
            params = {'openApiroarand': token, 'plantid': plant_id}

            try:
                response = session.post(url, params=params, verify=False)
                response.raise_for_status()
                real_time_data = response.json()

                if 'resultSunData' in real_time_data.get('resultData', {}):
                    for data in real_time_data['resultData']['resultSunData']:
                        device_id = data.get('deviceid')
                        power_gene = data.get('dailyPowerGeneration')

                        if device_id and power_gene is not None:
                            post_daily_power_generation(device_id, power_gene)
                        else:
                            logging.warning(f"Invalid real-time data: {data}")

                else:
                    logging.warning('Received empty device data.')

            except RequestException as e:
                logging.error(f"Real-time data request failed for plant ID {plant_id}: {e}")
            except HTTPError as e:
                logging.error(f"HTTP error occurred for plant ID {plant_id}: {e}")

        time.sleep(10)

def logout(base_url, token):
    """Logout from the API."""
    url = f'{base_url}/logout'
    params = {'openApiroarand': token}
    try:
        response = session.post(url, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logging.error(f"Logout request failed: {e}")
        raise
    except HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
        raise

def main():
    """Main function to execute the API workflow."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'credentials.json')

    try:
        credentials = read_credentials_from_json(json_file_path)
    except Exception as e:
        logging.critical(f"Failed to load credentials: {e}")
        return

    for cred in credentials:
        logging.info(f"Starting to access API for {cred['host']}...")
        try:
            BASE_URL = cred['base_url']
            login_response = login(BASE_URL, cred['user'], cred['password'])
            token = login_response.get('openApiroarand')

            if token:
                plant_list_response = get_plant_list(BASE_URL, token)
                handle_plant_list(plant_list_response, BASE_URL, token)
                logout_response = logout(BASE_URL, token)
                logging.info('Logged out successfully.')
            else:
                logging.error('Login failed, token not received.')

        except Exception as e:
            logging.error(f"Error processing {cred['host']}: {e}")

if __name__ == "__main__":
    main()
