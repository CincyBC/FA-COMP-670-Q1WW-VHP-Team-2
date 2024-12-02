import requests
import os
import time
from bs4 import BeautifulSoup

def get_html_document(url):
    """Fetch the HTML content of a webpage."""
    url = url.strip()
    response = requests.get(url)
    if response.status_code in [403, 404]:
      return ""
    return response.text

def download_html(url, save_directory):
    """Download the HTML content of a webpage and save it to a file."""
    url = url.strip()
    file_name = url.replace("https://", "").replace("http://", "").split('/')[-1] + ".html"
    save_path = os.path.join(save_directory, file_name)

    if not os.path.exists(save_path):
        print(f"Downloading HTML from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"HTML saved to {save_path}")
    else:
        print(f"HTML already exists at {save_path}")

def extract_and_download_links(url, save_directory):
    """Extract all links from a URL, download files if they are downloadable."""
    url = url.strip()
    html_doc = get_html_document(url)
    soup = BeautifulSoup(html_doc, 'html.parser')
    main_block = soup.find(id='block-fu-franklin-system-system-main')
    if main_block:
        links = main_block.find_all('a', href=True)
    else:
        links = []

    print(links)

    for link in links:
        file_url = link['href']
        # Skip email links, support links, and telephone links
        if "@" in file_url or file_url.startswith("mailto:") or file_url.startswith("https://support.franklin.edu/hc/") or file_url.startswith("tel:"):
            continue

        # Handle relative URLs
        if file_url.startswith("/"):
            file_url = requests.compat.urljoin(url, file_url)

        # Only download files from franklin.edu
        if not file_url.startswith("/") and "franklin.edu" not in file_url:
            continue

        # Extract the file name from the URL
        file_name = file_url.split('/')[-1]
        if '.' not in file_name:
            file_name += '.html'
        save_path = os.path.join(save_directory, file_name)

        if not os.path.exists(save_path):
            print(f"Downloading file from {file_url}...")
            response = requests.get(file_url)
            if response.status_code in [403, 404]:
                print(f"Skipping file due to status code {response.status_code}: {file_url}")
                continue
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"File saved to {save_path}")
            time.sleep(0.5)  # Pause to avoid overwhelming the server
        else:
            print(f"File already exists at {save_path}")

# Step 1: Define URLs and paths
urls = [
    "https://www.franklin.edu/current-students/academic-resources/academic-advising",
    "https://www.franklin.edu/degrees",
    "https://www.franklin.edu/learning-commons/tutoring-workshops/tutoring",
    "https://www.franklin.edu/learning-commons/library",
    "https://www.franklin.edu/current-students/academic-resources/graduation-information",
    "https://www.franklin.edu/current-students/military-veterans/military-benefits",
    "https://www.franklin.edu/current-students/military-veterans/military-benefits/military-family-member-discount",
    "https://www.franklin.edu/current-students/military-veterans/military-benefits/post-911-gi-bill",
    "https://www.franklin.edu/current-students/military-veterans/military-benefits/vocational-rehabilitation-employment",
]
save_directory = "scrapper_data"

# Ensure the directory exists
os.makedirs(save_directory, exist_ok=True)

# Step 2: Iterate over all URLs, download HTML documents, and extract & download links
for url in urls:
    download_html(url, save_directory)
    extract_and_download_links(url, save_directory)
