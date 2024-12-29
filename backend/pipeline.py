import csv
import os
import time
from crawler_utils import crawl_links_parallel
from db_utils import init_databases

def read_all_links(csv_file, column_name='Website'):
    """
    Read all links from a CSV file.

    Args:
        csv_file (str): Path to the CSV file.
        column_name (str): The column name containing the URLs.

    Returns:
        list: List of URLs.
    """
    links = []
    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if column_name in row and row[column_name].strip():
                    links.append(row[column_name].strip())
    except FileNotFoundError:
        print(f"CSV file '{csv_file}' not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return links

def main():
    """
    Main function to execute the crawling and scraping process.
    """
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(os.path.dirname(script_dir), '..', 'data', 'companies-12-2-2024 (1).csv')  
    
    # Parameters
    column_name = 'Website'  
    depth = 1
    max_links_per_domain = 20
    max_workers = 5  # Number of parallel threads

    print(f"Reading all links from '{csv_file}'...")
    links = read_all_links(csv_file, column_name)

    if not links:
        print("No links found to process.")
        return

    total_links = len(links)
    print(f"Total links to process: {total_links}\n")

    print(f"Starting to crawl {total_links} links with depth={depth} and max_links={max_links_per_domain} per link.")
    start_time = time.time()

    crawl_links_parallel(links, depth=depth, max_links=max_links_per_domain, max_workers=max_workers)

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\nCrawling completed in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    init_databases()
    main()