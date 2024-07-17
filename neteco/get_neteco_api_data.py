import os
import time
import requests
import json
import logging
from requests.exceptions import RequestException, HTTPError
from collections import defaultdict
from .post_neteco_to_api import (
    post_plant_details, 
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
    


def handle_device_list(base_url, plant_ids, token):
    """
    Handle the device list for each plant:
    - Process plant IDs in quarters to avoid overloading the server.
    - Send device details to the API.
    """

    # Initialize an empty dictionary to store the smartloggers
    smartlogger_data = {}
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


                if plant_id not in smartlogger_data:
                    smartlogger_data[plant_id] = []

                for data in device_list.get('resultData', []):
                    logger_name = data.get('SmartLogger')
                    device_id = data.get('deviceid')
                    device_name = data.get('deviceName')

                    smartlogger_data[plant_id].append({
                        "logger_name": logger_name,
                        'device_id': device_id,
                        'device_name': device_name
                    })
                    
                 
                    

            except RequestException as e:
                logging.error(f"Device list request failed for plant ID {plant_id}: {e}")


        time.sleep(10)
    # print(smartlogger_data)
    get_realtime_data(base_url, smartlogger_data, token)


def get_realtime_data(base_url, smartlogger_data, token):
    """
    Get real-time data for each SmartLogger.
    """
    quarter_size = max(1, len(smartlogger_data) // 4)
    quarters = [list(smartlogger_data.items())[i:i + quarter_size] for i in range(0, len(smartlogger_data), quarter_size)]

    def parse_power_gen(value):
        """
        Helper function to convert power generation values to float.
        Treats None, empty string, space, and other non-numeric values as 0.
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    for quarter in quarters:
        for plant_id, devices in quarter:
            print(f"Processing real-time data for plant ID: {plant_id}")
            url = f'{base_url}/queryDeviceDetail'
            params = {'openApiroarand': token, 'plantid': plant_id}
            
            # Create a dictionary mapping device IDs to logger names
            device_id_to_logger_name = {device['device_id']: device['logger_name'] for device in devices}
                
            # Dictionary to store cumulative power generation for each logger name
            logger_name_to_power_gen = {}

            try:
                response = session.post(url, params=params, verify=False)
                response.raise_for_status()
                real_time_data = response.json()

                if 'resultSunData' in real_time_data.get('resultData', {}):
                    for data in real_time_data['resultData']['resultSunData']:
                        device_id = data.get('deviceid')
                        power_gene = parse_power_gen(data.get('dailyPowerGeneration'))
                    
                        if device_id is not None:
                            # Get the logger name from the dictionary
                            logger_name = device_id_to_logger_name.get(device_id, device_id)
                                
                            # Sum the power generation for each logger name
                            if logger_name in logger_name_to_power_gen:
                                logger_name_to_power_gen[logger_name] += power_gene
                            else:
                                logger_name_to_power_gen[logger_name] = power_gene

                        else:
                            logging.warning(f"Invalid real-time data: {data}")
                else:
                    logging.warning('Received empty device data.')

            except RequestException as e:
                logging.error(f"Real-time data request failed for plant ID {plant_id}: {e}")

            # Print the cumulative power generation for each logger name
            for logger_name, total_power in logger_name_to_power_gen.items():
                print(f"{logger_name} generated {total_power} kWh today.")
                total_power = round(total_power, 3)
                post_daily_power_generation(logger_name, total_power)

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
