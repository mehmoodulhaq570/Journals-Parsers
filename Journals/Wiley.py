# ====================Wires Wiley====================
#
import requests

def get_doi_by_title(title):
    # Search DOI using CrossRef API
    url = "https://api.crossref.org/works"
    params = {'query': title}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['message']['items']:
            doi = data['message']['items'][0].get('DOI', None)
            return doi
    return None

def construct_pdf_download_link(doi):
    # Construct Wiley PDF download link
    if doi:
        base_url = "https://wires.onlinelibrary.wiley.com"
        pdf_link = f"{base_url}/doi/pdfdirect/{doi}?download=true"
        return pdf_link
    return None

# Paper title
title = "Hybrid CNN-LSTM Deep Learning for Track-Wise GNSS-R Ocean Wind Speed Retrieval"

# Get DOI
doi = get_doi_by_title(title)

# Generate PDF link and save to a .txt file
if doi:
    pdf_link = construct_pdf_download_link(doi)
    filename = f"pdf_link - {title}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"DOI: {doi}\n")
        f.write(f"PDF Link: {pdf_link}\n")

    print(f"PDF link saved to '{filename}'")
else:
    print("DOI not found for the given title.")



# import requests
#
# def get_doi_by_title(title):
#     # URL of CrossRef's API for searching papers by title
#     url = f"https://api.crossref.org/works"
#
#     # Send a GET request with the title as the query parameter
#     params = {'query': title}
#     response = requests.get(url, params=params)
#
#     # Check if the request was successful
#     if response.status_code == 200:
#         data = response.json()
#
#         # Extract the DOI from the first result
#         if data['message']['items']:
#             doi = data['message']['items'][0].get('DOI', 'DOI not found')
#
#             # Prepend the Wiley Online Library base URL to the DOI
#             wiley_doi_link = f"https://wires.onlinelibrary.wiley.com/doi/{doi}"
#             return wiley_doi_link
#         else:
#             return 'No results found for this title.'
#     else:
#         return f"Error: {response.status_code}"
#
# # Example usage:
# title = "Development evolving: the origins and meanings of instinct"
# doi_link = get_doi_by_title(title)
# print(f"Link to the paper '{title}': {doi_link}")


# Get url and updated pdf url ================================

# import requests
# from bs4 import BeautifulSoup

# # Function to get DOI link by paper title using CrossRef API
# def get_doi_by_title(title):
#     # URL of CrossRef's API for searching papers by title
#     url = "https://api.crossref.org/works"

#     # Send a GET request with the title as the query parameter
#     params = {'query': title}
#     response = requests.get(url, params=params)

#     # Check if the request was successful
#     if response.status_code == 200:
#         data = response.json()

#         # Extract the DOI from the first result
#         if data['message']['items']:
#             doi = data['message']['items'][0].get('DOI', 'DOI not found')

#             # Prepend the Wiley Online Library base URL to the DOI
#             wiley_doi_link = f"https://wires.onlinelibrary.wiley.com/doi/{doi}"
#             print(f"DOI Link: {wiley_doi_link}")
#             return wiley_doi_link
#         else:
#             return 'No results found for this title.'
#     else:
#         return f"Error: {response.status_code}"

# # Function to get the PDF download link from the given ePDF link
# def get_pdf_download_link(epdf_url):
#     # Print the updated link before parsing
#     updated_link = epdf_url.replace('doi', 'doi/epdf')  # Replace 'doi' with 'doi/epdf' for ePDF
#     print(f"Updated ePDF URL: {updated_link}")

#     # Send a GET request to fetch the HTML content of the ePDF link
#     response = requests.get(updated_link)

#     # Check if the request was successful
#     if response.status_code == 200:
#         # Parse the HTML content using BeautifulSoup
#         soup = BeautifulSoup(response.content, 'html.parser')

#         # Find the anchor tag with the class "download"
#         download_link_tag = soup.find('a', class_='download')

#         # If the download link is found, extract the href attribute
#         if download_link_tag:
#             href = download_link_tag.get('href')
#             # Return the full PDF download URL by concatenating the base URL
#             return 'https://wires.onlinelibrary.wiley.com' + href
#         else:
#             return 'Download link not found'
#     else:
#         return 'Failed to retrieve the webpage'

# # Example usage:
# title = "Development evolving: the origins and meanings of instinct"

# # Get the DOI link based on the paper title
# doi_link = get_doi_by_title(title)

# # Print the DOI link
# #print(f"Link to the paper '{title}': {doi_link}")

# # If the DOI link is valid, try to extract the PDF download link
# if doi_link != 'No results found for this title.' and 'Error' not in doi_link:
#     pdf_link = get_pdf_download_link(doi_link)
#     print(f"PDF Download link: {pdf_link}")

