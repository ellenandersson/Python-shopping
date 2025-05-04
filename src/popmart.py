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
    
    def start(self):
        if not self.driver:
            self._initialize_driver()
        print("🚀 Starting PopMart bot...")
        self.driver.get(BASE_URL)
        accept_cookies(self.driver)

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

            print("✅ Product page loaded successfully.")

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
                print("❌ No size options found. Checking buy button directly.")
                if self._find_buy_button():
                    print("✅ Found buy button. Product is available.")
                    available = True
                else:
                    print("❌ No buy button found. Product may not be available.")
                    available = False

            return available


        except Exception as e:
            print(f"🚨 Error checking product availability: {e}")
            return False
        
        
    def buy_product(self):
        """Buy the product using the shared WebDriver instance"""
        try:
            # Assume we're already on the product page from check_product
            # If not, navigate there
            if PRODUCT_URL not in self.driver.current_url:
                print("🛒 Opening product page")
                self.driver.get(PRODUCT_URL)
                
            # Wait for page to fully load
            time.sleep(1)

            # Handle variant selection dynamically
            self._select_variant()
            
            # Handle quantity adjustment dynamically
            self._adjust_quantity()
            
            buy_button = self._find_buy_button()
            if not buy_button:
                print("❌ Buy button not found. Product may not be available.")
                return False
            
            buy_button.click()

            # Wait for the guest checkout popup to appear
            print("⏳ Waiting for guest checkout popup...")
            try:
                # Try multiple XPath approaches to find the guest checkout button
                guest_checkout_xpaths = [
                    "//button[contains(., 'GUEST') or contains(., 'Guest')]"
                ]
                
                guest_checkout_button = None
                for xpath in guest_checkout_xpaths:
                    try:
                        guest_checkout_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        print(f"✅ Found guest checkout button with xpath: {xpath}")
                        break
                    except:
                        continue
                        
                if guest_checkout_button:
                    guest_checkout_button.click()
                    print("✅ Clicked guest checkout button")
                else:
                    print("❌ Could not find guest checkout button with any of the attempted selectors")
                    return False
            except Exception as e:
                print(f"⚠️ Guest checkout button not found: {e}")
                return False

            # Wait for cart update
            self.wait.until(
                EC.url_contains("order-confirmation")
            )
            
            print("🛒 At checkout.")
            self._fill_email()
            self._fill_address_book()

            # Wait for the delivery options to load
            try:
                delivery_text = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'delivery') or contains(text(), 'Delivery')]"))
                )
                print(f"✅ Found delivery options text: '{delivery_text.text}'")
            except Exception as e:
                print(f"⚠️ Delivery options text not found: {e}")
                return False

            # Wait for the proceed to pay button to appear
            try:
                proceed_to_pay_xpaths = [
                    "//button[contains(., 'PAY') or contains(., 'Place Order')]",
                ]
                
                proceed_to_pay_button = None
                for xpath in proceed_to_pay_xpaths:
                    try:
                        proceed_to_pay_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        print(f"✅ Found proceed to pay button with xpath: {xpath}")
                        break
                    except:
                        continue
                        
                if proceed_to_pay_button:
                    print ("✅ Proceed to pay button found, clicking...")
                    self.driver.execute_script("arguments[0].click();", proceed_to_pay_button)
                    print("✅ Clicked proceed to pay button")
                else:
                    print("❌ Could not find proceed to pay button with any of the attempted selectors")
                    return False
            except Exception as e:
                print(f"⚠️ Proceed to pay button not found: {e}")
                return False
            
            return True

        except Exception as e:
            print(f"🚨 Something went wrong: {e}")
            # Don't clean up on purchase failure - might be temporary
            return False

    def _adjust_quantity_with_buttons(self):
        """Adjust quantity using + and - buttons when direct input is not possible"""
        try:
            print("🔢 Looking for quantity +/- buttons...")
                
            # Find the quantity display/input field
            quantity_input = self.driver.find_element(By.CSS_SELECTOR, "input[class*='countInput']")
            
            if not quantity_input:
                print("⚠️ Could not find quantity display")
                return
            
            # Find the plus button - looking for the one with a plus sign
            quantity_buttons = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='countButton']")
            
            if not quantity_buttons:
                print("⚠️ Could not find plus buttons")
                return
                
            plus_button = None
            for button in quantity_buttons:
                button_text = button.text.strip()
                if button_text == "+" or "add" in button_text.lower() or "plus" in button_text.lower():
                    plus_button = button
                    print(f"✅ Found plus button with text: '{button_text}'")
                    break
                    
            # If text-based approach fails, try the second button (assuming first is minus, second is plus)
            if not plus_button and len(quantity_buttons) >= 2:
                plus_button = quantity_buttons[1]  # Usually the second button is plus
                print("✅ Using second count button as plus button")
            
            if not plus_button:
                print("⚠️ Could not find a button that looks like plus, will buy one")
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
                    time.sleep(0.3)
                
                print(f"➕ Set quantity to {current_quantity}")


        except Exception as e:
            print(f"⚠️ Could not adjust quantity with buttons: {e}")
            print("⚠️ Continuing with default quantity")
            
    # Try our specialized method first, fall back to the general one if it fails
    def _adjust_quantity(self):
        try:
            self._adjust_quantity_with_buttons()
        except Exception as e:
            print(f"⚠️ Specialized quantity adjustment failed: {e}")
    
    def _select_variant(self):
        if SPECIAL_TYPES:
            print("🧩 Looking for special type variants")
            variants = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'index_sizeInfoItem')]")
            if variants:
                print(f"📏 Found {len(variants)} size options")
                
                # First, collect all available (non-disabled) variants
                available_variants = []
                for idx, variant in enumerate(variants):
                    variant_class = variant.get_attribute("class")
                    if "disabled" not in variant_class:
                        available_variants.append((idx, variant))
                
                if not available_variants:
                    print("❌ No available variants found.")
                    return
                
                # Now check if our preferred item exists
                if available_variants and len(variants) >= SPECIAL_TYPE_PREFERENCE:
                    preferred_variant = variants[SPECIAL_TYPE_PREFERENCE - 1]  # Convert to 0-based index
                    preferred_class = preferred_variant.get_attribute("class")
                    
                    if "disabled" not in preferred_class:
                        print(f"✅ Found preferred variant (#{SPECIAL_TYPE_PREFERENCE})")
                        preferred_variant.click()
                        print(f"Selected preferred variant: {preferred_variant.text}")
                        return
                
                else:
                    if SPECIAL_TYPE_ANY:
                        print(f"❌ Preferred variant #{SPECIAL_TYPE_PREFERENCE} not available")
                        print("✅ Selecting first available variant instead: {available_variants[0][1].text}")
                        available_variants[0][1].click()
                    else:
                        print(f"❌ Preferred variant #{SPECIAL_TYPE_PREFERENCE} not available")
                        print("❌ Do not want any other variants")
                        return
        else:
            try:
                print("🧩 Looking for product with whole set and single box, or singular")
                
                whole_set_option = None
                single_box_option = None
                
                try:
                    # Find elements containing the text "whole set" (case insensitive)
                    whole_set_option = self.driver.find_element(By.XPATH, 
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
                    single_box_option = self.driver.find_element(By.XPATH, 
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
            "div[role='button'][class*='buy'], div[role='button'][class*='cart']"
        ]
        
        found_buy_button = None
        for selector in buy_button_selectors:
            try:
                # Use a short timeout to avoid long waits for non-existent elements
                buttons = WebDriverWait(self.driver, 3).until(
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

    def _fill_email(self):
        try:
            print("🔍 Looking for email field...")
            email_selectors = [
                "//input[contains(@class, 'emailInput')]"
            ]
            
            email_field = None
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"✅ Found email field with selector: {selector}")
                    break
                except:
                    continue
            
            if not email_field:
                raise Exception("Email field not found with any of the attempted selectors")
            
            apply_selectors = [
                "//span[contains(@class, 'applyBtn')]"
            ]

            # wait for overlay to click confirm
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[class*='loadingWrapFull']"))
            )
            
            email_field_apply = None
            for selector in apply_selectors:
                try:
                    email_field_apply = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ Found confirm button with selector: {selector}")
                    break
                except:
                    continue
            
            if not email_field_apply:
                raise Exception("Confirm button not found with any of the attempted selectors")
            
            email_field.send_keys(POPMART_USERNAME)
            # Click first apply button
            email_field_apply.click()

            print("✅ Email field filled and applied")

            confirm_selectors = [
                "//button[contains(@class, 'confirmBtn')]"
            ]
            email_field_confirm = None
            for selector in confirm_selectors:
                try:
                    email_field_confirm = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ Found confirm button with selector: {selector}")
                    break
                except:
                    continue
            
            if not email_field_confirm:
                raise Exception("Confirm button not found with any of the attempted selectors")
            
            email_field_confirm.click()
            print("✅ Email field filled and double confirmed")
            
            # Wait for any loading modal or overlay to disappear
            try:
                print("⏳ Waiting for any modals or loading overlays to disappear...")
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[class*='modal'], div[class*='overlay'], div[class*='loading']"))
                )
                print("✅ All modals and overlays are gone, proceeding")
            except Exception as e:
                print(f"⚠️ Timeout waiting for modal to disappear: {e}")
                # Continue anyway as the modal might not be present
                pass
            
        except Exception as e:
            print(f"⚠️ Error filling email: {e}")
    
    def _fill_address_book(self):
        try:
            print("🔍 Looking for address book...")
            address_book_selectors = [
                "//div[contains(@class, 'addAddressBtn')]"
            ]
            
            address_book = None
            for selector in address_book_selectors:
                try:
                    address_book = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"✅ Found address book with selector: {selector}")
                    break
                except:
                    continue
            
            if not address_book:
                raise Exception("Address book not found with any of the attempted selectors")
            
            address_book.click()
            print("✅ Address book opened")

            # Wait for the address form modal to appear
            form_modal_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='modal-content']"))
            )
            print("✅ Address form modal loaded")
            
            manual_address_selectors_xpath = [
                "//span[contains(@class, 'addOrUpdateAddress_text')]"
            ]
            enter_manually_btn = None
            for selector in manual_address_selectors_xpath:
                try:
                    enter_manually_btn = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print(f"✅ Found enter manually with selector: {selector}")
                    break
                except:
                    continue
            
            if not enter_manually_btn:
                raise Exception("Confirm button not found with any of the attempted selectors")


            print("✅ Clicking enter manually button")
            try:
                # First try the normal click
                enter_manually_btn.click()
            except Exception as e:
                print(f"⚠️ Normal click failed: {e}")
                # Try using JavaScript to click the element
                self.driver.execute_script("arguments[0].click();", enter_manually_btn)
                print("✅ Clicked using JavaScript")

            # Wait for the address form to load completely and specifically for the zipcode field
            try:
                print("⏳ Waiting for zipcode field to appear...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "postalCode"))
                )
                print("✅ Zipcode field appeared, form is ready to be filled")
            except Exception as e:
                print(f"⚠️ Timed out waiting for zipcode field: {e}")
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "postalCode"))
                    )
                    print("✅ Found zipcode field second time")
                except Exception as e:
                    print(f"⚠️ Could not find zipcode field: {e}")
                    raise Exception("Address form not fully loaded - missing zipcode field")

            # Find all input fields within the modal
            input_fields = form_modal_element.find_elements(By.CSS_SELECTOR, "input")
            textarea_fields = form_modal_element.find_elements(By.CSS_SELECTOR, "textarea")
            select_fields = form_modal_element.find_elements(By.CSS_SELECTOR, "select")

            print(f"📝 Found {len(input_fields)} input fields, {len(textarea_fields)} textarea fields, and {len(select_fields)} select fields")

            # You can iterate through the inputs to fill them
            for field in input_fields:
                field_id = field.get_attribute("id")
                print(f"Found field: {field_id}")
                if field_id == "givenName":
                    field.send_keys("Ellen")
                    print(f"✅ Filled name field: {field_id}")
                elif field_id == "familyName":
                    field.send_keys("Andersson")
                    print(f"✅ Filled family name field: {field_id}")
                elif field_id == "telNumber":
                    field.send_keys("0704257728")
                    print(f"✅ Filled phone number field: {field_id}")
                elif field_id == "detailInfo":
                    field.send_keys("Höjdvägen 3A")
                    print(f"✅ Filled address field: {field_id}")
                elif field_id == "cityName":
                    field.send_keys("Saltsjö-Boo")
                    print(f"✅ Filled city field: {field_id}")
                elif field_id == "postalCode":
                    field.send_keys("13242")
                    print(f"✅ Filled postal code field: {field_id}")
                elif field_id == "province":
                    try:
                        field.click()
                        print("🔍 Clicked province field, waiting for dropdown...")
                        try:
                            # Then find the virtual list holder which is the scrollable element
                            virtual_list_holder = WebDriverWait(self.driver, 3).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='rc-virtual-list-holder']"))
                            )

                            # Scroll through the virtual list to reveal all options
                            print("🔍 Scrolling through dropdown to find Stockholm...")
                            
                            # Scroll in increments to reveal all options in the virtualized list
                            found_stockholm = False
                            for scroll_percent in [0.2, 0.4, 0.6, 0.8, 1.0]:
                                # Scroll to different positions
                                self.driver.execute_script(
                                    f"arguments[0].scrollTop = arguments[0].scrollHeight * {scroll_percent};", 
                                    virtual_list_holder
                                )
                                print(f"Scrolled to {scroll_percent*100}% of list height")
                                time.sleep(0.3)  # Brief pause after scrolling
                                
                                # Check if Stockholm is visible after this scroll
                                try:
                                    stockholm_option = self.driver.find_element(
                                        By.XPATH, 
                                        "//div[contains(@class, 'ant-select-item') and contains(@title, 'Stockholm')]"
                                    )
                                    print("✅ Found Stockholm option!")
                                    found_stockholm = True
                                    
                                    # Make sure it's in view and click it
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", stockholm_option)
                                    time.sleep(0.2)  # Brief pause after scrolling
                                    
                                    stockholm_option.click()
                                    print("✅ Selected Stockholm option from dropdown")
                                    break
                                except Exception:
                                    print(f"Stockholm not visible at {scroll_percent*100}% scroll position, continuing...")
                            
                            if not found_stockholm:
                                raise Exception("Stockholm option not found after scrolling through the entire list")
                                
                        except Exception as e:
                            print(f"⚠️ Error handling dropdown scrolling: {e}")
                            raise  # Re-raise to try fallback methods
                            
                    except Exception as e:
                        print(f"⚠️ Error selecting/filling province: {e}")
                        try:
                            # Last resort fallback: Try using JavaScript to set the value directly
                            self.driver.execute_script(
                                "arguments[0].value = 'Stockholms län'; " +
                                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", 
                                field
                            )
                            print("✅ Set province using direct JavaScript injection (fallback)")
                        except Exception as e:
                            print(f"⚠️ All province selection methods failed: {e}")
                else:
                    print(f"⚠️ Unhandled input type: {field_id}")

            try:
                # Find the submit/save button to complete the address entry
                submit_button = form_modal_element.find_element(By.CSS_SELECTOR, "button[type='submit'], button[class*='save'], button[class*='confirm']")
                print("✅ Found address submit button")
                submit_button.click()
            except:
                print("❌ Submit button not found")
            
            
        except Exception as e:
            print(f"⚠️ Error filling address book: {e}")