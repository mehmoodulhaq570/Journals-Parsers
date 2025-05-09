#====================MDPI====================
# This works with MDPI using selenium for 403 error

import random
import time
import requests
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# List of User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com"
    }

def setup_selenium():
    options = Options()
    options.add_argument('--headless')  # Run without GUI
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')

    driver = webdriver.Chrome(options=options)
    return driver

def fetch_mdpi_pdf_link(paper_title):
    # Step 1: Search on Google Scholar
    query = urllib.parse.quote_plus(paper_title)
    scholar_url = f"https://scholar.google.com/scholar?q={query}"

    print("[*] Searching Google Scholar...")
    response = requests.get(scholar_url, headers=get_random_headers())
    if response.status_code != 200:
        print("[-] Failed to fetch Google Scholar results.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    first_result = soup.select_one('h3.gs_rt a')
    if not first_result or "mdpi.com" not in first_result['href']:
        print("[-] No MDPI link found in the first result.")
        return None

    article_url = first_result['href']
    print(f"[+] Found MDPI article link: {article_url}")

    # Step 2: Use Selenium to fetch the MDPI article page
    driver = setup_selenium()

    for attempt in range(3):
        print(f"[*] Attempting to fetch MDPI article page... (Try {attempt+1})")
        try:
            driver.get(article_url)
            time.sleep(5)  # Allow JS content to load

            # Fetch the page source after JavaScript rendering
            article_html = driver.page_source
            article_soup = BeautifulSoup(article_html, "html.parser")

            download_link_tag = article_soup.find("a", id="js-button-download")

            if download_link_tag and download_link_tag.get("href"):
                pdf_full_url = f"https://www.mdpi.com{download_link_tag['href']}"
                print(f"[+] Final PDF URL: {pdf_full_url}")
                driver.quit()
                return pdf_full_url
            else:
                print("[-] PDF download button not found.")
                driver.quit()
                return None
        except Exception as e:
            print(f"[!] Exception: {e}")
            driver.quit()
            return None

    print("[-] Failed to load MDPI article page after multiple tries.")
    driver.quit()
    return None

# Example usage
title = "Challenges and Trends of Financial Technology (Fintech): A Systematic Literature Review"
fetch_mdpi_pdf_link(title)

#
# Selenium Example (if needed) for 403 error handling
# This is an example of how to use Selenium to fetch a page that might be blocked by a 403 error.
#
#
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# import time
#
# # Configure headless Chrome
# options = Options()
# options.add_argument('--headless')  # Run without GUI
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# options.add_argument('--window-size=1920,1080')
# options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                      'AppleWebKit/537.36 (KHTML, like Gecko) '
#                      'Chrome/122.0.0.0 Safari/537.36')
#
# # Path to chromedriver (if not in PATH, provide full path)
# driver = webdriver.Chrome(options=options)
#
# # URL to scrape
# url = "https://www.mdpi.com/2078-2489/11/12/590"
#
# # Load the page
# driver.get(url)
#
# # Optional: wait for JavaScript content to load
# time.sleep(5)
#
# # Get full HTML
# html = driver.page_source
#
# # Print or save HTML
# print(html)
#
# # Clean up
# driver.quit()
#
