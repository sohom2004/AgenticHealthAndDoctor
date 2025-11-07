from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import urllib.parse
import re


def scrape_google_maps(doc_type, location):
    """
    Scrape medical professional data from Google Maps
    
    Args:
        doc_type (str): Type of medical professional (e.g., "cardiologist", "dentist", "hospital")
        location (str): Location to search (e.g., "kolkata", "mumbai", "delhi")
    
    Returns:
        list: List of dictionaries containing:
            - name: Name of doctor/hospital/clinic
            - address: Address
            - phone: Contact number
            - rating: Star rating
            - reviews: Number of reviews
    
    Example:
        >>> from google_maps_scraper import scrape_google_maps
        >>> results = scrape_google_maps("cardiologist", "kolkata")
        >>> print(f"Found {len(results)} cardiologists")
        >>> print(results[0]['name'])
    """
    
    driver = None
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        query = f"{doc_type} in {location}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/maps/search/{encoded_query}/"
        
        driver.get(url)
        time.sleep(5)
        
        try:
            time.sleep(3)
            scrollable = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
            
            for i in range(5):
                driver.execute_script(
                    'arguments[0].scrollTo(0, arguments[0].scrollHeight);',
                    scrollable
                )
                time.sleep(2)
        except:
            for i in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
        
        results = []
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/maps/place/"]'))
        )
        
        listings = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
        
        for listing in listings:
            try:
                data = {
                    'name': 'N/A',
                    'address': 'N/A',
                    'phone': 'N/A',
                    'rating': 'N/A',
                    'reviews': 'N/A'
                }
                
                parent = listing.find_element(By.XPATH, './ancestor::div[contains(@class, "Nv2PK")]')
                
                aria_label = listing.get_attribute('aria-label')
                if aria_label:
                    data['name'] = aria_label.strip()
                
                try:
                    rating_elem = parent.find_element(By.CSS_SELECTOR, 'span[role="img"]')
                    rating_text = rating_elem.get_attribute('aria-label')
                    if rating_text and 'star' in rating_text.lower():
                        parts = rating_text.split()
                        if len(parts) > 0:
                            data['rating'] = parts[0]
                except:
                    pass
                
                try:
                    all_text = parent.text
                    pattern = r'\d+\.?\d*\s*\((\d+(?:,\d+)*)\)'
                    matches = re.findall(pattern, all_text)
                    if matches:
                        data['reviews'] = matches[0].replace(',', '')
                    else:
                        pattern2 = r'\((\d+(?:,\d+)*)\)'
                        matches2 = re.findall(pattern2, all_text)
                        if matches2:
                            for match in matches2:
                                num = int(match.replace(',', ''))
                                if num >= 1:
                                    data['reviews'] = str(num)
                                    break
                except:
                    pass
                
                try:
                    text_elements = parent.find_elements(By.TAG_NAME, 'div')
                    for elem in text_elements:
                        text = elem.text.strip()
                        if not text:
                            continue
                        
                        if any(char.isdigit() for char in text) and ('+' in text or len([c for c in text if c.isdigit()]) >= 8):
                            if '⋅' not in text and 'km' not in text:
                                data['phone'] = text
                        
                        elif len(text) > 15 and text != data['name']:
                            if '⋅' not in text and '₹' not in text and not text.replace('.', '').isdigit():
                                if data['address'] == 'N/A':
                                    data['address'] = text
                except:
                    pass
                
                if data['name'] != 'N/A':
                    results.append(data)
                    
            except:
                continue
        
        return results
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
        
    finally:
        if driver:
            driver.quit()

def perform_ranking(results):
    """
    Compute a normalized score (0-1) for each doctor based on rating and review count.

    Scoring formula:
        raw_score = (normalized_rating * 0.6) + (normalized_reviews * 0.4)
    
    Normalization is done using min-max scaling for both rating and reviews.

    Args:
        results (list[dict]): List of doctor entries containing "rating" and "reviews".

    Returns:
        list[dict]: Same list with an additional "score" field scaled between 0 and 1.
    """
    if not results:
        return []

    for r in results:
        try:
            r["rating"] = float(r.get("rating", 0))
        except:
            r["rating"] = 0.0
        try:
            r["reviews"] = int(r.get("reviews", 0))
        except:
            r["reviews"] = 0

    ratings = [r["rating"] for r in results]
    reviews = [r["reviews"] for r in results]

    def normalize(values):
        min_v, max_v = min(values), max(values)
        if max_v == min_v:
            return [0.5 for _ in values]
        return [(v - min_v) / (max_v - min_v) for v in values]

    norm_ratings = normalize(ratings)
    norm_reviews = normalize(reviews)

    rating_weight = 0.6
    review_weight = 0.4

    for r, nr, nrev in zip(results, norm_ratings, norm_reviews):
        r["score"] = round((nr * rating_weight) + (nrev * review_weight), 4)

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:6]
    return results