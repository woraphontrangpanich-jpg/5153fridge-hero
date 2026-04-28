import os
import time
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://foodsubs.com"

def get_ingredient_urls():
    """Fetch all ingredient URLs by paginating through the main groups list"""
    urls = set()
    print("Gathering ingredient URLs (this might take a minute)...")
    
    # We know there are ~115 pages based on page.size=40
    for page in range(120):
        url = f"{BASE_URL}/groups?page.number={page}&page.size=40&i=true"
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Find all ingredient links on this page
            page_urls = [a['href'] for a in soup.find_all('a', href=True) if '/ingredients/' in a['href']]
            
            # If no ingredient links found, we reached the end
            if not page_urls:
                break
                
            for href in page_urls:
                if href.startswith('/'):
                    href = BASE_URL + href
                urls.add(href)
                
            # print(f"Page {page}: found {len(urls)} total URLs...")
            time.sleep(0.1) # Respectful delay
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
            
    return list(urls)

def scrape_substitutes(url):
    """Scrape the substitutes for a specific ingredient page."""
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(resp.content, 'html.parser')
    substitutes = []
    
    # Substitutes are listed in div elements with class 'sub-details'
    sub_details_divs = soup.find_all('div', class_='sub-details')
    for div in sub_details_divs:
        # Many substitutes are wrapped in <a> tags, which isolates the exact ingredient name 
        link = div.find('a')
        if link:
            # Extracts just "Camembert" from "1 pound Camembert"
            substitutes.append(link.text.strip().lower())
        else:
            # Fallback for plain text substitutes without links
            text = div.text.strip().lower()
            if text:
                substitutes.append(text)
            
    return list(set(substitutes))  # Deduplicate

def main():
    print("Starting FoodSubs scraper...")
    urls = get_ingredient_urls()
    print(f"Found {len(urls)} ingredients to scrape.")
    
    # Create the output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    output_file = 'data/foodsubs_scraped_data.json'
    
    # NOTE: Uncomment the line below to test on just 5 ingredients first!
    # urls = urls[:5]
    
    results = {}
    
    for i, url in enumerate(urls):
        ing_name = url.split('/')[-1]
        print(f"[{i+1}/{len(urls)}] Scraping {ing_name}...")
        
        subs = scrape_substitutes(url)
        if subs:
            # Un-slugify the ingredient name (e.g. "cream-cheese" -> "cream cheese")
            clean_name = ing_name.replace('-', ' ')
            results[clean_name] = subs
            
        # Respectful delay to not overwhelm the server
        time.sleep(0.5)
        
        # Save incrementally every 20 ingredients in case the script is interrupted
        if i > 0 and i % 20 == 0:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)

    # Final save
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Scraping complete! Extracted substitutes for {len(results)} ingredients.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
