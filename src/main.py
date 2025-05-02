from bot import ShoppingBot
from config import *

import time
import random

def main():
    # Create bot without config (it now imports directly from config.py)
    bot = ShoppingBot()
    
    # Login with credentials from config
    bot.login()

    while True:
        if bot.check_product():
            if bot.buy_product():
                print("✅ Product purchased successfully!")
                break
        sleep_time = random.randint(CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX)
        print(f"⏳ Wait {sleep_time} seconds until next check.")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
