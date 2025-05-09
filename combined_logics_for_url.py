# https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261752  
# Check for this too

import os
import requests
import urllib.parse
import random
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# === Configuration ===
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
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')
    return webdriver.Chrome(options=options)

def get_first_google_scholar_url(paper_title):
    query = urllib.parse.quote_plus(paper_title)
    url = f"https://scholar.google.com/scholar?q={query}"
    response = requests.get(url, headers=get_random_headers())

    if response.status_code != 200:
        print("Failed to fetch search results.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    result = soup.select_one('h3.gs_rt a')
    return result['href'] if result else None

def get_pdf_from_springer_or_nature(article_url):
    response = requests.get(article_url, headers=get_random_headers())
    if response.status_code != 200:
        print("Failed to fetch article page.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    pdf_tag = soup.find("a", attrs={"data-article-pdf": "true"})

    if pdf_tag and pdf_tag.has_attr("href"):
        parsed_url = urllib.parse.urlparse(article_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return urllib.parse.urljoin(base_url, pdf_tag['href'])
    return None

def get_pdf_from_tandfonline(article_url):
    """
    Constructs and returns a direct PDF download link for articles hosted on Taylor & Francis Online.
    Example input: https://www.tandfonline.com/doi/full/10.1080/15435075.2013.849257
    Output: http://tandfonline.com/doi/pdf/10.1080/15435075.2013.849257?download=true
    """
    match = re.search(r'/doi/(?:full|abs|epdf|pdf)/(.+)', article_url)
    if match:
        doi_suffix = match.group(1)
        return f"http://tandfonline.com/doi/pdf/{doi_suffix}?download=true"
    return None


def get_pdf_from_ieee(article_url):
    arnumber_match = re.search(r'/document/(\d+)', article_url)
    if arnumber_match:
        arnumber = arnumber_match.group(1)
        return f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={arnumber}"
    return None

def get_pdf_from_mdpi(article_url):
    driver = setup_selenium()
    try:
        driver.get(article_url)
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        link_tag = soup.find("a", id="js-button-download")
        if link_tag and link_tag.get("href"):
            return f"https://www.mdpi.com{link_tag['href']}"
    finally:
        driver.quit()
    return None

def sanitize_filename(title):
    return "".join(c if c.isalnum() or c in " ._-" else "_" for c in title)[:150]

def download_pdf(pdf_url, title):
    try:
        response = requests.get(pdf_url, headers=get_random_headers(), stream=True, timeout=30)
        if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
            os.makedirs("downloads", exist_ok=True)
            filename = sanitize_filename(title) + ".pdf"
            file_path = os.path.join("downloads", filename)
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[✓] Saved as: {file_path}")
            return True
        else:
            print("[-] Invalid PDF or failed download.")
    except Exception as e:
        print(f"[!] Exception during PDF download: {e}")
    return False

def get_pdf_link(paper_title):
    article_url = get_first_google_scholar_url(paper_title)
    if not article_url:
        print("No article URL found.")
        return None

    print(f"[+] First Result URL: {article_url}")

    if "ieeexplore.ieee.org" in article_url:
        return get_pdf_from_ieee(article_url)
    elif "link.springer.com" in article_url or "nature.com" in article_url:
        return get_pdf_from_springer_or_nature(article_url)
    elif "mdpi.com" in article_url:
        return get_pdf_from_mdpi(article_url)
    elif "tandfonline.com" in article_url:
        return get_pdf_from_tandfonline(article_url)

    print("[-] PDF download link not found or unsupported source.")
    return None

def process_titles(file_path="titles.txt"):
    failed = []
    os.makedirs("downloads", exist_ok=True)

    with open(file_path, "r", encoding="utf-8") as f:
        titles = [line.strip() for line in f if line.strip()]

    for idx, title in enumerate(titles, start=1):
        sanitized_name = sanitize_filename(title)
        output_path = os.path.join("downloads", sanitized_name + ".pdf")

        if os.path.exists(output_path):
            print(f"\n[{idx}/{len(titles)}] Skipping already downloaded: {title}")
            continue

        print(f"\n[{idx}/{len(titles)}] Processing: {title}")
        pdf_url = get_pdf_link(title)

        if pdf_url and download_pdf(pdf_url, title):
            pass
        else:
            failed.append(title)

        time.sleep(random.uniform(4, 8))  # polite delay

    if failed:
        with open("failed_downloads.txt", "w", encoding="utf-8") as f:
            for fail in failed:
                f.write(fail + "\n")
        print(f"\n[!] Failed to download {len(failed)} papers. Saved to 'failed_downloads.txt'.")

if __name__ == "__main__":
    process_titles("titles.txt")
