def send_request(url, method='GET', data=None, headers=None):
    import requests

    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    else:
        raise ValueError("Unsupported HTTP method: {}".format(method))

    response.raise_for_status()
    return response


def parse_response(response):
    from bs4 import BeautifulSoup

    # Check if response is already a string or a response object
    if hasattr(response, 'text'):
        html_content = response.text
    else:
        html_content = response  # Assume it's already a string

    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def accept_cookies(driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        print("🍪 Looking for cookie/policy consent banners...")
        banner_selectors = [
            "//div[contains(@class, 'policy_aboveFixedContainer')]"
        ]
        
        # Common button texts for accept buttons
        accept_texts = ['accept', 'acceptera', 'ok', 'got it', 'agree', 'close', 'accept all']
        
        # Use a more resilient approach for each banner selector
        for selector in banner_selectors:
            try:
                # Use explicit wait to find banners
                banners = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                
                if banners:
                    print(f"Found potential banner with selector: {selector}")
                    
                    try:
                        accept_button = driver.find_element(By.XPATH, "//div[contains(@class, 'policy_acceptBtn')]")
                        if accept_button:
                            driver.execute_script("arguments[0].click();", accept_button)
                            print("✅ Clicked accept button with policy_acceptBtn class")
                            return
                        else:
                            print("❌ Accept button not found with policy_acceptBtn class")
                            Exception("Accept button not found")
                    except Exception:
                        for text in accept_texts:
                            try:
                                xpath = f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]"
                                xpath_div = f"//*[contains(@class, 'button') or contains(@class, 'btn')][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]"
                                
                                buttons = WebDriverWait(driver, 1).until(
                                    EC.presence_of_all_elements_located((By.XPATH, f"{xpath} | {xpath_div}"))
                                )
                                if buttons:
                                    driver.execute_script("arguments[0].click();", buttons[0])
                                    print(f"✅ Clicked accept button with text: {text}")
                                    break
                            except Exception:
                                continue
                                
                        # 3. If no text buttons worked, try any buttons within the banner
                        try:
                            for banner in banners:
                                buttons = driver.execute_script(
                                    "return arguments[0].querySelectorAll('button, .button, [role=\"button\"], [class*=\"accept\"], [class*=\"btn\"]');", 
                                    banner
                                )
                                if buttons:
                                    driver.execute_script("arguments[0].click();", buttons[0])
                                    print("✅ Clicked first button in banner")
                                    break
                        except Exception:
                            pass
                    
                    # 4. As a last resort, try to hide the banner with JavaScript
                    try:
                        driver.execute_script(
                            f"document.querySelectorAll('{selector}').forEach(el => el.style.display = 'none');"
                        )
                        print(f"✅ Tried to hide banner with selector: {selector}")
                    except Exception:
                        pass
            except Exception:
                continue
    except Exception as e:
        print(f"⚠️ Error handling cookie banners: {e}")
