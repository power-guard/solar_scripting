import os
import time
import requests
import json
from .post_neteco_to_api import (post_plant_details, 
                                 post_devicelist_details,
                                 post_daily_power_generation)

# Session
session = requests.Session()
session.verify = False  # Disabling SSL certificate verification

def read_credentials_from_json(file_path):
    with open(file_path, 'r') as f:
        credentials_data = json.load(f)
    return credentials_data['credentials']


def login(base_url, user, password):
    url = f'{base_url}/login'
    params = {'userName': user, 'password': password}
    response = session.post(url, params=params, verify=False)
    response.raise_for_status()
    return response.json()


def get_plant_list(BASE_URL, token):
    url = f'{BASE_URL}/queryPlantList'
    params = {'openApiroarand': token}
    response = session.post(url, params=params, verify=False)
    response.raise_for_status()
    return response.json()


def handle_plant_list(plant_list_response, BASE_URL, token):
    """
    Getting plant id, plant name 
    """
    result_data = plant_list_response['resultData']
    plant_ids = []  # Initialize an empty list to collect plant IDs
    if result_data:
        for plant in result_data:
            plants_id = plant['plantid']
            plant_name = plant['plantName']

            # Send the data to API only plantid and plant name 
            post_plant_details(plants_id, plant_name)

            # Collect plant ID
            plant_ids.append(plants_id)

    else:
        print('Received empty plant list.')
    # Pass the collected plant IDs to handle_device_list
    handle_device_list(BASE_URL, plant_ids, token)
    get_realtime_data(BASE_URL, plant_ids, token)


def handle_device_list(BASE_URL, plant_ids, token):

    # Calculate the quarter size
    quarter_size = len(plant_ids) // 4
    first_quarter = plant_ids[:quarter_size]
    second_quarter = plant_ids[quarter_size:2*quarter_size]
    third_quarter = plant_ids[2*quarter_size:3*quarter_size]
    fourth_quarter = plant_ids[3*quarter_size:]

    quarters = [first_quarter, second_quarter, third_quarter, fourth_quarter]
    # Iterate over each quarter
    for quarter in quarters:
        # Iterate over each plant ID in the current quarter
        for plant_id in quarter:
            print(plant_id)
            url = f'{BASE_URL}/queryDeviceList'
            params = {
                'openApiroarand': token,
                'plantid': plant_id
            }
            device_list = session.post(url, params=params, verify=False)
            device_list.raise_for_status()
            try:
                response_text = device_list.text
                response_json = json.loads(response_text)
                print(response_json)
            except json.JSONDecodeError:
                print("Error: Unable to decode JSON response.")
                print("Response Text:", response_text)

            for data in response_json['resultData']:
                plant_id = data['plantid']
                logger_name = data['SmartLogger']
                device_id = data['deviceid']
                device_name = data['deviceName']

                #Send the data to API only plant_id, logger_name, device_id, device_name
                post_devicelist_details(plant_id, logger_name, device_id, device_name)

        # Wait for 10 seconds before making requests for the next quarter
        time.sleep(10)


def get_realtime_data(BASE_URL, plant_ids, token):
    # Calculate the quarter size
    quarter_size = len(plant_ids) // 4
    first_quarter = plant_ids[:quarter_size]
    second_quarter = plant_ids[quarter_size:2*quarter_size]
    third_quarter = plant_ids[2*quarter_size:3*quarter_size]
    fourth_quarter = plant_ids[3*quarter_size:]

    quarters = [first_quarter, second_quarter, third_quarter, fourth_quarter]
    # Iterate over each quarter
    for quarter in quarters:
        # Iterate over each plant ID in the current quarter
        for plant_id in quarter:
            print(f"Plant ID number= {plant_id}")
            url = f'{BASE_URL}/queryDeviceDetail'
            params = {
                'openApiroarand': token,
                'plantid': plant_id
            }
            real_time_data = session.post(url, params=params, verify=False)
            real_time_data.raise_for_status()
            response_json = real_time_data.json()

            if 'resultSunData' in response_json['resultData']:
                for data in response_json['resultData']['resultSunData']:
                    device_id = data['deviceid']
                    power_gene = data['dailyPowerGeneration']
                    post_daily_power_generation(device_id, power_gene)
                    #print(data)
            else:
                print('Received empty device data.')
        # Wait for 10 seconds before making requests for the next quarter
        time.sleep(10)



def logout(BASE_URL, token):
    url = f'{BASE_URL}/logout'
    params = {'openApiroarand': token}
    response = session.post(url, params=params, verify=False)
    response.raise_for_status()
    return response.json()





def main():
    # Get the path to the JSON file relative to the current script location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'credentials.json')

    credentials = read_credentials_from_json(json_file_path)
    for cred in credentials:
        print(f'Starting to access API for {cred["host"]}...')
        try:
            # Construct BASE_URL using host and port from credentials
            BASE_URL = cred['base_url']
            
            login_response = login(BASE_URL, cred['user'], cred['password'])
            token = login_response['openApiroarand']

            # Call other functions using credentials from 'cred'
            plant_list_response = get_plant_list(BASE_URL, token)
            handle_plant_list(plant_list_response, BASE_URL, token)

            logout_response = logout(BASE_URL, token)
            print('Logged out successfully.')
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
