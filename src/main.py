from bot import ShoppingBot
from config import *

import time
import random

def main():
    shoppingBot = ShoppingBot(STORE)
    
    try:
        if ON_RELEASE:
            print(f"🕒 Waiting for release at {RELEASE_DATE} {RELEASE_HOUR}:{RELEASE_MINUTE}")
            
            release_datetime = time.mktime(time.strptime(f"{RELEASE_DATE.year}-{RELEASE_DATE.month}-{RELEASE_DATE.day} {RELEASE_HOUR}:{RELEASE_MINUTE}:00", "%Y-%m-%d %H:%M:%S"))
            current_datetime = time.time()
            
            # If release time is in the past, start immediately
            if current_datetime >= release_datetime:
                print("🚀 Starting bot (release time has already passed)")
            else:
                while True:
                    current_datetime = time.time()
                    # Start bot if within 5 minutes of release time
                    time_until_release = release_datetime - current_datetime
                    if time_until_release <= 300:  # 5 minutes in seconds
                        print(f"🚀 Starting bot (within 5 minutes of release time)")
                        break
                    
                    current_second = time.localtime().tm_sec
                    sleep_seconds = 60 - current_second
                    print(f"🕒 Waiting {sleep_seconds} seconds until the next minute... ({int(time_until_release/60)} minutes until release)")
                    time.sleep(sleep_seconds)

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
