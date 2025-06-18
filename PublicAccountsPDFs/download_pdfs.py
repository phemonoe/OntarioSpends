#!/usr/bin/env python3
import os
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re  # Added for sanitizing file names

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Global set to avoid revisiting URLs
visited_urls = set()

def sanitize_filename(name):
    """Remove or replace characters that are invalid in filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_pdf(pdf_url, dest_base, file_name=None):
    """
    Downloads a PDF from pdf_url and saves it under dest_base.
    If file_name is provided, it is sanitized and used for the saved file.
    Otherwise, the URL's path is used.
    """
    try:
        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()
    except Exception as e:
        logging.error("Failed to download {}: {}".format(pdf_url, e))
        return

    parsed = urlparse(pdf_url)
    # Extract a year folder from the URL path if available
    path_parts = parsed.path.lstrip("/").split("/")
    year_folder = None
    for part in path_parts:
        if re.match(r'^(19|20)\d{2}$', part):
            year_folder = part
            break
    if not year_folder:
        year_folder = "misc"
    full_directory = os.path.join(dest_base, year_folder)
    os.makedirs(full_directory, exist_ok=True)

    if file_name:
        sanitized_name = sanitize_filename(file_name)
        if not sanitized_name.lower().endswith(".pdf"):
            sanitized_name += ".pdf"
        local_path = os.path.join(full_directory, sanitized_name)
    else:
        # Use the original file name from URL's last segment as a fallback
        original_name = os.path.basename(parsed.path)
        local_path = os.path.join(full_directory, original_name)

    logging.info("Downloading PDF: {} -> {}".format(pdf_url, local_path))
    try:
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        logging.error("Error writing file {}: {}".format(local_path, e))

def parse_page(url, dest_base, depth=0, base_domain=None):
    """
    Parses an HTML page for links. Downloads PDFs and recursively
    follows further HTML links.
    
    Logs a warning if a link is followed at a deeper more than one level.
    """
    global visited_urls
    if base_domain is None:
        base_domain = urlparse(url).netloc

    if url in visited_urls:
        return
    visited_urls.add(url)

    try:
        logging.info("Processing URL (depth {}): {}".format(depth, url))
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        logging.error("Failed to fetch {}: {}".format(url, e))
        return

    # Only parse HTML pages
    content_type = response.headers.get('Content-Type', '')
    if 'text/html' not in content_type:
        logging.info("Skipping non-HTML content at {} (Content-Type: {})".format(url, content_type))
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    for tag in soup.find_all('a'):
        href = tag.get('href')
        if not href:
            continue

        # Resolve the URL relative to the current page
        new_url = urljoin(url, href)
        # Remove any URL fragment (#anchor)
        new_url = new_url.split("#")[0]

        parsed_new = urlparse(new_url)
        # Skip links that point to an external domain
        if parsed_new.netloc and parsed_new.netloc != base_domain:
            logging.info("Skipping external link: {}".format(new_url))
            continue

        if new_url in visited_urls:
            continue

        if new_url.lower().endswith('.pdf'):
            link_text = tag.get_text(strip=True)
            download_pdf(new_url, dest_base, file_name=link_text)
        else:
            if depth >= 1:
                logging.warning("Following nested HTML link (depth {}): {}".format(depth+1, new_url))
            parse_page(new_url, dest_base, depth + 1, base_domain)

def main():
    # Starting URL as provided
    start_url = "https://epe.lac-bac.gc.ca/100/201/301/public_accounts_can/pdf/index.html"
    # Base directory where PDFs will be stored (root folder is 'pdfs')
    dest_base = "pdfs"
    
    parse_page(start_url, dest_base)

if __name__ == "__main__":
    main() 