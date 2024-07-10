import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .post_data import (
    post_plant_details,
    post_daily_power_generation
)

def load_config(file_path):
    """Load configuration from JSON file."""
    with open(file_path) as config_file:
        return json.load(config_file)

def setup_driver():
    """Set up and return the WebDriver instance."""
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    return driver

def login(driver, base_url, username, password):
    """Log in to the website."""
    driver.get(base_url)
    wait = WebDriverWait(driver, 200)

    username_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="username"]')))
    password_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="value"]')))

    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="submitDataverify"]')))
    login_button.click()
    time.sleep(5)

def click_first_available_search_button(driver):
    """Click the first available search button."""
    xpaths = [
        '//*[@id="rc-tabs-0-panel-inverter"]/div/div/div[1]/div[1]/div/form/div[4]/div/div/div/button',
        '//*[@id="rc-tabs-1-panel-inverter"]/div/div/div[1]/div[1]/div/form/div[4]/div/div/div/button',
        '//*[@id="rc-tabs-2-panel-inverter"]/div/div/div[1]/div[1]/div/form/div[4]/div/div/div/button'
    ]

    for xpath in xpaths:
        try:
            search_button = driver.find_element(By.XPATH, xpath)
            search_button.click()
            return True
        except:
            continue
    return False

def interact_with_first_available_search_table(driver, word_to_search):
    """Interact with the first available search table and calculate total electricity generation."""
    xpaths = [
        '//*[@id="rc-tabs-0-panel-inverter"]/div/div/div[2]/div[2]/div/div/div/div/div[2]/table',
        '//*[@id="rc-tabs-1-panel-inverter"]/div/div/div[2]/div[2]/div/div/div/div/div[2]/table',
        '//*[@id="rc-tabs-2-panel-inverter"]/div/div/div[2]/div[2]/div/div/div/div/div[2]/table'
    ]

    for xpath in xpaths:
        try:
            table_element = driver.find_element(By.XPATH, xpath)
            rows = table_element.find_elements(By.TAG_NAME, 'tr')

            total_elect_gen = 0.0
            for row in rows[1:]:
                td_4 = row.find_element(By.XPATH, './td[4]')
                td_4_value = float(td_4.text.strip())
                total_elect_gen += td_4_value
            total_elect_gen = round(total_elect_gen, 3)
            post_plant_details(word_to_search)
            post_daily_power_generation(word_to_search, total_elect_gen)
            print(f"{word_to_search}: {total_elect_gen}")    

            return True
        except Exception as e:
            print(f"Table in this '{xpath}' is not found.")
            continue
    
    return False

def process_sites(driver, config, base_url):
    """Process each site and interact with elements."""
    for site_identifier, site_details in config['sites'].items():
        print(f'Loading report url {site_details["id"]}.')
        data_url = f'{base_url}/pvmswebsite/assets/build/index.html#/view/station/{site_details["id"]}/report'
        driver.get(data_url)
        time.sleep(5)

        wait = WebDriverWait(driver, 200)
        base_xpath = "//*[@id='root']/div/div/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div[1]/div[1]/div"
        full_xpath = f"{base_xpath}//*[contains(text(), 'Inverter Report')]"

        inverter_report = wait.until(EC.presence_of_element_located((By.XPATH, full_xpath)))
        inverter_report.click()
        time.sleep(3)

        dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="inverter-report-nco-tree-select-customized"]/span')))
        dropdown.click()
        time.sleep(1)

        for system_id in site_details['system']:
            word_to_search = system_id

            first_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{word_to_search}')]")
            first_element.click()
            time.sleep(1)

        
            if not click_first_available_search_button(driver):
                print("No search button found")
            time.sleep(5)

            if interact_with_first_available_search_table(driver, word_to_search):
                print("Interacted with the first available search table.")
            else:
                print("No clickable search table found or error occurred.")

            dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="inverter-report-nco-tree-select-customized"]/span')))
            dropdown.click()
            time.sleep(5)

            first_element.click()

        print(f'End report url {site_details["id"]}.')

def main():
    config = load_config('om_config.json')
    driver = setup_driver()
    try:
        login(driver, config['base_url'], config['user_name'], config['password'])
        process_sites(driver, config, config['base_url'])
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
