import os
import time
import json
from datetime import datetime, timedelta
from urllib.parse import quote
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def log(message):
    """Print a message with a timestamp prefix."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    # Uncomment the line below if you want to run in headless mode
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_next_saturday():
    """Calculate the date of the next Saturday."""
    today = datetime.now()
    days_until_saturday = (5 - today.weekday()) % 7  # 5 is Saturday in weekday()
    if days_until_saturday == 0:  # If today is Saturday, get next Saturday
        days_until_saturday = 7
    return today + timedelta(days=days_until_saturday)

def login_to_courtreserve(driver, username, password):
    """Log in to CourtReserve using provided credentials."""
    try:
        log("Starting reservation process...")
        # Navigate to the login page
        driver.get('https://app.courtreserve.com/Online/Account/Login/12465?isMobileLayout=False')

        # Wait for the username field to be present and enter credentials
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="email"]'))
        )
        username_field.send_keys(username)

        # Find and fill in the password field
        password_field = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
        password_field.send_keys(password)
        
        # Find and click the login button
        login_button = driver.find_element(By.XPATH, "//button[descendant::*[contains(text(), 'Continue')]]")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(3)
        
        # Set the InternalCalendarDate cookie to next Saturday so that the calendar defaults to that. We need this because
        # if you select a date that you already have a reservation it won't let you click for a new one. Saturday seems likely
        # to not have one
        target_date = get_next_saturday().strftime("%-m/%-d/%Y")
        encoded_date = quote(target_date)
        driver.add_cookie({
            'name': 'InternalCalendarDate',
            'value': encoded_date,
            'domain': '.courtreserve.com'
        })
        log(f"Set InternalCalendarDate cookie to {target_date} (encoded: {encoded_date})")
        
        # Now navigate to the bookings page
        driver.get('https://app.courtreserve.com/Online/Reservations/Bookings/12465')
        time.sleep(3)
        
        reserve_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//a[contains(text(), 'Reserve')])[last()]"))
        )
        reserve_link.click()
        time.sleep(3)
        
        form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "createReservation-Form"))
        )
        
        request_data = form.find_element(By.ID, "RequestData").get_attribute("value")
        verification_token = form.find_element(By.NAME, "__RequestVerificationToken").get_attribute("value")
        
        log(f"RequestData: {request_data}")
        log(f"Verification Token: {verification_token}")
        
        auth_data = {
            "request_data": request_data,
            "verification_token": verification_token
        }
        
        with open("auth.json", "w") as f:
            json.dump(auth_data, f, indent=4)
        log("Auth data written to auth.json")
        
        return True
    except Exception as e:
        log(f"An error occurred during login: {str(e)}")
        # Delete auth.json if it exists
        if os.path.exists("auth.json"):
            os.remove("auth.json")
            log("Cleaned up auth.json file after error")
        return False

def main():
    # Delete any existing auth.json at start
    if os.path.exists("auth.json"):
        os.remove("auth.json")
        log("Cleaned up existing auth.json file")
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    username = os.getenv('COURTRESERVE_USERNAME')
    password = os.getenv('COURTRESERVE_PASSWORD')
    
    if not username or not password:
        log("Error: Please set COURTRESERVE_USERNAME and COURTRESERVE_PASSWORD in your .env file")
        return
    
    # Set up the driver
    driver = setup_driver()
    
    try:
        login_to_courtreserve(driver, username, password)
    finally:
        # Keep the browser open for now (remove this in production)
        # input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main() 
