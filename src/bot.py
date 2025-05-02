from config import *

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from utils.helpers import parse_response

class ShoppingBot:
    def __init__(self):
        self.session = requests.Session()

    def login(self):
        payload = {
            'username': USERNAME,
            'password': PASSWORD
        }
        response = self.session.post(LOGIN_URL, data=payload)
        return response.ok

    def check_product(self):
        try:
            response = requests.get(PRODUCT_URL, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                print(f"Error when fetching product: {response.status_code}")
                return False

            soup = parse_response(response.text)

            if IN_STOCK_TEXT.lower() in soup.text.lower():
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

        driver = webdriver.Chrome(options=options)

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        try:
            print("🛒 Open product page")
            driver.get(PRODUCT_URL)
            
            # Wait for page to load instead of fixed time delay
            wait = WebDriverWait(driver, 10)

            print("🔎 Finding purchase button.")
            buy_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, BUY_BUTTON_SELECTOR))
            )
            
            buy_button.click()
            print("✅ Clicked buy.")

            # Wait for cart update
            wait.until(
                EC.url_contains("shoppingCart")
            )

            # Go to checkout
            driver.get(CHECKOUT_URL)

            # Wait for checkout page to load
            wait.until(
                EC.url_contains("checkout")
            )

            # Select delivery options etc
            
            print("🛒 At checkout.")
            return True

        except Exception as e:
            print(f"🚨 Something went wrong: {e}")
            return False

        finally:
            driver.quit()