from config import *
from utils.helpers import accept_cookies

import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium_stealth import stealth

class PopMartBot:
    def __init__(self):
        self.session = requests.Session()
        self.driver = None
        self.wait = None
        self._initialize_driver()
        
    def _initialize_driver(self):
        """Initialize the WebDriver to be used throughout the entire bot session"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # Turn on --headless if you wanna run it in the background
        # options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Linux",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        
    def cleanup(self):
        """Clean up resources when bot is done or encounters a fatal error"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
                self.wait = None

    def login(self):
        """Log in to the website using the shared WebDriver instance"""
        if not self.driver:
            self._initialize_driver()
            
        try:
            print("🔐 Navigating to login page.")
            self.driver.get(LOGIN_URL)
            
            accept_cookies(self.driver)
            
            # Look for common email field patterns
            print("🔍 Finding email field.")
            username_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    "input[type='email'], input[name='email'], input[id*='email'], input[name='username'], input[id*='username']"))
            )

            if not username_field:
                print("❌ Email field not found.")
                return False
            
            # Fill in email
            print("✏️ Entering email")
            username_field.clear()
            username_field.send_keys(POPMART_USERNAME)
            
            # Find continue button
            print("🔍 Finding continue button...")
            continue_button_xpath_patterns = [
                "//button[contains(translate(text(), 'CONTINUECONTINU', 'continuecontinu'), 'continue')]"
            ]
            
            continue_button = None
            for xpath in continue_button_xpath_patterns:
                try:
                    buttons = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_all_elements_located((By.XPATH, xpath))
                    )
                    if buttons:
                        continue_button = buttons[0]
                        break
                except Exception:
                    print(f"❌ Continue button not found with XPath: {xpath}")
                    return False
            
            # If we found the continue button, click it
            continue_button.click()
            time.sleep(0.5)
            
            # Look for password field
            print("🔍 Finding password field...")
            password_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )

            if not password_field:
                print("❌ password field not found.")
                return False
            
            password_field.clear()
            password_field.send_keys(POPMART_PASSWORD)
            
            # Find submit button
            print("🔍 Finding login button...")
            submit_button_xpath_patterns = [
                "//button[contains(@class, 'loginButton')]", 
                "//button[contains(@class, 'index_loginButton')]"
            ]
            
            submit_button = None
            for xpath in submit_button_xpath_patterns:
                try:
                    buttons = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_all_elements_located((By.XPATH, xpath))
                    )
                    if buttons:
                        submit_button = buttons[0]
                        break
                except Exception:
                    continue
            
            if submit_button:
                print("🖱️ Clicking submit button")
                # Scroll to the button first
                self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5)  # Small wait after scrolling
                
                try:
                    # Try clicking with ActionChains
                    from selenium.webdriver.common.action_chains import ActionChains
                    ActionChains(self.driver).move_to_element(submit_button).click().perform()
                    print("✅ Clicked login button using ActionChains")
                except Exception as e:
                    print(f"⚠️ ActionChains click failed: {e}")
                    try:
                        # Try regular click
                        submit_button.click()
                        print("✅ Clicked login button with regular click")
                    except Exception as e:
                        print(f"⚠️ Regular click failed: {e}")
                        # Try JavaScript click as last resort
                        self.driver.execute_script("arguments[0].click();", submit_button)
                        print("✅ Clicked login button with JavaScript")
                
                # Wait for redirect after login (either to homepage or dashboard)
                try:
                    self.wait.until(EC.url_changes(LOGIN_URL))
                    if self.driver.current_url == LOGIN_URL:
                        print("❌ Still on login page after clicking submit.")
                        return False
                    print("✅ Login successful! Redirected from login page.")
                except Exception:
                    # Sometimes the URL might not change on successful login
                    # Check for elements that would appear after successful login
                    try:
                        self.wait.until(EC.presence_of_element_located((
                            By.CSS_SELECTOR, ".user-account, .account, .profile, .my-account, .logout"
                        )))
                        print("✅ Login successful! Found account-related elements.")
                    except Exception as e:
                        print(f"⚠️ Could not confirm successful login: {e}")
                
                selenium_cookies = self.driver.get_cookies()
                for cookie in selenium_cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                return True
            else:
                print("❌ Login button not found.")
                return False
                
        except Exception as e:
            print(f"🚨 Login failed: {e}")
            return False

    def check_product(self):
        """Check if the product is available using Selenium to process JavaScript-rendered content"""
        try:
            if not self.driver:
                self._initialize_driver()

            print("🔍 Checking product availability using Selenium...")
            self.driver.get(PRODUCT_URL)
            
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='index_price']"))
            )

            available = False

            size_items = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'index_sizeInfoItem')]")

            if size_items:
                print(f"📏 Found {len(size_items)} size options")
                
                # Check if all size items are disabled
                for item in size_items:
                    class_name = item.get_attribute("class")
                    if "disabled" not in class_name:
                        print("✅ Found available size option")
                        available = True
                        break
            else:
                if self._find_buy_button():
                    available = True
                else:
                    available = False

            return available


        except Exception as e:
            print(f"🚨 Error checking product availability: {e}")
            return False
        
        
    def buy_product(self):
        """Buy the product using the shared WebDriver instance"""
        if not self.driver:
            print("❌ No active browser session. Please login first.")
            return False

        try:
            # Assume we're already on the product page from check_product
            # If not, navigate there
            if PRODUCT_URL not in self.driver.current_url:
                print("🛒 Opening product page")
                self.driver.get(PRODUCT_URL)
                
            # Wait for page to fully load
            time.sleep(1)
            
            # Handle variant selection dynamically
            self._select_variant(self.driver)
            
            # Handle quantity adjustment dynamically
            self._adjust_quantity(self.driver)
            
            buy_button = self._find_buy_button()
            if not buy_button:
                print("❌ Buy button not found. Product may not be available.")
                return False
            
            buy_button.click()

            ## TODO fix here

            # Wait for cart update
            self.wait.until(
                EC.url_contains("shoppingCart")
            )

            # Go to checkout
            self.driver.get(CHECKOUT_URL)

            # Wait for checkout page to load
            self.wait.until(
                EC.url_contains("checkout")
            )
            
            print("🛒 At checkout.")
            
            # Don't quit the driver here - let main program decide when to quit
            return True

        except Exception as e:
            print(f"🚨 Something went wrong: {e}")
            # Don't clean up on purchase failure - might be temporary
            return False

    def _adjust_quantity_with_buttons(self, driver):
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
    def _adjust_quantity(self, driver):
        try:
            self._adjust_quantity_with_buttons(driver)
        except Exception as e:
            print(f"⚠️ Specialized quantity adjustment failed: {e}")
    
    def _select_variant(self, driver):
        """Dynamically detect and select product variants (size, color, etc.)"""
        try:
            print("🧩 Looking for product variants...")
            
            whole_set_option = None
            single_box_option = None
            
            try:
                # Find elements containing the text "whole set" (case insensitive)
                whole_set_option = driver.find_element(By.XPATH, 
                    "//*[contains(translate(text(), 'WHOLESET', 'wholeset'), 'whole set')]")
                class_name = whole_set_option.get_attribute("class")
                print("Found 'whole set' option")
                if "disabled" in class_name:
                    whole_set_option = None
                    print("Whole set option is out of stock")
            except NoSuchElementException:
                print("No 'whole set' option found")
                
            try:
                # Find elements containing the text "single box" (case insensitive)
                single_box_option = driver.find_element(By.XPATH, 
                    "//*[contains(translate(text(), 'SINGLEBOX', 'singlebox'), 'single box')]")
                class_name = single_box_option.get_attribute("class")
                print("Found 'single box set' option")
                if "disabled" in class_name:
                    single_box_option = None
                    print("Single set option is out of stock")
            except NoSuchElementException:
                print("No 'single box' option found")

            if not whole_set_option and not single_box_option:
                print("❌ No available variant options found.")
                return
            
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


        
    def _find_buy_button(self):
        # Look for buy buttons - try multiple selectors for better reliability
        buy_button_selectors = [
            BUY_BUTTON_SELECTOR,
            "button.buy, button.add-to-cart, button.buy-now, button.add",
            "button:contains('Buy'), button:contains('Add')",
            "div[role='button'][class*='buy'], div[role='button'][class*='cart']",
            "button[type='button']:not([disabled])"
        ]
        
        found_buy_button = None
        for selector in buy_button_selectors:
            try:
                # Use a short timeout to avoid long waits for non-existent elements
                buttons = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                
                # Check if any of the buttons have buy-related text
                for button in buttons:
                    button_text = button.text.lower()
                    if BUY_NOW.lower() in button_text or ADD_TO_CART.lower() in button_text or 'buy' in button_text or 'add to cart' in button_text:
                        print(f"✅ Product in stock! Found buy button with text: '{button.text}'")
                        found_buy_button = button
                        break
            except Exception:
                # Continue trying other selectors
                continue
            
            if found_buy_button:
                break
        
        # Try an alternative approach if no buttons found - look by XPath for text
        if not found_buy_button:
            try:
                buy_xpath = "//button[contains(translate(text(), 'BUYNOWADD', 'buynowadd'), 'buy') or contains(translate(text(), 'BUYNOWADD', 'buynowadd'), 'add to cart')]"
                buy_buttons = self.driver.find_elements(By.XPATH, buy_xpath)
                if buy_buttons:
                    print(f"✅ Product in stock! Found buy button with XPath with text: '{buy_buttons[0].text}'")
                    found_buy_button = buy_buttons[0]
            except Exception as e:
                print(f"⚠️ XPath button search error: {e}")
                
        return found_buy_button