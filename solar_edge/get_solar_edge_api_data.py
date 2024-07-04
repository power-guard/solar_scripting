import requests
import yaml
from datetime import datetime
from .post_solar_edge_api_data import (
    post_plant_details,
    post_daily_power_generation
)

def main():
    try:
        # Load the configuration from the external YAML file
        with open('solar_edge/plant_id_token.yml', 'r') as file:
            data = yaml.safe_load(file)

        # Extract plants data from YAML
        plants = data['plants']

        base_url = "https://monitoringapi.solaredge.com"

        # Function to fetch plant energy production for a specific date
        def fetch_energy_data(plant_id, api_key, date):
            url = f"{base_url}/site/{plant_id}/energy.json"
            params = {
                'api_key': api_key,
                'startDate': date,
                'endDate': date,
                'timeUnit': 'DAY'
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch data for plant {plant_id}: {response.status_code} - {response.text}")
                return None

        # Get today's date in the required format
        today = datetime.now().strftime('%Y-%m-%d')

        # Iterate through each plant in the YAML data
        for plant_name, plant_data in plants.items():
            api_key = plant_data['api_key']
            plant_id = plant_data['plants_id']

            # Fetch energy data for the plant
            energy_data = fetch_energy_data(plant_id, api_key, today)

            # Process the fetched data (example: printing energy values)
            if energy_data:
                energy_wh = energy_data['energy']['values'][0]['value']
                energy_kwh = energy_wh / 1000
                print(f"Energy production for {plant_name} on {today}: {energy_kwh} kWh")

                """
                This is the for post request to add the powerplans in the database.
                If there are any new system are added then only this is used.
                """
                post_plant_details(plant_name)

                """
                This is the post request to get powerplan daily production.
                They have only one smart loger.
                """
                post_daily_power_generation(plant_name, energy_kwh)

                
        print('Solar Edge API calls completed successfully.')

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
