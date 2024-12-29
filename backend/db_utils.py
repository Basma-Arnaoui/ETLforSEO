import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPED_DB_PATH = os.path.join(BASE_DIR, 'scraped_data.db')
INACCESSIBLE_DB_PATH = os.path.join(BASE_DIR, 'inaccessible_sites.db')

def init_databases():
    """Initialize the SQLite databases and create the necessary tables."""
    # Initialize scraped data database
    scraped_conn = sqlite3.connect(SCRAPED_DB_PATH)
    scraped_cursor = scraped_conn.cursor()
    scraped_cursor.execute("""
        CREATE TABLE IF NOT EXISTS web_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            text_content TEXT
        )
    """)
    scraped_conn.commit()

    # Initialize inaccessible sites database
    inaccessible_conn = sqlite3.connect(INACCESSIBLE_DB_PATH)
    inaccessible_cursor = inaccessible_conn.cursor()
    inaccessible_cursor.execute("""
        CREATE TABLE IF NOT EXISTS inaccessible_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            reason TEXT
        )
    """)
    inaccessible_conn.commit()

    scraped_conn.close()
    inaccessible_conn.close()

def is_url_scraped(url):
    """Check if the URL has already been scraped."""
    conn = sqlite3.connect(SCRAPED_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM web_content WHERE url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_scraped_data(url, text_content):
    """Save the scraped text content to the database."""
    try:
        conn = sqlite3.connect(SCRAPED_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO web_content (url, text_content) VALUES (?, ?)",
            (url, text_content)
        )
        conn.commit()
        conn.close()
        print(f"[DB] Saved: {url}")
    except Exception as e:
        print(f"[DB Error] Could not save {url}: {e}")

def save_inaccessible_site(url, reason):
    """Save inaccessible site information to a separate database."""
    try:
        conn = sqlite3.connect(INACCESSIBLE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO inaccessible_sites (url, reason) VALUES (?, ?)",
            (url, reason)
        )
        conn.commit()
        conn.close()
        print(f"[Inaccessible] {url} - Reason: {reason}")
    except Exception as e:
        print(f"[DB Error] Could not save inaccessible site {url}: {e}")