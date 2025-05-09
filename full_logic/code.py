import os
import requests
import urllib.parse
import random
import re
from bs4 import BeautifulSoup

# User agents for request headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36"
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com"
    }

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

def download_pdf(pdf_url, title):
    os.makedirs("downloads", exist_ok=True)
    filename = os.path.join("downloads", sanitize_filename(title) + ".pdf")
    try:
        response = requests.get(pdf_url, headers=get_random_headers(), stream=True, timeout=15)
        if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"✅ PDF downloaded: {filename}")
            return True
        else:
            print(f"❌ Failed to download PDF. Status: {response.status_code} | Content-Type: {response.headers.get('Content-Type')}")
    except Exception as e:
        print(f"❌ Error downloading PDF: {e}")
    return False

def search_ieee(title):
    search_url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText={urllib.parse.quote_plus(title)}"
    try:
        res = requests.get(search_url, headers=get_random_headers(), timeout=10)
        if res.status_code != 200:
            return None, None
        soup = BeautifulSoup(res.text, 'html.parser')
        script_tag = soup.find("script", string=lambda s: s and "global.document.metadata" in s)
        if not script_tag:
            return None, None
        arnumber = re.search(r'"arnumber":"(\d+)"', script_tag.string)
        if not arnumber:
            return None, None
        arnum = arnumber.group(1)
        pdf_url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={arnum}&ref="
        title = re.search(r'"title":"(.*?)"', script_tag.string)
        return pdf_url, title.group(1) if title else "IEEE_Paper"
    except Exception as e:
        print(f"IEEE error: {e}")
        return None, None

def search_springer(title):
    search_url = f"https://link.springer.com/search?query={urllib.parse.quote_plus(title)}"
    try:
        res = requests.get(search_url, headers=get_random_headers(), timeout=10)
        if res.status_code != 200:
            return None, None
        soup = BeautifulSoup(res.text, 'html.parser')
        link_tag = soup.find("a", href=re.compile(r"^/article/10\.\d{4,9}/[^/]+"))
        if not link_tag:
            return None, None
        article_url = urllib.parse.urljoin("https://link.springer.com", link_tag['href'])
        article_res = requests.get(article_url, headers=get_random_headers())
        if article_res.status_code != 200:
            return None, None
        article_soup = BeautifulSoup(article_res.text, 'html.parser')
        pdf_tag = article_soup.find("a", href=re.compile(r".*\.pdf"))
        title_tag = article_soup.find("meta", {"name": "dc.title"})
        pdf_url = urllib.parse.urljoin(article_url, pdf_tag["href"]) if pdf_tag else None
        title = title_tag["content"] if title_tag else "Springer_Paper"
        return pdf_url, title
    except Exception as e:
        print(f"Springer error: {e}")
        return None, None

def search_tandf(title):
    search_url = f"https://www.tandfonline.com/action/doSearch?AllField={urllib.parse.quote_plus(title)}"
    try:
        res = requests.get(search_url, headers=get_random_headers(), timeout=10)
        if res.status_code != 200:
            return None, None
        soup = BeautifulSoup(res.text, 'html.parser')
        link_tag = soup.find("a", href=re.compile(r"/doi/full/10\.\d{4,9}/[^/]+"))
        if not link_tag:
            return None, None
        doi_url = urllib.parse.urljoin("https://www.tandfonline.com", link_tag['href'])
        doi = re.search(r'/doi/full/(10\.\d{4,9}/[^/]+)', doi_url).group(1)
        pdf_url = f"https://www.tandfonline.com/doi/pdf/{doi}?download=true"
        return pdf_url, doi.replace(".", " ")
    except Exception as e:
        print(f"T&F error: {e}")
        return None, None

def search_wiley(title):
    search_url = f"https://onlinelibrary.wiley.com/action/doSearch?AllField={urllib.parse.quote_plus(title)}"
    try:
        res = requests.get(search_url, headers=get_random_headers(), timeout=10)
        if res.status_code != 200:
            return None, None
        soup = BeautifulSoup(res.text, 'html.parser')
        link_tag = soup.find("a", href=re.compile(r"^/doi/10\.\d{4,9}/[^/]+"))
        if not link_tag:
            return None, None
        article_url = urllib.parse.urljoin("https://onlinelibrary.wiley.com", link_tag['href'])
        article_res = requests.get(article_url, headers=get_random_headers())
        soup2 = BeautifulSoup(article_res.text, 'html.parser')
        pdf_tag = soup2.find("a", href=re.compile(r".*\.pdf"))
        title_tag = soup2.find("meta", {"name": "dc.Title"})
        pdf_url = urllib.parse.urljoin(article_url, pdf_tag["href"]) if pdf_tag else None
        title = title_tag["content"] if title_tag else "Wiley_Paper"
        return pdf_url, title
    except Exception as e:
        print(f"Wiley error: {e}")
        return None, None

def process_title(paper_title):
    print(f"\n🔍 Searching for: {paper_title}")
    for handler in [search_ieee, search_springer, search_tandf, search_wiley]:
        print(f"🔄 Trying {handler.__name__}...")
        pdf_url, title = handler(paper_title)
        if pdf_url:
            print(f"📄 PDF URL: {pdf_url}")
            print(f"📘 Title: {title}")
            success = download_pdf(pdf_url, title)
            if success:
                print(f"✅ Successfully downloaded from {handler.__name__}")
                return True, pdf_url, paper_title
            else:
                print(f"⚠️ Failed to download from {handler.__name__}. Trying next source...")
        else:
            print(f"❌ No valid link found from {handler.__name__}.")
    print("❌ No downloadable PDF found from any supported publisher.")
    return False, None, paper_title

def main_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        titles = [line.strip() for line in f if line.strip()]
    
    with open("failed_download.txt", 'a', encoding='utf-8') as fail_log, \
         open("pdf_link.txt", 'a', encoding='utf-8') as link_log:

        for title in titles:
            success, pdf_url, original_title = process_title(title)
            if success and pdf_url:
                link_log.write(pdf_url + "\n")
            else:
                fail_log.write(original_title + "\n")

# Example usage 
main_from_file(r"C:\Users\mehmo\Downloads\rpdownloader2\full_logic\titles.txt")





# import os
# import re
# import random
# import urllib.parse
# import requests
# from bs4 import BeautifulSoup
# from fuzzywuzzy import fuzz

# # --- Constants ---
# PDF_FOLDER = r"C:\Users\mehmo\Downloads\rpdownloader2\downloads"
# TITLE_FILE = r"C:\Users\mehmo\Downloads\rpdownloader2\full_logic\titles.txt"
# FAILED_LOG = "failed_download.txt"
# PDF_LINK_LOG = "pdf_link.txt"
# MATCH_THRESHOLD = 80

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36"
# ]

# # --- Helper Functions ---

# def get_random_headers():
#     return {
#         "User-Agent": random.choice(USER_AGENTS),
#         "Accept-Language": "en-US,en;q=0.9",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#         "Referer": "https://www.google.com"
#     }

# def sanitize_filename(title):
#     return re.sub(r'[\\/*?:"<>|]', "", title)

# def fuzzy_matched(title, pdf_folder):
#     pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
#     for pdf in pdf_files:
#         score = fuzz.token_set_ratio(title.lower(), os.path.splitext(pdf)[0].lower())
#         if score >= MATCH_THRESHOLD:
#             print(f'✅ Already downloaded: "{title}" ~ "{pdf}" [{score}%]')
#             return True
#     return False

# def fuzzy_title_check(input_title, found_title):
#     score = fuzz.token_set_ratio(input_title.lower(), found_title.lower())
#     print(f"🔎 Fuzzy match: \"{input_title}\" ~ \"{found_title}\" => {score}%")
#     return score >= MATCH_THRESHOLD

# def download_pdf(pdf_url, title):
#     os.makedirs(PDF_FOLDER, exist_ok=True)
#     filename = os.path.join(PDF_FOLDER, sanitize_filename(title) + ".pdf")
#     try:
#         response = requests.get(pdf_url, headers=get_random_headers(), stream=True, timeout=15)
#         if response.status_code == 200 and 'application/pdf' in response.headers.get('Content-Type', ''):
#             with open(filename, "wb") as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)
#             print(f"📥 Downloaded: {filename}")
#             return True
#         else:
#             print(f"❌ Invalid response | Status: {response.status_code} | Content-Type: {response.headers.get('Content-Type')}")
#     except Exception as e:
#         print(f"❌ Exception while downloading PDF: {e}")
#     return False

# # --- Publisher Handlers ---

# def search_ieee(title):
#     try:
#         search_url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText={urllib.parse.quote_plus(title)}"
#         res = requests.get(search_url, headers=get_random_headers(), timeout=10)
#         if res.status_code != 200:
#             return None, None
#         soup = BeautifulSoup(res.text, 'html.parser')
#         script_tag = soup.find("script", string=lambda s: s and "global.document.metadata" in s)
#         if not script_tag:
#             return None, None
#         arnumber = re.search(r'"arnumber":"(\d+)"', script_tag.string)
#         if not arnumber:
#             return None, None
#         arnum = arnumber.group(1)
#         pdf_url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={arnum}&ref="
#         title_match = re.search(r'"title":"(.*?)"', script_tag.string)
#         return pdf_url, title_match.group(1) if title_match else "IEEE_Paper"
#     except Exception as e:
#         print(f"IEEE error: {e}")
#         return None, None

# def search_springer(title):
#     try:
#         search_url = f"https://link.springer.com/search?query={urllib.parse.quote_plus(title)}"
#         res = requests.get(search_url, headers=get_random_headers(), timeout=10)
#         soup = BeautifulSoup(res.text, 'html.parser')
#         link_tag = soup.find("a", href=re.compile(r"^/article/10\.\d{4,9}/[^/]+"))
#         if not link_tag:
#             return None, None
#         article_url = urllib.parse.urljoin("https://link.springer.com", link_tag['href'])
#         article_res = requests.get(article_url, headers=get_random_headers())
#         soup2 = BeautifulSoup(article_res.text, 'html.parser')
#         pdf_tag = soup2.find("a", href=re.compile(r".*\.pdf"))
#         title_tag = soup2.find("meta", {"name": "dc.title"})
#         pdf_url = urllib.parse.urljoin(article_url, pdf_tag["href"]) if pdf_tag else None
#         title = title_tag["content"] if title_tag else "Springer_Paper"
#         return pdf_url, title
#     except Exception as e:
#         print(f"Springer error: {e}")
#         return None, None

# def search_tandf(title):
#     try:
#         search_url = f"https://www.tandfonline.com/action/doSearch?AllField={urllib.parse.quote_plus(title)}"
#         res = requests.get(search_url, headers=get_random_headers(), timeout=10)
#         soup = BeautifulSoup(res.text, 'html.parser')
#         link_tag = soup.find("a", href=re.compile(r"/doi/full/10\.\d{4,9}/[^/]+"))
#         if not link_tag:
#             return None, None
#         doi_url = urllib.parse.urljoin("https://www.tandfonline.com", link_tag['href'])
#         doi = re.search(r'/doi/full/(10\.\d{4,9}/[^/]+)', doi_url).group(1)
#         pdf_url = f"https://www.tandfonline.com/doi/pdf/{doi}?download=true"
#         return pdf_url, doi.replace(".", " ")
#     except Exception as e:
#         print(f"T&F error: {e}")
#         return None, None

# def search_wiley(title):
#     try:
#         search_url = f"https://onlinelibrary.wiley.com/action/doSearch?AllField={urllib.parse.quote_plus(title)}"
#         res = requests.get(search_url, headers=get_random_headers(), timeout=10)
#         soup = BeautifulSoup(res.text, 'html.parser')
#         link_tag = soup.find("a", href=re.compile(r"^/doi/10\.\d{4,9}/[^/]+"))
#         if not link_tag:
#             return None, None
#         article_url = urllib.parse.urljoin("https://onlinelibrary.wiley.com", link_tag['href'])
#         article_res = requests.get(article_url, headers=get_random_headers())
#         soup2 = BeautifulSoup(article_res.text, 'html.parser')
#         pdf_tag = soup2.find("a", href=re.compile(r".*\.pdf"))
#         title_tag = soup2.find("meta", {"name": "dc.Title"})
#         pdf_url = urllib.parse.urljoin(article_url, pdf_tag["href"]) if pdf_tag else None
#         title = title_tag["content"] if title_tag else "Wiley_Paper"
#         return pdf_url, title
#     except Exception as e:
#         print(f"Wiley error: {e}")
#         return None, None

# # --- Main Logic ---

# def main():
#     with open(TITLE_FILE, 'r', encoding='utf-8') as f:
#         titles = [line.strip() for line in f if line.strip()]

#     unmatched = []

#     for paper_title in titles:
#         print(f"\n🔍 Searching: {paper_title}")

#         if fuzzy_matched(paper_title, PDF_FOLDER):
#             continue  # Already exists

#         for handler in [search_ieee, search_springer, search_tandf, search_wiley]:
#             pdf_url, found_title = handler(paper_title)
#             if pdf_url and fuzzy_title_check(paper_title, found_title):
#                 print(f"📄 Found PDF: {pdf_url}")
#                 if download_pdf(pdf_url, found_title):
#                     with open(PDF_LINK_LOG, 'a', encoding='utf-8') as pl:
#                         pl.write(pdf_url + "\n")
#                     break
#                 else:
#                     print("⚠️ Download failed, trying next source...")
#             elif pdf_url:
#                 print("❌ Title mismatch, skipping download.")
#         else:
#             print(f"❌ Not found: {paper_title}")
#             unmatched.append(paper_title)
#             with open(FAILED_LOG, 'a', encoding='utf-8') as fl:
#                 fl.write(paper_title + "\n")

#     with open(TITLE_FILE, 'w', encoding='utf-8') as f:
#         for title in unmatched:
#             f.write(title + "\n")

#     print("\n✅ Process completed.")

# # --- Run Script ---
# if __name__ == "__main__":
#     main()
