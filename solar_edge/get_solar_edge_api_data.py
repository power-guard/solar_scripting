import requests
import yaml
from datetime import datetime
from .post_solar_edge_api_data import (
    post_plant_details,
    post_daily_power_generation
)


def main():
    try:
        # from solaredge import solaredge_api

        # Load the configuration from the external YAML file
        with open('solar_edge/plant_id_token.yml', 'r') as file:
            data = yaml.safe_load(file)

        api_key = data['solar_edge_bulk']['api_key']
        plants = data['solar_edge_bulk']['plants']

        base_url = "https://monitoringapi.solaredge.com"

        # Function to get plant energy production for today
        def get_plant_energy(plant_id, date):
            url = f"{base_url}/site/{plant_id}/energy.json"
            params = {
                'api_key': api_key,
                'startDate': date,
                'endDate': date,
                'timeUnit': 'DAY'
            }
            response = requests.get(url, params=params)
            return response.json()

        # Get today's date in the required format
        today = datetime.now().strftime('%Y-%m-%d')

        # Example usage
        for plant_name, plant_id in plants.items():
            energy = get_plant_energy(plant_id, today)
            # Extracting the value in Wh
            energy_wh = energy['energy']['values'][0]['value']
            energy_kwh = energy_wh / 1000
            print(f"Energy production for {plant_name} on {today}: {energy_kwh} kwh")

            """
                This is the for post request to add the powerplans in the database.
                If there are any new system are added then only this is used.
            """
            #post_plant_details(plant_name)

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
