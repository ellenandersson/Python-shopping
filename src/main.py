import time
from bot import ShoppingBot

def main():
    bot = ShoppingBot()
    bot.login()
    
    item_to_search = "example item"
    bot.search_item(item_to_search)
    
    time.sleep(2)  # Wait for search results to load
    bot.add_to_cart(item_to_search)
    
    time.sleep(1)  # Wait for item to be added to cart
    bot.checkout()

if __name__ == "__main__":
    main()