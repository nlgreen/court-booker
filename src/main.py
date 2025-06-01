import os
import time
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

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

def login_to_courtreserve(driver, username, password):
    """Log in to CourtReserve using provided credentials."""
    try:
        # Navigate to the login page
        driver.get('https://app.courtreserve.com/Online/Account/Login/12465?isMobileLayout=False')
        
        # Wait for the page to load and take a screenshot
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "UserNameOrEmail"))
        )
        driver.save_screenshot("login_page.png")
        print("Screenshot saved as 'login_page.png'")

        # Wait for the username field to be present and enter credentials
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "UserNameOrEmail"))
        )
        username_field.send_keys(username)
        
        # Find and fill in the password field
        password_field = driver.find_element(By.ID, "Password")
        password_field.send_keys(password)
        
        # Find and click the login button
        login_button = driver.find_element(By.CSS_SELECTOR, "#loginForm button[type='button']")
        login_button.click()
        
        # Wait for login to complete (you might want to adjust this based on what appears after login)
        time.sleep(3)
        
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
        
        print("RequestData:", request_data)
        print("Verification Token:", verification_token)
        
        auth_data = {
            "request_data": request_data,
            "verification_token": verification_token
        }
        
        with open("auth.json", "w") as f:
            json.dump(auth_data, f, indent=4)
        print("Auth data written to auth.json")
        
        return True
    except Exception as e:
        print(f"An error occurred during login: {str(e)}")
        return False

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials from environment variables
    username = os.getenv('COURTRESERVE_USERNAME')
    password = os.getenv('COURTRESERVE_PASSWORD')
    
    if not username or not password:
        print("Error: Please set COURTRESERVE_USERNAME and COURTRESERVE_PASSWORD in your .env file")
        return
    
    # Set up the driver
    driver = setup_driver()
    
    try:
        # Attempt to log in
        if login_to_courtreserve(driver, username, password):
            print("Successfully logged in!")
            # Add your booking logic here
        else:
            print("Failed to log in")
    finally:
        # Keep the browser open for now (remove this in production)
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main() 