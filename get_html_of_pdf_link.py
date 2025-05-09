import requests

def save_pdf_from_url_with_session(doi, filename="downloaded_article.pdf"):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://www.tandfonline.com/doi/full/{doi}"
    }

    # Step 1: Visit the full article page to get cookies
    full_url = f"https://www.tandfonline.com/doi/full/{doi}"
    session.get(full_url, headers=headers)

    # Step 2: Try downloading the PDF with the same session
    pdf_url = f"https://www.tandfonline.com/doi/pdf/{doi}?download=true"
    response = session.get(pdf_url, headers=headers)

    if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"[✓] PDF saved as '{filename}'")
    else:
        print(f"[!] Failed to download PDF. Status: {response.status_code}")

# Example usage
doi = "10.1080/16000870.2014.967710"
save_pdf_from_url_with_session(doi)
