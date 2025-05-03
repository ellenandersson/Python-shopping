from config import *
from popmart import PopMartBot

import requests

class ShoppingBot:
    def __init__(self, store):
        self.session = requests.Session()
        self.store = store
        self.bot = self._get_bot()
        
    def _get_bot(self):
        if self.store == "popmart":
            return PopMartBot()
        else:
            raise ValueError(f"Unsupported store: {self.store}")
    
    def start(self):
        if self.bot:
            self.bot.start()
        else:
            raise ValueError("No bot instance available. Please check the store name.")
    
    def check_product(self):
        if self.bot:
            return self.bot.check_product()
        else:
            raise ValueError("No bot instance available. Please check the store name.")
            
    def buy_product(self):
        if self.bot:
            return self.bot.buy_product()
        else:
            raise ValueError("No bot instance available. Please check the store name.")
