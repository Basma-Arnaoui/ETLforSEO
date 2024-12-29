import sqlite3
import re
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Additional stop words
custom_stop_words = {'us', 'www', 'com', 'html', 'htm', 'php', 'contact', 'home', 'index', 'about', 'service'}
all_stop_words = stop_words.union(custom_stop_words)

# Function to clean grouped database
def clean_grouped_db():
    conn = sqlite3.connect('backend/grouped_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT domain, combined_text FROM domain_data')
    rows = cursor.fetchall()

    cleaned_data = []

    for domain, text in rows:
        # Remove non-alphabetical characters and short words
        cleaned_text = ' '.join([word for word in re.sub(r'[^a-zA-Z ]', ' ', text).split() if len(word) > 2])
        # Remove stopwords
        cleaned_text = ' '.join([word for word in cleaned_text.split() if word.lower() not in all_stop_words])
        cleaned_data.append((domain, cleaned_text))

    cursor.execute('DELETE FROM domain_data')
    cursor.executemany('INSERT INTO domain_data (domain, combined_text) VALUES (?, ?)', cleaned_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    clean_grouped_db()
    print("Grouped database cleaned and optimized.")
