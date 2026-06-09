import time
import json
import re
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # CORS middleware

# Initialize FastAPI application
app = FastAPI(title="E-Commerce AI Platform API")

# --- CONFIGURE CORS MIDDLEWARE ---
# This allows your React frontend on port 5173 to securely request resources from FastAPI on port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direct imports from local modules
from scraper.search_scraper import search_products
from scraper.review_scraper import scrape_reviews

from nlp.sentiment import analyze_sentiment
from nlp.fake_detector import detect_fake_reviews
from nlp.summarizer import summarize_reviews

from cv.image_quality import analyze_image_quality
from timeseries.price_forecast import forecast_product_price
from recsys.recommender import get_recommendations

# Request Model
class AnalysisRequest(BaseModel):
    product_url: str
    products_list: Optional[List[dict]] = None

# --- BULLETPROOF SCRAPER HELPER ---
def scrape_description_and_details(product_url: str) -> dict:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=options)
    details = {"name": "Flipkart Product", "price": "N/A", "image_url": None, "description": ""}
    
    try:
        driver.get(product_url)
        time.sleep(3)
        
        # 1. Product Name extraction
        try:
            name_elem = driver.find_element(By.CSS_SELECTOR, "span.VU-Z7G, span.B_NuCI, h1")
            details["name"] = name_elem.text
        except:
            pass

        # 2. Product Price
        price_found = False
        price_selectors = [
            "div.Nx9bqj.CxhGGd", "div._30jeq3._16Jk6d", "div.Nx9bqj", "div._30jeq3", "span.Nx9bqj", "div.CxhGGd"
        ]
        
        for selector in price_selectors:
            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, selector)
                text = price_elem.text
                if text and "₹" in text:
                    details["price"] = text.strip()
                    price_found = True
                    break
            except:
                continue
                
        # Regex Fallback
        if not price_found or details["price"] == "N/A":
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                price_matches = re.findall(r'₹[0-9,]+', body_text)
                if price_matches:
                    valid_prices = []
                    for m in price_matches:
                        val = int(m.replace('₹', '').replace(',', '').strip())
                        if val > 150:
                            valid_prices.append(m)
                    if valid_prices:
                        details["price"] = valid_prices[0]
                        price_found = True
                        print(f"[SUCCESS] Regex Scanner successfully extracted price: {valid_prices[0]}")
            except Exception as regex_err:
                print(f"[WARNING] Price Regex Scanner failed: {regex_err}")
            
        # 3. Image URL extraction
        try:
            img_elem = driver.find_element(By.CSS_SELECTOR, "img.DByo7b, img._396cs4, div._3exPp9 img, img[src*='rukminim']")
            details["image_url"] = img_elem.get_attribute("src")
        except:
            pass
            
        # 4. Specifications Extraction
        for scroll in [800, 1600, 2400]:
            driver.execute_script(f"window.scrollTo(0, {scroll});")
            time.sleep(0.8)
            
        try:
            expand_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'View all') or contains(text(), 'All details') or contains(text(), 'Read More') or contains(text(), 'Specifications')]")
            for btn in expand_buttons:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1.0)
                except:
                    continue
        except:
            pass

        spec_text = ""
        spec_selectors = [
            "div._3k-BhJ", "div._14_KAd", "table", "div.x8YvA2"
        ]
        
        for selector in spec_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                if elem.text and len(elem.text.strip()) > 30:
                    spec_text = elem.text
                    break
            except:
                continue
                
        specs_summary = ""
        if spec_text:
            lines = [line.strip() for line in spec_text.split('\n') if line.strip()]
            formatted_specs = []
            headers = [
                "in the box", "general", "dimensions", "important note", 
                "specifications", "manufacturer info", "warranty", "product details", "all details"
            ]
            
            i = 0
            while i < len(lines) - 1:
                key = lines[i]
                val = lines[i+1]
                if key.lower() in headers or val.lower() in headers:
                    i += 1
                    continue
                if len(key) < 30 and len(val) < 100:
                    formatted_specs.append(f"{key}: {val}")
                    i += 2
                else:
                    formatted_specs.append(key)
                    i += 1
            specs_summary = ". ".join(formatted_specs)

        # Fallback to JSON-LD SEO Schema
        description_text = ""
        if not specs_summary:
            try:
                scripts = driver.find_elements(By.CSS_SELECTOR, "script[type='application/ld+json']")
                for script in scripts:
                    try:
                        schema_data = json.loads(script.get_attribute("innerHTML"))
                        if isinstance(schema_data, list):
                            schema_data = schema_data[0]
                        if "description" in schema_data:
                            desc = schema_data["description"]
                            if desc and not desc.startswith("Buy ") and "best prices" not in desc:
                                description_text = desc
                                break
                    except:
                        continue
            except:
                pass

        final_desc = specs_summary if specs_summary else description_text
        if final_desc:
            details["description"] = final_desc.strip()
        else:
            details["description"] = "N/A"
            
    except Exception as e:
        print(f"[ERROR] Error in product details scraping: {e}")
    finally:
        driver.quit()
        
    return details

# --- API ROUTES ---

@app.get("/")
def read_root():
    return {"message": "Welcome to E-Commerce AI Platform API!"}

@app.get("/api/test")
def test_api():
    return {
        "status": "success",
        "message": "FastAPI backend connected successfully!"
    }

@app.get("/api/search")
def search(q: str = Query(..., description="Product name to search")):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
    try:
        results = search_products(q)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/analyze")
def analyze_product(req: AnalysisRequest):
    url = req.product_url
    if not url.strip() or "/p/" not in url:
        raise HTTPException(status_code=400, detail="Invalid Flipkart Product URL. Must contain '/p/'.")

    try:
        details = scrape_description_and_details(url)
        current_product = {
            "name": details["name"],
            "price": details["price"],
            "image": details["image_url"],
            "url": url
        }

        cv_results = {}
        if details["image_url"]:
            text_to_match = details["description"] if details["description"] != "N/A" else details["name"]
            cv_results = analyze_image_quality(details["image_url"], text_to_match)

        df_history, df_forecast, indicators = forecast_product_price(details["price"])
        history_list = df_history.to_dict(orient="records")
        forecast_list = df_forecast.to_dict(orient="records")

        reviews = scrape_reviews(url)
        
        sentiment_results = {}
        fake_results = {}
        summary_results = {}
        if reviews:
            sentiment_results = analyze_sentiment(reviews)
            fake_results = detect_fake_reviews(reviews)
            summary_results = summarize_reviews(reviews)

        recommendations = []
        if req.products_list:
            recommendations = get_recommendations(current_product, req.products_list)

        return {
            "status": "success",
            "product_details": current_product,
            "description": details["description"],
            "cv_analysis": cv_results,
            "timeseries_analysis": {
                "indicators": indicators,
                "history": history_list,
                "forecast": forecast_list
            },
            "nlp_analysis": {
                "overall_sentiment": sentiment_results,
                "fake_analysis": fake_results,
                "ai_summary": summary_results.get("summary", ""),
                "top_themes": summary_results.get("keywords", [])
            },
            "recommendations": recommendations,
            "raw_reviews_count": len(reviews)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline crashed: {str(e)}")