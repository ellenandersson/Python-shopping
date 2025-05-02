from config import *
from popmart import PopMartBot

import requests

class ShoppingBot:
    def __init__(self):
        self.session = requests.Session()

    def login(self, store):
        match store:
            case "popmart":
                popMartBot = PopMartBot()
                popMartBot.login()
                return True
            case _:
                print("Invalid store selected. Please choose a valid store.")
                return False
    
    def check_product(self, store):
        match store:
            case "popmart":
                popMartBot = PopMartBot()
                return popMartBot.check_product()
            case _:
                print("Invalid store selected. Please choose a valid store.")
                return False
            
    def buy_product(self, store):
        match store:
            case "popmart":
                popMartBot = PopMartBot()
                return popMartBot.buy_product()
            case _:
                print("Invalid store selected. Please choose a valid store.")
                return False