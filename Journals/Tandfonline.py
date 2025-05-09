import requests
import urllib.parse
import random
import re

# User agents for CrossRef and Taylor & Francis requests
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
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com"
    }

def get_doi_from_crossref(paper_title):
    query = urllib.parse.quote_plus(paper_title)
    url = f"https://api.crossref.org/works?query={query}&rows=1"

    try:
        response = requests.get(url, headers=get_random_headers())
        if response.status_code == 200:
            data = response.json()
            items = data.get("message", {}).get("items", [])
            if items:
                return items[0].get("DOI")
    except requests.RequestException as e:
        print(f"[!] Error fetching DOI: {e}")
    return None

def get_tandf_pdf_url(doi):
    if doi:
        print("DOI:", doi)
        return f"https://www.tandfonline.com/doi/pdf/{doi}?download=true"
    return None

def save_pdf_from_url(pdf_url, filename="downloaded_article.pdf"):
    try:
        response = requests.get(pdf_url, headers=get_random_headers())
        if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"[✓] PDF saved as '{filename}'")
        else:
            print(f"[!] Failed to download PDF. Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"[!] Error downloading PDF: {e}")

def sanitize_filename(title):
    # Remove invalid characters for filenames
    return re.sub(r'[\\/*?:"<>|]', "", title)

def save_metadata_to_txt(title, doi, pdf_url):
    safe_title = sanitize_filename(title)
    filename = f"pdf_link - {safe_title}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"DOI: {doi}\n")
        f.write(f"PDF Link: {pdf_url}\n")
    print(f"[✓] Metadata saved to '{filename}'")

if __name__ == "__main__":
    paper_title = "A Statistical Model for Wind Power on the Basis of Ramp Analysis"  # Replace with your title
    doi = get_doi_from_crossref(paper_title)

    if doi:
        pdf_url = get_tandf_pdf_url(doi)
        print(f"[✓] PDF Download URL:\n{pdf_url}")
        save_metadata_to_txt(paper_title, doi, pdf_url)
        save_pdf_from_url(pdf_url)  # Save using the default name
    else:
        print("[-] DOI not found. Cannot construct PDF URL.")
