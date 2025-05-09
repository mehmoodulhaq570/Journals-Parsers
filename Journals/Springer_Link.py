# This works with springer link and nature.com

import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Function to get DOI from CrossRef using the paper title
def get_doi_from_crossref(paper_title):
    query = urllib.parse.quote_plus(paper_title)
    crossref_url = f"https://api.crossref.org/works?query={query}&rows=1"

    response = requests.get(crossref_url)
    if response.status_code != 200:
        print("Failed to fetch DOI from CrossRef.")
        return None

    data = response.json()
    items = data.get("message", {}).get("items", [])

    if items:
        return items[0].get("DOI")
    else:
        print("No DOI found for the given paper title.")
        return None

# Function to get PDF URL and article title from Springer using DOI
def get_pdf_url_and_title(doi):
    springer_url = f"https://link.springer.com/article/{doi}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(springer_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch article page from Springer.")
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title from meta tag
    title_tag = soup.find("meta", attrs={"name": "dc.title"})
    title = title_tag["content"].strip() if title_tag else "Unknown_Title"

    # Extract PDF link
    pdf_tag = soup.find("a", href=True, string=lambda text: text and "pdf" in text.lower())
    if pdf_tag:
        return urllib.parse.urljoin(springer_url, pdf_tag["href"]), title

    # Fallback: links ending in .pdf
    pdf_links = soup.find_all("a", href=lambda href: href and href.lower().endswith(".pdf"))
    if pdf_links:
        return urllib.parse.urljoin(springer_url, pdf_links[0]["href"]), title

    print("PDF link not found on the article page.")
    return None, title

# Function to download PDF using its URL and article title
def download_pdf(pdf_url, title):
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    filename = f"{safe_title}.pdf"

    response = requests.get(pdf_url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"PDF downloaded and saved as: {filename}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")

# === MAIN ===
paper_title = "Global emergence of unprecedented lifetime exposure to climate extremes"
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
