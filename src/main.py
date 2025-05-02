from bot import ShoppingBot

import time
import random

def main(self):
    interval_min = self.config['CHECK_INTERVAL_MIN']
    interval_max = self.config['CHECK_INTERVAL_MAX']

    bot = ShoppingBot()
    bot.login()

    while True:
        if bot.check_product():
            if bot.buy_product():
                print("✅ Product purchased successfully!")
                break
        sleep_time = random.randint(interval_min, interval_max)
        print(f"⏳ Wait {sleep_time} seconds until next check.")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
