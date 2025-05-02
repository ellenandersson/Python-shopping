import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

STORE = "popmart"

BASE_URL = "https://www.popmart.com/se"
LOGIN_URL = f"{BASE_URL}/user/login"
CART_URL = f"{BASE_URL}/largeShoppingCart"
CHECKOUT_URL = f"{BASE_URL}/checkout"
# Allow for product URL to be changed without modifying code
PRODUCT_URL = os.getenv("PRODUCT_URL", f"{BASE_URL}/products/1443/BAZBON-Label-Plan-Series-1%2F8-Action-Figure")

POPMART_USERNAME = os.getenv("POPMART_USERNAME", "fake")
POPMART_PASSWORD = os.getenv("POPMART_USERNAME", "fake")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

BUY_NOW = 'BUY NOW'
ADD_TO_CART = 'ADD TO CART'

BUY_BUTTON_SELECTOR = "div[class*='red'][class*='btn'], div[class*='red'][class*='Btn']"

# Purchase preferences
PREFERRED_QUANTITY = 1 # Can be env vars
PREFER_WHOLE_SET = True # Can be env vars

CHECK_INTERVAL_MIN = 30
CHECK_INTERVAL_MAX = 60