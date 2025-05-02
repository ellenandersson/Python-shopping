import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def analyze_network_requests(product_url, duration=30):
    """
    Analyze network requests to find potential API endpoints for product availability.
    
    Args:
        product_url: URL of the product page to analyze
        duration: How long to monitor network traffic (in seconds)
    
    Returns:
        List of potential API endpoints that might contain availability info
    """
    print(f"🔍 Analyzing network requests for {duration} seconds...")
    print(f"📝 Please interact with the product page during this time")
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    
    # Storage for requests
    captured_requests = []
    
    try:
        # Set up performance logging
        driver.execute_cdp_cmd("Network.enable", {})
        
        # Set up event listener using a different approach
        def capture_request(driver):
            # Get all network events
            logs = driver.get_log("performance")
            for log in logs:
                network_log = json.loads(log["message"])["message"]
                
                # Filter for network requests
                if "Network.requestWillBeSent" in network_log["method"]:
                    request_data = network_log["params"]
                    url = request_data.get("request", {}).get("url", "")
                    method = request_data.get("request", {}).get("method", "")
                    
                    # Skip image, font, css, etc. resources
                    if any(ext in url.lower() for ext in ['.jpg', '.png', '.css', '.js', '.svg', '.woff']):
                        continue
                    
                    captured_requests.append({
                        "url": url,
                        "method": method
                    })
        
        # Navigate to the product page
        driver.get(product_url)
        print(f"✅ Opened {product_url}")
        print(f"⏳ Monitoring network traffic for {duration} seconds...")
        
        # Enable performance logging
        driver.execute_cdp_cmd("Network.enable", {})
        
        # Start time
        start_time = time.time()
        
        # Collect requests for the specified duration
        while time.time() - start_time < duration:
            try:
                capture_request(driver)
            except:
                pass
            time.sleep(1)
        
        # Filter and analyze the collected requests
        api_endpoints = []
        keywords = ['product', 'stock', 'inventory', 'availability', 'sku', 'cart', 'api', 'json', 'graphql']
        
        # Deduplicate requests
        unique_urls = set()
        for req in captured_requests:
            url = req['url'].lower()
            if url not in unique_urls:
                unique_urls.add(url)
                
                # Look for URLs that might be API endpoints
                if ('/api/' in url or '/graphql' in url or 
                    any(keyword in url for keyword in keywords)):
                    api_endpoints.append(req)
        
        # Print findings
        print(f"\n🔍 Found {len(api_endpoints)} potential API endpoints:")
        for i, endpoint in enumerate(api_endpoints):
            print(f"{i+1}. {endpoint['method']} {endpoint['url']}")
        
        return api_endpoints
    
    finally:
        driver.quit()

if __name__ == "__main__":
    from config import PRODUCT_URL
    endpoints = analyze_network_requests(PRODUCT_URL)
    
    # Save findings to a file for later analysis
    # Get current file directory and save results there
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'potential_api_endpoints.json')
    
    with open(output_path, 'w') as f:
        json.dump(endpoints, f, indent=2)
        
    print(f"\n✅ Analysis complete! Results saved to {output_path}")
    