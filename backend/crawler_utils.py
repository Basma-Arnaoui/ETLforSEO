import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import time

from db_utils import is_url_scraped, save_scraped_data, save_inaccessible_site

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    )
}

# Dictionary to hold locks per domain
domain_locks = {}
domain_locks_lock = threading.Lock()

def get_domain(url):
    """Extract the domain from a URL."""
    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc
    return domain

def acquire_domain_lock(domain):
    """Acquire a lock for a specific domain to prevent concurrent scraping."""
    with domain_locks_lock:
        if domain not in domain_locks:
            domain_locks[domain] = threading.Lock()
        lock = domain_locks[domain]
    lock.acquire()

def release_domain_lock(domain):
    """Release the lock for a specific domain."""
    with domain_locks_lock:
        lock = domain_locks.get(domain)
    if lock:
        lock.release()

def force_protocol(url):
    """Ensure the URL starts with http:// or https://. Prefer https if possible."""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            url = re.sub(r'^http://', 'https://', url, count=1)
    except requests.exceptions.RequestException:
        url = re.sub(r'^http://', 'https://', url, count=1)
    return url

def scrape_text(url, session):
    """Scrape the text content from the given URL."""
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            return text
        else:
            save_inaccessible_site(url, f"Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        save_inaccessible_site(url, str(e))
        return None

def crawl_and_scrape(url, depth=1, max_links=20):
    """
    Crawl a single domain up to the specified depth and scrape accessible pages.

    Args:
        url (str): The starting URL.
        depth (int): Crawling depth.
        max_links (int): Maximum number of pages to scrape per domain.
    """
    start_time = time.time()
    initial_url = force_protocol(url)
    domain = get_domain(initial_url)

    # Acquire lock for the domain
    acquire_domain_lock(domain)
    try:
        if is_url_scraped(initial_url):
            print(f"[{domain}] Already scraped. Skipping: {initial_url}")
            return

        queue = [(initial_url, 0)]
        scraped_count = 0
        visited = set()

        session = requests.Session()

        while queue:
            current_url, current_depth = queue.pop(0)
            if current_url in visited:
                continue
            visited.add(current_url)

            if scraped_count >= max_links:
                print(f"[{domain}] Reached max limit of {max_links} links.")
                break

            print(f"[{domain}] Scraping ({scraped_count + 1}/{max_links}): {current_url}")
            text = scrape_text(current_url, session)

            if text:
                save_scraped_data(current_url, text)
                scraped_count += 1

                if current_depth < depth:
                    try:
                        response = session.get(current_url, timeout=5)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            anchors = soup.find_all('a', href=True)
                            for a in anchors:
                                href = a['href'].strip()
                                if not href or href == " ":
                                    continue
                                # Resolve relative URLs
                                child_url = urljoin(current_url, href)
                                child_domain = get_domain(child_url)
                                if child_domain == domain:
                                    if child_url not in visited and not is_url_scraped(child_url):
                                        queue.append((child_url, current_depth + 1))
                                        if len(queue) + scraped_count >= max_links:
                                            break
                    except requests.exceptions.RequestException as e:
                        save_inaccessible_site(current_url, str(e))
                        continue
            else:
                print(f"[{domain}] Failed to scrape: {current_url}")
    finally:
        # Release domain lock
        release_domain_lock(domain)
        elapsed = time.time() - start_time
        print(f"[{domain}] Completed in {elapsed:.2f} seconds.")

def crawl_links_parallel(links, depth=1, max_links=20, max_workers=5):
    """
    Crawl and scrape multiple domains in parallel.

    Args:
        links (list): List of URLs to crawl.
        depth (int): Crawling depth.
        max_links (int): Maximum number of pages to scrape per domain.
        max_workers (int): Number of parallel threads.
    """
    total_companies = len(links)
    completed_companies = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(crawl_and_scrape, link, depth, max_links): link for link in links}
        for future in futures:
            link = futures[future]
            try:
                future.result()
                completed_companies += 1
                print(f"Completed {completed_companies}/{total_companies} companies.")
            except Exception as exc:
                print(f"[Error] {link} generated an exception: {exc}")
