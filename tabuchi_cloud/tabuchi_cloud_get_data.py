import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .post_data import (
    post_plant_details,
    post_daily_power_generation
)


def load_credentials(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['credentials'][0]

def initialize_driver():

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

def login(driver, base_url, user_id, password):
    driver.get(base_url)
    
    # Wait for the login fields to be available
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="thingworx-form-userid"]'))
    )
    
    username_field = driver.find_element(By.XPATH, '//*[@id="thingworx-form-userid"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="thingworx-form-password"]')
    login_button = driver.find_element(By.XPATH, '//*[@id="btnlogin"]')
    
    username_field.send_keys(user_id)
    password_field.send_keys(password)
    login_button.click()
    
def get_energy_generation(driver):
    # Wait for the energy generation element to be available
    energy_generation_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root_pagemashupcontainer-1_ValueDisplay-373"]/table/tbody/tr/td/div/div/div'))
    )
    return energy_generation_element.text

def main():
    # Load credentials
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(current_dir, 'credentials.json')

    credentials = load_credentials(json_file_path)
    
    # Initialize WebDriver
    driver = initialize_driver()
    
    try:
        # Perform login
        login(driver, credentials['base_url'], credentials['id'], credentials['password'])
        system_id = credentials['plan']
        # Get energy generation value
        energy_data = get_energy_generation(driver)
        print(f"{system_id} Energy Generation: {energy_data}")
        post_plant_details(system_id)
        post_daily_power_generation(system_id, energy_data)
        
    finally:
        # Quit the driver
        driver.quit()

if __name__ == "__main__":
    main()
