from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

from .post_fusion_solar_api_data import (
    post_plant_details,
    post_daily_power_generation
)

def load_config(config_path='fusion_solar/hase_config.json'):
    with open(config_path) as config_file:
        return json.load(config_file)

def initialize_webdriver(driver_path):
    return webdriver.Chrome(executable_path=driver_path)

def login(driver, login_url, username, password):
    driver.get(login_url)
    wait = WebDriverWait(driver, 10)
    
    username_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="username"]')))
    password_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="value"]')))
    
    username_field.send_keys(username)
    password_field.send_keys(password)
    
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submitDataverify"]')))
    login_button.click()
    
    time.sleep(5)

def fetch_electricity_generation(driver, base_url, site_identifier, ne_number):
    data_url = f'{base_url}/pvmswebsite/assets/build/index.html#/view/station/{ne_number}/overview'
    driver.get(data_url)
    wait = WebDriverWait(driver, 10)
    
    time.sleep(5)
    
    try:
        text_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div/div[3]/div[2]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[1]/div[2]/div/div[1]/div[1]/span')))
        electricity_generation = text_element.text
        post_plant_details(site_identifier)
        post_daily_power_generation(site_identifier, electricity_generation)
        print(f"{site_identifier} site's electricity generation is {electricity_generation} kWh")
    except Exception as e:
        print(f"Failed to retrieve text for {site_identifier}: {e}")

def hase_script():
    config = load_config()

    # Initialize the WebDriver (e.g., Chrome)
    #driver = webdriver.Chrome()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        login(driver, config['base_url'], config['user_name'], config['password'])
        
        for site_identifier, ne_number in config['sites'].items():
            fetch_electricity_generation(driver, config['base_url'], site_identifier, ne_number)
    finally:
        driver.quit()

if __name__ == "__main__":
    hase_script()
