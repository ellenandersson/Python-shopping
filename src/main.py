from bot import ShoppingBot
from config import *

import time
import random

def main():
    shoppingBot = ShoppingBot(STORE)
    
    try:
        if shoppingBot.login():
            while True:
                if shoppingBot.check_product():
                    if shoppingBot.buy_product():
                        print("✅ Product purchased successfully!")
                        break
                sleep_time = random.randint(CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX)
                print(f"⏳ Wait {sleep_time} seconds until next check.")
                time.sleep(sleep_time)
        else:
            print("❌ Login failed. Please check your credentials.")
            return
    finally:
        # Make sure to clean up browser resources even if we exit with an error
        if shoppingBot and shoppingBot.bot:
            shoppingBot.bot.cleanup()
            print("🧹 Browser session cleaned up")

if __name__ == "__main__":
    main()
