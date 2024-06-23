import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from datetime import datetime
import urllib.parse

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    # Add more User-Agent strings as needed
]

def get_html(url):
    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }
    retries = 5
    for i in range(retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code in [503, 500, 429]:
            # Backoff strategy
            print(f"Server returned {response.status_code}. Retrying in {2**i} seconds...")
            time.sleep(2**i)
        else:
            break
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    return ""

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    product_containers = soup.find_all('div', {'data-component-type': 's-search-result'})

    extracted_data = {
        "Title": [],
        "Price": [],
        "Rating": []
    }

    for container in product_containers:
        title = container.find('span', class_='a-size-medium a-color-base a-text-normal')
        extracted_data["Title"].append(title.get_text(strip=True) if title else "N/A")

        price_whole = container.find('span', class_='a-price-whole')
        price_fraction = container.find('span', class_='a-price-fraction')
        if price_whole and price_fraction:
            price = f"{price_whole.get_text(strip=True)}.{price_fraction.get_text(strip=True)}"
        elif price_whole:
            price = price_whole.get_text(strip=True)
        else:
            price = "N/A"
        extracted_data["Price"].append(price)

        rating = container.find('span', class_='a-icon-alt')
        extracted_data["Rating"].append(rating.get_text(strip=True) if rating else "N/A")

    return extracted_data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def extract_product_name_from_url(url):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    if 'k' in query_params:
        return query_params['k'][0]
    else:
        return 'product'

def main():
    url = input("Enter the Amazon search URL: ").strip()
    product_name = extract_product_name_from_url(url)

    html = get_html(url)
    if html:
        extracted_data = parse_html(html)
        if extracted_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{product_name}_{timestamp}.csv"
            save_to_csv(extracted_data, output_filename)
            print(f"Scraped data and saved to '{output_filename}'")
        else:
            print("Failed to extract data or no data found.")
    else:
        print("Failed to retrieve the webpage content.")

if __name__ == '__main__':
    main()
