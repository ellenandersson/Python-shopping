import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from utils.helpers import parse_response

class ShoppingBot:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

    def login(self, username, password):
        login_url = self.config['LOGIN_URL']
        payload = {
            'username': username,
            'password': password
        }
        response = self.session.post(login_url, data=payload)
        return response.ok

    def check_product(self):
        headers = self.config['HEADERS']
        product_url = self.config['CHECKOUT_URL']
        in_stock_text = self.config['IN_STOCK_TEXT']
        try:
            response = requests.get(product_url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Error when fetching product: {response.status_code}")
                return False

            soup = parse_response(response.text)

            if in_stock_text.lower() in soup.text.lower():
                print("✅ Product in stock.")
                return True
            else:
                print("❌ Still not in stock.")
                return False

        except requests.RequestException as e:
            print(f"Network error: {e}")
            return False
        
        
    def buy_product(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Turn on --headless if you wanna run it in the background
        # options.add_argument("--headless")

        driver = webdriver.Firefox(options=options)

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        try:
            product_page = self.config['PRODUCT_URL']
            checkout_page = self.config['CHECKOUT_URL']
            buy_button = self.config['BUY_BUTTON_SELECTOR']
            print("🛒 Open product page")
            driver.get(product_page)
            time.sleep(random.uniform(2, 5))  # Wait like a real user

            print("🔎 Finding purchase button.")
            buy_button = driver.find_element(By.CSS_SELECTOR, buy_button)
            buy_button.click()

            print("✅ Clicked buy.")

            time.sleep(random.uniform(2, 4))

            # Go to checkout
            driver.get(checkout_page)

            # Select delivery options etc
            
            print("🛒 At checkout.")

        except Exception as e:
            print(f"🚨 Something went wrong: {e}")

        finally:
            driver.quit()