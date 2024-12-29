import sqlite3
from urllib.parse import urlparse

def group_by_domain():
    conn = sqlite3.connect('backend/cleaned_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, cleaned_text FROM cleaned_data')
    rows = cursor.fetchall()
    
    domain_dict = {}
    for url, text in rows:
        domain = urlparse(url).netloc
        if domain in domain_dict:
            domain_dict[domain] += ' ' + text
        else:
            domain_dict[domain] = text
        print("url print")

    # Store grouped data
    conn_grouped = sqlite3.connect('backend/grouped_data.db')
    cursor_grouped = conn_grouped.cursor()
    cursor_grouped.execute('CREATE TABLE IF NOT EXISTS domain_data (domain TEXT, combined_text TEXT)')

    for domain, combined_text in domain_dict.items():
        cursor_grouped.execute('INSERT INTO domain_data VALUES (?, ?)', (domain, combined_text))

    conn_grouped.commit()
    conn_grouped.close()
    conn.close()

if __name__ == "__main__":
    group_by_domain()  