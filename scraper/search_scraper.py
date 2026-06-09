from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def get_driver():
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def search_products(query: str) -> list:
  
    driver = get_driver()
    products = []

    try:
        url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(url)
        time.sleep(3)

        # Close the login popup 
        try:
            driver.find_element(By.XPATH, "//button[contains(text(),'✕')]").click()
        except:
            pass

        # Primary method - standard product containers
        items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
        
        # Secondary method-fallback to product containers
        # in flipkart they are of two types-grid and list 
        if len(items) == 0:
            items = driver.find_elements(By.CSS_SELECTOR, "div._1AtVbE")

        print(f"Search Scraper found {len(items)} containers.")


        #now once we get the containers we will extract top 10 products 

        for item in items[:10]:  
            try:
               
                link = None
                try:
                    tag_name = item.tag_name
                    href_val = item.get_attribute("href")
                    if tag_name == "a" and href_val and "/p/" in href_val:
                        link = href_val
                    else:
                        link_elem = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                        link = link_elem.get_attribute("href")
                except:
                    try:
                        link_elem = item.find_element(By.TAG_NAME, "a")
                        link = link_elem.get_attribute("href")
                    except:
                        continue

                
                if not link or "/p/" not in link:
                    continue

                #Product Name 
                name = None
                
                # Use alt text of image as fallback for product name 
                try:
                    img_elem = item.find_element(By.TAG_NAME, "img")
                    alt_text = img_elem.get_attribute("alt")
                    if alt_text and len(alt_text.strip()) > 5:
                        name = alt_text.strip()
                except:
                    pass

                # Multi-selector approach for product name
                if not name:
                    name_selectors = [
                        ".RG5Slk", ".KzDlHZ", ".wubgfb", ".WKTcLC", "a.IRpwTa", "div._4rR01T"
                    ]
                    for sel in name_selectors:
                        try:
                            name_elem = item.find_element(By.CSS_SELECTOR, sel)
                            if name_elem.text:
                                name = name_elem.text
                                break
                        except:
                            continue

                # Get from link title 
                if not name:
                    try:
                        link_elem = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                        title_val = link_elem.get_attribute("title")
                        if title_val:
                            name = title_val
                    except:
                        pass

                
                if not name:
                    name = "Flipkart Product"

                # Product Price
                price = "N/A"
                price_selectors = [
                    ".hZ3P6w", 
                    ".Nx9bqj", 
                    "._30jeq3", 
                    "div._30jeq3", 
                    "div._25b18c",
                    "div.Nx9bqj"
                ]
                for sel in price_selectors:
                    try:
                        price_elem = item.find_element(By.CSS_SELECTOR, sel)
                        if price_elem.text and "₹" in price_elem.text:
                            price = price_elem.text
                            break
                    except:
                        continue

                # Image URL
                image = None
                try:
                    img_elem = item.find_element(By.TAG_NAME, "img")
                    image = img_elem.get_attribute("src")
                except:
                    pass

                if link:
                    products.append({
                        "name": name,
                        "price": price,
                        "image": image,
                        "url": link
                    })
            except:
                continue

    except Exception as e:
        print(f"Error in Search Scraper: {e}")
    finally:
        driver.quit()

    return products
