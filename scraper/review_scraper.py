from requests import options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service


def get_driver():
   options = Options()
   options.add_argument("--headless")
   options.add_argument("--no-sandbox")
   options.add_argument("--disable-dev-shm-usage")
   options.add_argument("--disable-gpu")
   options.add_argument("--window-size=1920,1080")
   options.binary_location = "/usr/bin/chromium"  # HF Spaces path

   service = Service("/usr/bin/chromedriver")  # HF Spaces path
   driver = webdriver.Chrome(service=service, options=options)
   return driver

def scrape_reviews(product_url: str) -> list:
    driver = get_driver()
    reviews = []

    reviews_url = product_url.replace("/p/", "/product-reviews/")
    if "pid=" in reviews_url:
        base = reviews_url.split("?")[0]
        pid = reviews_url.split("pid=")[1].split("&")[0]
        reviews_url = f"{base}?pid={pid}&marketplace=FLIPKART"

    print(f"Reviews URL: {reviews_url}\n")

    try:
        driver.get(reviews_url)
        time.sleep(3)

        # Login popup close 
        try:
            close_btn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
            close_btn.click()
            time.sleep(1)
        except:
            pass

        
        scroll_steps = 4
        scroll_pause_time = 1.0

        for i in range(scroll_steps):
          
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(scroll_pause_time)

        
        time.sleep(1)

       
        all_text = driver.find_element(By.TAG_NAME, "body").text
        lines = all_text.split('\n')

        skip_keywords = [
            "Review for:", "READ MORE", "Helpful", "Report Abuse",
            "Certified Buyer", "verified", "ago", "stars", "Star",
            "Ratings", "Filter", "Sort", "NEXT", "PREV", "of 5"
        ]

        for line in lines:
            line = line.strip()
            
            if (len(line) > 50 and
                not any(kw.lower() in line.lower() for kw in skip_keywords) and
                not line.startswith("Color") and
                not line.startswith("Variant")):
                reviews.append(line)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

    return reviews

if __name__ == "__main__":
    import sys
    import os
    
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from nlp.sentiment import analyze_sentiment

    url = "https://www.flipkart.com/panasonic-2026-model-1-5-ton-3-star-split-inverter-wi-fi-smart-dustbuster-tech-matter-enabled-ai-higher-airflow-2-way-swing-cools-55-deg-c-copper-condenser-8in1-convertible-pm0-1-filter-ac/p/itmc394322d7a27f?pid=ACNHJZN5MZNMBWZS"

    reviews = scrape_reviews(url)
    print(f"\nTotal Reviews: {len(reviews)}")