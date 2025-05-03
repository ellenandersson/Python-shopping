import os
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ON_RELEASE = True
# Convert string date to datetime object
RELEASE_DATE_STR = "2025-05-03"
# Parse the date string into a datetime object
RELEASE_DATE = datetime.datetime.strptime(RELEASE_DATE_STR, "%Y-%m-%d").date()
RELEASE_HOUR = "12"
RELEASE_MINUTE = "03"

STORE = "popmart"

BASE_URL = "https://www.popmart.com/se"
LOGIN_URL = f"{BASE_URL}/user/login"
CART_URL = f"{BASE_URL}/largeShoppingCart"
CHECKOUT_URL = f"{BASE_URL}/checkout"
# Allow for product URL to be changed without modifying code
PRODUCT_URL = os.getenv("PRODUCT_URL", f"{BASE_URL}/products/169/Modoli-Mood-%26-Weather-Series")

POPMART_USERNAME = os.getenv("POPMART_USERNAME", "fake")
POPMART_PASSWORD = os.getenv("POPMART_PASSWORD", "fake")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

BUY_NOW = 'BUY NOW'
ADD_TO_CART = 'ADD TO CART'

BUY_BUTTON_SELECTOR = "div[class*='red'][class*='btn'], div[class*='red'][class*='Btn']"

# Purchase preferences
PREFERRED_QUANTITY = 3 # Can be env vars
PREFER_WHOLE_SET = True # Can be env vars

CHECK_INTERVAL_MIN = 30
CHECK_INTERVAL_MAX = 60

SPECIAL_TYPES = False
SPECIAL_TYPE_PREFERENCE = 1
SPECIAL_TYPE_ANY = True