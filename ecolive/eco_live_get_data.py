"""
We have only one power plan, so we manually input the site ID and system name. 
site_id = '10'
plant_name = 'PGOMHV100004'
"""
from datetime import date, datetime
import requests
from .post_data import post_plant_details, post_daily_power_generation

class EcoLiveClient:
    """Downloads data from the EcoLive API developed by Power Guard.
    
    Example usage:
    ```
    import datetime
    from ecolive import EcoLiveClient
    today = datetime.date.today()
    site_id = 'PGOMHV100004'

    with EcoLiveClient() as client:
        kwh = client.get_hourly_kwh(today)

        if kwh:
            for timestamp, energy in kwh.items():
                print(timestamp, energy)
        else:
            print("No data available for the given date.")
    ```
    """

    TIMEOUT = (6, 9.05)
    BASE_URI = 'http://176.34.13.254:27500/api'
    SITE_ID = '10'  
    PLANT_NAME = 'PGOMHV100004'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def _get(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.TIMEOUT
        res = requests.get(*args, **kwargs)
        res.raise_for_status()
        return res

    def get_hourly_kwh(self, target_date: date):
        """Download hourly energy generation for a single day in kWh.

        Args:
            target_date (datetime.date): Date for which to download data.

        Returns:
            dict: Keys are timestamps in ISO format. Values are energy generation in kWh, or None if no data is available.
        """
        uri = f'{self.BASE_URI}/hourly/{self.SITE_ID}/{target_date.isoformat()}'
        
        try:
            res = self._get(uri)
            res = res.json()
            return res.get('energySeries', None)
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"Error fetching data: {e}")
            return None

    def get_hourly_data(self, target_date: date):
        """Download hourly energy generation and irradiation for a single day in kWh.

        Args:
            target_date (datetime.date): Date for which to download data.

        Returns:
            tuple: First element is a dict with energy generation data, second element is a dict with irradiation data.
                   Returns (None, None) if no data is available.
        """
        uri = f'{self.BASE_URI}/hourly/{self.SITE_ID}/{target_date.isoformat()}'
        try:
            res = self._get(uri)
            res = res.json()
            return res.get('energySeries', None), res.get('irradiationSeries', None)
        except (requests.exceptions.RequestException, KeyError) as e:
            print(f"Error fetching data: {e}")
            return None, None

def main():
    today = date.today()
    system_id = EcoLiveClient.PLANT_NAME

    with EcoLiveClient() as client:
        kwh = client.get_hourly_kwh(today)

        if kwh:
            total_energy = sum(kwh.values())
            
            post_plant_details(system_id)
            post_daily_power_generation(system_id, total_energy)

            print(f"Total energy generated for {system_id}: {total_energy} kWh")
        else:
            print("No data available for the given date.")

if __name__ == "__main__":
    main()
