import requests

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

    def search_item(self, item_name):
        search_url = self.config['SEARCH_URL']
        response = self.session.get(search_url, params={'q': item_name})
        return response.json()  # Assuming the response is in JSON format

    def add_to_cart(self, item_id):
        cart_url = self.config['CART_URL']
        response = self.session.post(cart_url, json={'item_id': item_id})
        return response.ok

    def checkout(self):
        checkout_url = self.config['CHECKOUT_URL']
        response = self.session.post(checkout_url)
        return response.ok