from matplotlib import lines
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_product(product_url: str) -> dict:
    driver = get_driver()
    product = {}

    try:
        driver.get(product_url)
        time.sleep(4)

        
        try:
            close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
            close_btn.click()
            time.sleep(1)
        except:
            pass

        body_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [line.strip() for line in body_text.split('\n') if line.strip()]

        # Extract prices
        prices = []
        for line in lines:
            clean = line.replace(',', '').replace('₹', '').strip()
            if clean.isdigit() and len(clean) >= 4:
                prices.append(int(clean))

        # Rating — X.X format(Use of regrex: r'^\d\.\d$')
        rating = None
        for line in lines:
            if re.match(r'^\d\.\d$', line.strip()):
                rating = float(line.strip())
                break

        # Review count— | 25,353 format
        review_count = None
        for line in lines:
            if line.startswith('|') and any(c.isdigit() for c in line):
                review_count = line.replace('|', '').replace(',', '').strip()
                break

        
        name = None
        for i, line in enumerate(lines):
            if re.match(r'^\d\.\d$', line.strip()):
                if i > 0:
                    name = lines[i - 1]
                    break

        
        prices_sorted = sorted(set(prices))
        current_price = None
        original_price = None

        for line in lines:
            if line.startswith('₹') and ',' in line:
                clean = line.replace('₹', '').replace(',', '').strip()
                if clean.isdigit():
                    current_price = int(clean)
                    break

        for line in lines:
            clean = line.replace(',', '').strip()
            if clean.isdigit() and len(clean) == 5:
                val = int(clean)
                if current_price and val > current_price:
                    original_price = val
                    break

        product = {
            "name": name,
            "rating": rating,
            "review_count": review_count,
            "current_price": current_price,
            "original_price": original_price,
            "url": product_url
        }

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

    return product


if __name__ == "__main__":
    url = "https://www.flipkart.com/fire-boltt-axiom-1-43-amoled-display-smartwatch-bt-calling-wireless-charging-metal-case/p/itmcf8978cc82573?pid=SMWHFNF6GCZJHEHR&lid=LSTSMWHFNF6GCZJHEHR9TKYDY&marketplace=FLIPKART&store=ajy%2Fbuh&srno=b_1_1&otracker=browse&fm=organic&iid=7b1f2a84-affa-45cd-87e9-5de606c8b02a.SMWHFNF6GCZJHEHR.SEARCH&ppt=hp&ppn=homepage&ssid=muri90fu9s0000001780543194978&ov_redirect=true"

    
    product = scrape_product(url)

    print(f"\nName:           {product['name']}")
    print(f"Rating:         {product['rating']}")
    print(f"Review Count:   {product['review_count']}")
    print(f"Current Price:  ₹{product['current_price']}")
    print(f"Original Price: ₹{product['original_price']}")



    """
    1. Imported models webdriver, By, Options, time, re
    2. get_driver() function 
    3. main function scrape_product() 
          -driver.get(product_url)
          -close login popup
          -extract body text and split into lines (driver.find_element(By.TAG_NAME, "body").text
          lines=[for line in body_text.split('\n) if line.strip()])
          -make price list for original and current price
          for line in lines:
            if line.startswith('₹') and ',' in line:
                clean = line.replace('₹', '').replace(',', '').strip()
                if clean.isdigit():
                    current_price = int(clean)
                    break
                    
              -Rating - X.X format(if re.match('', line.strip()))
            -Review count - | 25,353 format (if line.startswith('|') and any(c.isdigit() for c in line))

    """