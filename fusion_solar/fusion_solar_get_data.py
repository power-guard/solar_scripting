import requests
import logging
import time
import json
from datetime import datetime, timezone
from typing import Dict, List

from .post_fusion_solar_api_data import (
    post_plant_details,
    post_daily_power_generation
)
from .get_hase_data_script import hase_script

logger = logging.getLogger('fusion_solar')
logger.setLevel(logging.INFO)

class FusionSolarClient:
    '''Client for fetching data from the Fusion Solar API.'''
    base_url = 'https://jp5.fusionsolar.huawei.com/thirdData'
    max_retries = 5
    backoff_factor = 2

    def __init__(self, user_name: str, system_code: str = '', max_retry: int = 10, verify_disable: bool = False):
        self.user_name = user_name
        self.system_code = system_code
        self.max_retry = max_retry

        self.session = requests.session()
        if verify_disable:
            self.session.verify = False
        self.session.headers.update(
            {'Connection': 'keep-alive', 'Content-Type': 'application/json'})

        self.token_expiration_time = 0

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def login(self):
        url = f'{self.base_url}/login'
        body = {'userName': self.user_name, 'systemCode': self.system_code}
        self.session.cookies.clear()
        
        for attempt in range(self.max_retries):
            r = self.session.post(url=url, json=body)
            if r.status_code == 200 and r.json().get('success'):
                self.session.headers.update({'XSRF-TOKEN': r.cookies.get(name='XSRF-TOKEN')})
                self.token_expiration_time = datetime.now(timezone.utc).timestamp() + 30 * 60  # Set token expiration to 30 minutes
                return
            elif r.json().get('failCode') == 20400:
                wait_time = self.backoff_factor ** attempt
                logger.warning(f"Online user limit reached. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                r.raise_for_status()

        raise Exception('Maximum login attempts exceeded due to user login limit.')

    def is_token_expired(self):
        return datetime.now(timezone.utc).timestamp() > self.token_expiration_time

    def ensure_logged_in(self):
        if self.is_token_expired():
            logger.info("Token expired, logging in again...")
            self.login()

    @staticmethod
    def _validate_response(response: requests.Response) -> bool:
        response.raise_for_status()
        body = response.json()
        success = body.get('success', False)
        if not success:
            raise Exception(body)
        return True

    def _request(self, function: str, data=None) -> Dict:
        self.ensure_logged_in()
        if data is None:
            data = {}
        url = f'{self.base_url}/{function}'
        r = self.session.post(url=url, json=data)
        self._validate_response(r)
        return r.json()

    def get_station_kpi_day(self, plant_code: str, date: datetime) -> Dict:
        time = int(date.timestamp()) * 1000
        return self._request('getKpiStationDay', {'stationCodes': plant_code, 'collectTime': time})

# Function to fetch and print daily KPI data for specified sites
def fetch_and_print_daily_kpi(client: FusionSolarClient, target_date: datetime, sites: Dict[str, str]):
    try:
        for site_name, plant_code in sites.items():
            logger.info(f"Fetching data for site: {site_name} (Code: {plant_code})")

            # Fetch daily KPI data for the site
            kpi_data = client.get_station_kpi_day(plant_code, target_date)
            kpi_list = kpi_data.get('data', [])

            # Filter and print data for the target date only
            for data in kpi_list:
                collect_time = datetime.fromtimestamp(data['collectTime'] / 1000.0).strftime('%Y-%m-%d')
                if collect_time == target_date.strftime('%Y-%m-%d'):
                    inverter_power = data['dataItemMap'].get('inverter_power', 0)
                    post_plant_details(site_name)
                    post_daily_power_generation(site_name, inverter_power)
                    print(f"Site: {site_name}, Date: {collect_time}, Inverter Power: {inverter_power} kWh")
        """
            Run the script to get the data from hase 
        """
        hase_script()

    except Exception as e:
        logger.error(f"Error occurred: {e}")

# Main function
def main():

    # Load configuration from JSON file
    with open('fusion_solar/config.json') as config_file:
        config = json.load(config_file)

    target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # Today's date

    for account in config['accounts']:
        user_name = account['user']
        password = account['password']
        sites = account['sites']

        with FusionSolarClient(user_name, password, verify_disable=True) as client:
            fetch_and_print_daily_kpi(client, target_date, sites)

if __name__ == "__main__":
    main()
