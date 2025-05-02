BASE_URL = "https://example.com"
LOGIN_URL = f"{BASE_URL}/login"
SEARCH_URL = f"{BASE_URL}/search"
CART_URL = f"{BASE_URL}/cart"
CHECKOUT_URL = f"{BASE_URL}/checkout"
PRODUCT_URL = f"{BASE_URL}/product"

USERNAME = "your_username"
PASSWORD = "your_password"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

IN_STOCK_TEXT = 'i lager'
BUY_BUTTON_SELECTOR = ".buy-button"

CHECK_INTERVAL_MIN = 30
CHECK_INTERVAL_MAX = 60