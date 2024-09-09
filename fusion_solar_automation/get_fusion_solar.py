import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

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
        '/html/body/div[3]/div/div/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/div/div[1]/div[1]/div/form/div[4]/div/div/div/div/button'
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
    try:
        # Check if the table body element exists by the provided XPath
        table_element = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div/div/div/div[2]/table/tbody')

        try:
            # Find all <tr> elements within the table body
            tr_elements = table_element.find_elements(By.TAG_NAME, 'tr')
            tr_count = len(tr_elements)

            print(f"Number of <tr> tags: {tr_count}")
            total_sum = 0  
            # Loop from 2 to tr_count (Python uses zero-based index)
            for i in range(1, tr_count):  # Loop starts from index 1 for the second <tr> element
                # Dynamically construct the XPath for each row's <td[4]> <span>
                dynamic_xpath = f'/html/body/div[3]/div/div/div/div/div[3]/div[2]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div/div/div/div[2]/table/tbody/tr[{i + 1}]/td[4]/span'

                try:
                    # Locate the <span> element based on the dynamically constructed XPath
                    span_element = driver.find_element(By.XPATH, dynamic_xpath)
                    span_text = span_element.text.strip()

                    # Convert the text to a float (or int) if it's numeric and add to the total sum
                    try:
                        number = float(span_text)  # Use float for decimal values, change to int if you expect only integers
                        total_sum += number
                        #print(f"Row {i + 1}, <td[4]> <span> text: {span_text} (number added to sum)")
                    except ValueError:
                        print(f"Row {i + 1}, <td[4]> <span> text: '{span_text}' is not a valid number") 
                except NoSuchElementException:
                    print(f"Row {i + 1}, <td[4]> <span> not found")
            total_sum_rounded = round(total_sum, 3)
            post_plant_details(word_to_search)
            post_daily_power_generation(word_to_search, total_sum)
            print(f"{word_to_search}: {total_sum_rounded}")
        except NoSuchElementException:
            print("No such table row")
    except NoSuchElementException:
        print("Table element not found")
        

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
