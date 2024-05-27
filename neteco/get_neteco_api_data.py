import os
import requests
import json
from .post_neteco_to_api import post_plant_details, post_devicelist_details

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
    Geting plant id, plant name 
    """
    result_data = plant_list_response['resultData']
    if result_data:
        for plant in result_data:
            plants_id = plant['plantid']
            plant_name = plant['plantName']

            #Send the data to API only plantid and plant name 
            #post_plant_details(plants_id, plant_name)

            # Pass BASE_URL and token to handle_device_list and get_realtime_data function
            handle_device_list(BASE_URL, plants_id, token)
            #get_realtime_data(BASE_URL, plant_details['plantid'], token)
    else:
        print('Received empty plant list.')

def handle_device_list(BASE_URL, plants_id, token):
    print(plants_id)
    url = f'{BASE_URL}/queryDeviceList'
    params = {
            'openApiroarand': token,
            'plantid': plants_id
            }
    real_time_data = session.post(url, params=params, verify=False)
    real_time_data.raise_for_status()
    response_json = real_time_data.json()
    print(response_json)

    # if 'resultSunData' in response_json['resultData']:
    for data in response_json['resultData']:
        plant_id = data['plantid']
        logger_name = data['SmartLogger']
        device_id = data['deviceid']
        device_name = data['deviceName']
        
        #Send the data to API only plant_id, logger_name, device_id, device_name
        post_devicelist_details(plant_id, logger_name, device_id, device_name)
    


# def get_realtime_data(BASE_URL, plantid, token):
#     url = f'{BASE_URL}/queryDeviceDetail'
#     params = {
#             'openApiroarand': token,
#             'plantid': plantid
#             }
#     real_time_data = session.post(url, params=params, verify=False)
#     real_time_data.raise_for_status()
#     response_json = real_time_data.json()

#     if 'resultSunData' in response_json['resultData']:
#         for data in response_json['resultData']['resultSunData']:
#             prod_details = {'deviceid': data['deviceid'], 'deviceName': data['deviceName'], 'dailyPowerGeneration': data['dailyPowerGeneration']}
#             print(prod_details)
#     else:
#         print('Received empty plant list.')









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
