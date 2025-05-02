from config import *

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium_stealth import stealth
from utils.helpers import parse_response

class PopMartBot:
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
            
            # Look for any enabled buttons - more generic approach
            buttons = soup.select(BUY_BUTTON_SELECTOR)
            buy_buttons = [b for b in buttons if BUY_NOW in b.text.lower() or ADD_TO_CART in b.text.lower()]
            
            if buy_buttons:
                print("✅ Product in stock (buy button found).")
                return True
            else:
                print("❌ Still not in stock (no buy button).")
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
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            
            # Handle variant selection dynamically
            self._select_variant(driver, wait)
            
            # Handle quantity adjustment dynamically
            self._adjust_quantity(driver, wait)
            
            # Find and click buy button - using text content for more reliability
            print("🔎 Finding purchase button.")
            buy_buttons = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, BUY_BUTTON_SELECTOR))
            )
            
            # Filter for buttons with text containing "köp" or "buy"
            for button in buy_buttons:
                if BUY_NOW in button.text.lower() or ADD_TO_CART in button.text.lower():
                    button.click()
                    print("✅ Clicked buy.")
                    break
            else:
                # If no buy button was found and clicked
                print("❌ No buy button found.")
                raise Exception("Buy button not found")

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
            
            print("🛒 At checkout.")
            return True

        except Exception as e:
            print(f"🚨 Something went wrong: {e}")
            return False

        finally:
            driver.quit()

    def _adjust_quantity_with_buttons(self, driver, wait):
        """Adjust quantity using + and - buttons when direct input is not possible"""
        try:
            print("🔢 Looking for quantity +/- buttons...")
            
            # Find the plus button - using partial class name
            plus_button = driver.find_element(By.CSS_SELECTOR, "div[class*='countButton']")
            
            if not plus_button:
                print("⚠️ Could not find plus button")
                return
                
            # Find the quantity display/input field
            quantity_input = driver.find_element(By.CSS_SELECTOR, "input[class*='countInput']")
            
            if not quantity_input:
                print("⚠️ Could not find quantity display")
                return
                
            # Get current quantity
            current_quantity = int(quantity_input.get_attribute("value") or "1")
            print(f"📊 Current quantity: {current_quantity}")
            
            # Click the + button until we reach desired quantity or can't increase anymore
            if current_quantity < PREFERRED_QUANTITY:
                previous_quantity = current_quantity
                for _ in range(PREFERRED_QUANTITY - current_quantity):
                    plus_button.click()
                    current_quantity = int(quantity_input.get_attribute("value") or "1")

                    if current_quantity <= previous_quantity:
                        print(f"⚠️ Reached maximum available quantity: {current_quantity}")
                        break

                    previous_quantity = current_quantity
                    time.sleep(0.3)  # Small wait between clicks
                
                print(f"➕ Set quantity to {current_quantity}")


        except Exception as e:
            print(f"⚠️ Could not adjust quantity with buttons: {e}")
            print("⚠️ Continuing with default quantity")
            
    # Try our specialized method first, fall back to the general one if it fails
    def _adjust_quantity(self, driver, wait):
        try:
            self._adjust_quantity_with_buttons(driver, wait)
        except Exception as e:
            print(f"⚠️ Specialized quantity adjustment failed: {e}")
            # Fall back to the original method
    
    def _select_variant(self, driver, wait):
        """Dynamically detect and select product variants (size, color, etc.)"""
        try:
            print("🧩 Looking for product variants...")
            
            whole_set_option = None
            single_box_option = None
            
            try:
                # Find elements containing the text "whole set" (case insensitive)
                whole_set_option = driver.find_element(By.XPATH, 
                    "//*[contains(translate(text(), 'WHOLESET', 'wholeset'), 'whole set')]")
                print("Found 'whole set' option")
            except NoSuchElementException:
                print("No 'whole set' option found")
                
            try:
                # Find elements containing the text "single box" (case insensitive)
                single_box_option = driver.find_element(By.XPATH, 
                    "//*[contains(translate(text(), 'SINGLEBOX', 'singlebox'), 'single box')]")
                print("Found 'single box' option")
            except NoSuchElementException:
                print("No 'single box' option found")
            
            # Select based on preference
            if PREFER_WHOLE_SET and whole_set_option:
                whole_set_option.click()
                print("✅ Selected: Whole set")
            elif not PREFER_WHOLE_SET and single_box_option:
                single_box_option.click()
                print("✅ Selected: Single box")

        except Exception as e:
            print(f"⚠️ Could not select variant: {e}")
            print("⚠️ Continuing with default variant")