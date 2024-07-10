import requests
import os
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree
import yaml
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from .post_data import (
    post_plant_details,
    post_daily_power_generation
)


class BasicAuthConfig:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class SolarLinkApiClient():

    TIMEOUT = (5, 3.05)
    BASE_URL = 'https://services.energymntr.com/megasolar/'

    def __init__(self, config: BasicAuthConfig):
        """The 'username' in the config object should contain
        the site ID as defined in SolarLink.
        This can usually be found in the URL.
        """
        self.config = config
        self.auth = HTTPDigestAuth(config.username, config.password)

    def _get(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.TIMEOUT
        if 'auth' not in kwargs:
            kwargs['auth'] = self.auth
        res = requests.get(*args, **kwargs)
        res.raise_for_status()
        return res

    def get_site_daily(self, yyyymmdd: str):
        """Get daily production data for an entire site.

        Args:
            yyyymmdd (str) - Date for which data is to
                        be fetched, in YYYYMMDD format.
        Returns:
            (float) Gross generation in kwh
            for the entire site for the specified day.
        """
        endpoint = '/services/api/generating/daily.php'
        endpoint = self.BASE_URL + self.config.username + endpoint
        
        params = {
            'unit': 'total',
            'groupid': 1,
            'time': f'{yyyymmdd}000000',
            'failure': 'false',
        }

        res = self._get(endpoint, params=params)
        
        try:
            root = ElementTree.fromstring(res.content)
        except ElementTree.ParseError:
            raise Exception('Failed to parse XML.')

        ac_energy = None
        for child in root.iter():
            if child.tag == 'apiStatus':
                if child.text != 'succeed':
                    raise Exception('SolarLink API reports failure.')

            if child.tag == 'acEnergy':
                ac_energy = child.text

        if ac_energy is not None:
            try:
                ac_energy = float(ac_energy)
                return ac_energy
            except ValueError:
                raise Exception(f'Failed to parse acEnergy value "{ac_energy}".')

        raise Exception('Could not fetch data.')

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    yml_file_path  = os.path.join(current_dir, 'credentials.yml')
    # Load credentials from YAML file
    with open(yml_file_path, 'r') as file:
        credentials = yaml.safe_load(file)

    # Get the current date in YYYYMMDD format
    #date_to_fetch = (datetime.now() - timedelta(1)).strftime('%Y%m%d')
    date_to_fetch = datetime.now().strftime('%Y%m%d')
    for system_id, creds in credentials.items():
        site_id = creds['site_id']
        password = creds['password']

        config = BasicAuthConfig(username=site_id, password=password)
        client = SolarLinkApiClient(config)

        try:
            energy_data = client.get_site_daily(date_to_fetch)

            post_plant_details(system_id)
            post_daily_power_generation(system_id, energy_data)

            print(f"Daily energy production of {system_id} on {date_to_fetch}: {energy_data} kWh")
        except:
            """
                If unable to fetch the data via use automation
            """
            print(f"Error fetching data from API now using script.")

            automate_get_data(system_id, site_id, password, date_to_fetch)


def automate_get_data(system_id, site_id, password, date_to_fetch):
    
    url = f"https://laplaceid.energymntr.com/?callback=https://services.energymntr.com/megasolar/{site_id}/login/index.php"

    # Initialize the WebDriver (e.g., Chrome)
    #driver = webdriver.Chrome()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        # Open the login page
        driver.get(url)

        # Wait for the username field to be present
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'idtext')))

        # Find the username and password fields and the login button
        username_field = driver.find_element(By.NAME, 'idtext')
        password_field = driver.find_element(By.NAME, 'pwtext')
        login_button = driver.find_element(By.XPATH, '//*[@id="loginWidget"]/div/div[2]/div/div[2]/button')

        # Enter the username and password
        username_field.send_keys(site_id)
        password_field.send_keys(password)

        # Click the login button
        login_button.click()

        # Wait for the login to complete and the next page to load
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="widgetArea"]/div/div[3]/div/div[2]/p[2]')))

        # Find the element with the required text
        daily_prod = driver.find_element(By.XPATH, '//*[@id="widgetArea"]/div/div[3]/div/div[2]/p[2]')

        # Copy the text from the element
        energy_data = daily_prod.text
        
        post_plant_details(system_id)
        post_daily_power_generation(system_id, energy_data)

        print(f"Daily energy production of {system_id} on {date_to_fetch}: {energy_data} kWh")
        

    finally:
        # Close the browser after a short wait to observe the result
        time.sleep(5)  # Adjust time as needed
        driver.quit()