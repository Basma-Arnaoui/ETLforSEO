import re
import sqlite3
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from concurrent.futures import ThreadPoolExecutor, as_completed

import nltk
nltk.download('stopwords')
nltk.download('punkt')

def clean_text(text):
    stop_words = set(stopwords.words('english'))
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    words = word_tokenize(text.lower())
    cleaned_text = ' '.join([word for word in words if word not in stop_words])
    return cleaned_text

def process_row(row):
    url, text = row
    cleaned_text = clean_text(text)
    return (url, cleaned_text)

def store_cleaned_data():
    # Connect to the original database to read the raw data
    conn = sqlite3.connect('backend/scraped_data.db')
    cursor = conn.cursor()
    
    # Read data from the web_content table
    cursor.execute('SELECT url, text_content FROM web_content')
    rows = cursor.fetchall()
    conn.close()
    
    # Connect to the new database to store the cleaned data
    conn_cleaned = sqlite3.connect('backend/cleaned_data.db')
    cursor_cleaned = conn_cleaned.cursor()
    
    cursor_cleaned.execute('CREATE TABLE IF NOT EXISTS cleaned_data (url TEXT, cleaned_text TEXT)')
    
    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_row = {executor.submit(process_row, row): row for row in rows}
        count = 0
        for future in as_completed(future_to_row):
            url, cleaned_text = future.result()
            cursor_cleaned.execute('INSERT INTO cleaned_data (url, cleaned_text) VALUES (?, ?)', (url, cleaned_text))
            count += 1
            if count % 10 == 0:
                print(f"{count} rows cleaned and stored.")
    
    conn_cleaned.commit()
    conn_cleaned.close()

if __name__ == "__main__":
    store_cleaned_data()