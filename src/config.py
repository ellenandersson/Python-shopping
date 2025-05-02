BASE_URL = "https://www.popmart.com/se"
LOGIN_URL = f"{BASE_URL}/user/login"
CART_URL = f"{BASE_URL}/largeShoppingCart"
CHECKOUT_URL = f"{BASE_URL}/checkout"
PRODUCT_URL = f"{BASE_URL}/products/1443/BAZBON-Label-Plan-Series-1%2F8-Action-Figure"

USERNAME = "your_username"
PASSWORD = "your_password"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

IN_STOCK_TEXT = 'i lager'
BUY_BUTTON_SELECTOR = ".buy-button"

CHECK_INTERVAL_MIN = 30
CHECK_INTERVAL_MAX = 60