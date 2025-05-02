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
            
            self._accept_cookies(self.driver)
            
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
                "//button[contains(translate(text(), 'CONTINUECONTINU', 'continuecontinu'), 'continue')]",
                "//a[contains(translate(text(), 'LOGINSGN', 'loginsgn'), 'login')]",
                "//a[contains(translate(text(), 'LOGINSGN', 'loginsgn'), 'sign in')]",
                "//button[contains(@class, 'loginButton')]",
                "//button[contains(@class, 'index_loginButton')]",
                "//button[contains(@class, 'ant-btn-primary')]"
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
            # Try multiple XPath patterns for login buttons
            submit_button_xpath_patterns = [
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(translate(text(), 'LOGINSGN', 'loginsgn'), 'login')]",
                "//button[contains(translate(text(), 'LOGINSGN', 'loginsgn'), 'sign in')]",
                "//button[contains(translate(text(), 'LOGINSGN', 'loginsgn'), 'log in')]",
                "//a[contains(translate(text(), 'LOGINSGN', 'loginsgn'), 'login')]",
                "//a[contains(translate(text(), 'LOGINSGN', 'loginsgn'), 'sign in')]",
                "//button[contains(@class, 'loginButton')]",  # The specific class from your error
                "//button[contains(@class, 'index_loginButton')]"  # Even more specific class
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
                        # We'll assume login succeeded and continue
                
                # Set cookies from browser session to requests session
                selenium_cookies = self.driver.get_cookies()
                for cookie in selenium_cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])
                
                return True
            else:
                print("❌ Login button not found.")
                self.cleanup()  # Clean up on critical failure
                return False
                
        except Exception as e:
            print(f"🚨 Login failed: {e}")
            self.cleanup()  # Clean up on critical failure
            return False

    def check_product(self):
        """Check if the product is available using both the driver and requests"""
        try:
            # First try with requests for speed
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
                
                # If we found it with requests, navigate there with the driver to prepare for purchase
                if self.driver:
                    print("🔄 Navigating to product page to prepare for purchase...")
                    self.driver.get(PRODUCT_URL)
                    
                return True
            else:
                print("❌ Still not in stock (no buy button).")
                return False

        except requests.RequestException as e:
            print(f"Network error: {e}")
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
            self._select_variant(self.driver, self.wait)
            
            # Handle quantity adjustment dynamically
            self._adjust_quantity(self.driver, self.wait)
            
            # Find and click buy button - using text content for more reliability
            print("🔎 Finding purchase button.")
            buy_buttons = self.wait.until(
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

    def _accept_cookies(self):
        # Handle cookie/policy banner with improved approach to avoid stale element references
        try:
            print("🍪 Looking for cookie/policy consent banners...")
            # Common selectors for cookie/policy banners
            banner_selectors = [
                ".policy_aboveFixedContainer__KfeZi",  # The specific class from your error
                "div[class*='cookie']", 
                "div[class*='consent']", 
                "div[class*='policy']", 
                "div[class*='gdpr']",
                "div[id*='cookie']", 
                "div[id*='consent']", 
                "div[id*='policy']", 
                "div[id*='gdpr']"
            ]
            
            # Common button texts for accept buttons
            accept_texts = ['accept', 'acceptera', 'ok', 'got it', 'agree', 'close', 'accept all']
            
            # Use a more resilient approach for each banner selector
            for selector in banner_selectors:
                try:
                    # Use explicit wait to find banners
                    banners = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    
                    if banners:
                        print(f"Found potential banner with selector: {selector}")
                        
                        # Try different approaches to find and click buttons
                        # 1. Try direct XPath with text for accept buttons
                        for text in accept_texts:
                            try:
                                xpath = f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]"
                                buttons = WebDriverWait(self.driver, 1).until(
                                    EC.presence_of_all_elements_located((By.XPATH, xpath))
                                )
                                if buttons:
                                    # Use JavaScript click to avoid interception
                                    self.driver.execute_script("arguments[0].click();", buttons[0])
                                    print(f"✅ Clicked accept button with text: {text}")
                                    time.sleep(1)  # Wait for banner to disappear
                                    break
                            except Exception:
                                continue
                                
                        # 2. If no text buttons worked, try any buttons within the banner
                        try:
                            for banner in banners:
                                # Use JavaScript to find buttons inside the banner
                                buttons = self.driver.execute_script(
                                    "return arguments[0].querySelectorAll('button, .button, [role=\"button\"]');", 
                                    banner
                                )
                                if buttons:
                                    self.driver.execute_script("arguments[0].click();", buttons[0])
                                    print("✅ Clicked first button in banner")
                                    time.sleep(1)
                                    break
                        except Exception:
                            pass
                        
                        # 3. As a last resort, try to hide the banner with JavaScript
                        try:
                            self.driver.execute_script(
                                f"document.querySelectorAll('{selector}').forEach(el => el.style.display = 'none');"
                            )
                            print(f"✅ Tried to hide banner with selector: {selector}")
                            time.sleep(0.5)
                        except Exception:
                            pass
                except Exception:
                    continue
        except Exception as e:
            print(f"⚠️ Error handling cookie banners: {e}")