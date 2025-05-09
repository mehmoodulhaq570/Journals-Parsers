#====================IEEE Xplore====================
# This si working for IEEE Xplore

import requests
import urllib.parse
import re
from bs4 import BeautifulSoup
import os

# Define headers to simulate a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com"
}


# Function to get DOI from CrossRef API
def get_doi_from_crossref(paper_title):
    query = urllib.parse.quote_plus(paper_title)
    crossref_url = f"https://api.crossref.org/works?query={query}&rows=1"
    response = requests.get(crossref_url, headers=HEADERS)

    if response.status_code != 200:
        print("Failed to fetch DOI from CrossRef. Status:", response.status_code)
        return None

    data = response.json()
    items = data.get("message", {}).get("items", [])

    if items:
        doi = items[0].get("DOI")
        return doi
    else:
        print("No DOI found for the given paper title.")
        return None


# Function to extract PDF URL and title from IEEE Xplore
def get_pdf_url_and_title(doi):
    # Extract arnumber from DOI
    match = re.search(r'\.(\d+)$', doi)
    if not match:
        print("Could not extract IEEE document number from DOI.")
        return None, None

    arnumber = match.group(1)
    doc_url = f"https://ieeexplore.ieee.org/document/{arnumber}/"
    # pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={arnumber}"
    pdf_url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={arnumber}&ref="

    # Fetch document page to get title from meta-description
    response = requests.get(doc_url, headers=HEADERS)
    if response.status_code != 200:
        print("Failed to fetch document page. Status:", response.status_code)
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")
    meta_tag = soup.find("meta", {"id": "meta-description", "name": "Description"})
    if meta_tag and meta_tag.get("content"):
        title = meta_tag["content"]
        return pdf_url, title

    print("Could not extract title from IEEE page.")
    return pdf_url, "Unknown_Title"


# Function to download the PDF
def download_pdf(pdf_url, title):
    filename = re.sub(r'[\\/*?:"<>|]', "", title) + ".pdf"  # Clean filename

    # Start a session to manage cookies and headers
    session = requests.Session()
    session.headers.update(HEADERS)

    # First, follow the initial redirection to get the actual PDF URL
    response = session.get(pdf_url, allow_redirects=True)

    if response.status_code == 200:
        # Check if we have landed on the actual PDF content
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' in content_type:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"PDF downloaded successfully: {filename}")
        else:
            print("The file is not a PDF. Content type:", content_type)
            print("Actual URL: ", response.url)
    else:
        print("Failed to download PDF. Status:", response.status_code)


# === Example Usage ===
paper_title = "Amorphous Solar Module for PV-T Collector for Solar Dryer"
doi = get_doi_from_crossref(paper_title)

if doi:
    print(f"DOI Found: {doi}")
    pdf_url, title = get_pdf_url_and_title(doi)

    if pdf_url:
        print(f"PDF URL: {pdf_url}")
        print(f"Title: {title}")
        download_pdf(pdf_url, title)
    else:
        print("PDF URL could not be retrieved.")
else:
    print("DOI not found.")


