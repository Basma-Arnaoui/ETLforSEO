from flask import Flask, render_template, request, jsonify
import sqlite3
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
import json
import time
import re
import os

nltk.download('punkt', quiet=True)
app = Flask(__name__)

class KeywordAnalyzer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        print("[INFO] KeywordAnalyzer initialized")
        
    def get_data(self, keyword):
        print(f"[INFO] Fetching data for keyword: {keyword}")
        start_time = time.time()
        try:
            conn = sqlite3.connect('backend/grouped_data.db')
            query = """
            SELECT domain, combined_text
            FROM domain_data 
            WHERE combined_text LIKE ?
            LIMIT 1000
            """
            df = pd.read_sql_query(query, conn, params=[f'%{keyword}%'])
            conn.close()
            
            fetch_time = time.time() - start_time
            
            if not df.empty:
                # Calculate keyword position relative to text length
                df['position_category'] = df['combined_text'].apply(
                    lambda text: self.categorize_position(text, keyword)
                )
                df['fetch_time'] = fetch_time
            
            print(f"[INFO] Found {len(df)} records in {fetch_time:.2f} seconds")
            return df
        except Exception as e:
            print(f"[ERROR] Database error: {str(e)}")
            return pd.DataFrame(columns=['domain', 'combined_text', 'position_category', 'fetch_time'])

    def categorize_position(self, text, keyword):
        tokens = text.split()
        keyword_indices = [i for i, token in enumerate(tokens) if keyword.lower() in token.lower()]

        if not keyword_indices:
            return 'Unknown'

        avg_index = sum(keyword_indices) / len(keyword_indices)
        relative_position = avg_index / len(tokens)

        if relative_position < 0.33:
            return 'Top'
        elif relative_position < 0.66:
            return 'Middle'
        else:
            return 'Bottom'

    def create_visualization(self, viz_type, data, layout):
        return {
            'data': data,
            'layout': {
                **layout,
                'template': 'plotly_white',
                'margin': {'l': 40, 'r': 30, 't': 40, 'b': 40},
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'height': 300,
                'font': {'family': 'Arial, sans-serif', 'size': 10}
            }
        }

    def analyze_keyword(self, keyword):
        print(f"[INFO] Starting analysis for keyword: {keyword}")
        start_time = time.time()

        df = self.get_data(keyword)
        if df is None or df.empty:
            return None

        results = {}
        try:
            results['domain_analysis'] = self.analyze_domains(df, keyword)
            results['related_terms'] = self.analyze_related_terms(df)
            results['context_analysis'] = self.analyze_context(df, keyword)
            results['network_analysis'] = self.analyze_network(df, keyword)
            results['location_analysis'] = self.analyze_location(df, keyword)
            
            # Add timing information
            results['analysis_time'] = time.time() - start_time
            results['fetch_time'] = df['fetch_time'].iloc[0] if not df.empty else 0
            
        except Exception as e:
            print(f"[ERROR] Analysis error: {str(e)}")
            return None

        return results

    def analyze_domains(self, df, keyword):
        df['keyword_count'] = df['combined_text'].str.lower().str.count(keyword.lower())
        domain_counts = df.groupby('domain')['keyword_count'].sum().sort_values(ascending=False).head(10)
        
        return self.create_visualization(
            'bar',
            [{
                'type': 'bar',
                'x': domain_counts.values.tolist(),
                'y': domain_counts.index.tolist(),
                'orientation': 'h',
                'marker': {
                    'color': '#3498db',
                    'line': {'width': 1, 'color': '#2980b9'}
                }
            }],
            {
                'title': 'Top Domains Using This Keyword',
                'xaxis': {'title': 'Frequency'},
                'yaxis': {'title': 'Domain', 'categoryorder': 'total ascending', 'automargin': True}
            }
        )

    def analyze_related_terms(self, df):
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(df['combined_text'])
        feature_names = vectorizer.get_feature_names_out()
        tfidf_mean = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
        
        top_indices = tfidf_mean.argsort()[-10:][::-1]
        top_terms = [(feature_names[i], float(tfidf_mean[i])) for i in top_indices]
        
        return self.create_visualization(
            'bar',
            [{
                'type': 'bar',
                'x': [score for _, score in top_terms],
                'y': [term for term, _ in top_terms],
                'orientation': 'h',
                'marker': {
                    'color': '#2ecc71',
                    'line': {'width': 1, 'color': '#27ae60'}
                }
            }],
            {
                'title': 'Most Relevant Related Terms',
                'xaxis': {'title': 'TF-IDF Score'},
                'yaxis': {'title': 'Term', 'categoryorder': 'total ascending', 'automargin': True}
            }
        )

    def analyze_context(self, df, keyword):
        text = ' '.join(df['combined_text'])
        tokens = word_tokenize(text.lower())
        window_size = 5
        
        context_words = []
        for i, token in enumerate(tokens):
            if token == keyword.lower():
                start = max(0, i - window_size)
                end = min(len(tokens), i + window_size + 1)
                context_words.extend(tokens[start:end])
                
        context_freq = Counter(context_words)
        del context_freq[keyword.lower()]
        
        top_context = pd.DataFrame(
            context_freq.most_common(10),
            columns=['word', 'frequency']
        )
        
        return self.create_visualization(
            'bar',
            [{
                'type': 'bar',
                'x': top_context['frequency'].tolist(),
                'y': top_context['word'].tolist(),
                'orientation': 'h',
                'marker': {
                    'color': '#e74c3c',
                    'line': {'width': 1, 'color': '#c0392b'}
                }
            }],
            {
                'title': f'Words Commonly Found Near "{keyword}"',
                'xaxis': {'title': 'Frequency'},
                'yaxis': {'title': 'Words', 'categoryorder': 'total ascending', 'automargin': True}
            }
        )

    def analyze_network(self, df, keyword):
        text = ' '.join(df['combined_text'].str.lower())
        tokens = word_tokenize(text)
        trigrams = list(ngrams(tokens, 3))
        
        keyword_trigrams = [tg for tg in trigrams if keyword.lower() in tg][:1000]
        trigram_freq = Counter(keyword_trigrams).most_common(8)
        
        if trigram_freq:
            pairs = pd.DataFrame(trigram_freq, columns=['trigram', 'weight'])
            pairs['connection'] = pairs['trigram'].apply(lambda x: ' → '.join(x))
            
            return self.create_visualization(
                'bar',
                [{
                    'type': 'bar',
                    'x': pairs['weight'].tolist(),
                    'y': pairs['connection'].tolist(),
                    'orientation': 'h',
                    'marker': {
                        'color': '#9b59b6',
                        'line': {'width': 1, 'color': '#8e44ad'}
                    }
                }],
                {
                    'title': f'Common Word Patterns with "{keyword}"',
                    'xaxis': {'title': 'Frequency'},
                    'yaxis': {'title': 'Word Pattern', 'categoryorder': 'total ascending', 'automargin': True}
                }
            )
        return None

    def analyze_location(self, df, keyword):
        position_counts = df['position_category'].value_counts()
        
        return self.create_visualization(
            'bar',
            [{
                'type': 'bar',
                'x': position_counts.values.tolist(),
                'y': position_counts.index.tolist(),
                'orientation': 'h',
                'marker': {
                    'color': '#f1c40f',
                    'line': {'width': 1, 'color': '#f39c12'}
                }
            }],
            {
                'title': 'Keyword Position in Content',
                'xaxis': {'title': 'Number of Occurrences'},
                'yaxis': {'title': 'Position', 'categoryorder': 'total ascending', 'automargin': True}
            }
        )

analyzer = KeywordAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    keyword = request.json.get('keyword', '').strip()
    print(f"[INFO] Received analysis request for keyword: {keyword}")
    
    if not keyword:
        return jsonify({'error': 'Please enter a keyword'}), 400
        
    results = analyzer.analyze_keyword(keyword)
    if not results:
        return jsonify({'error': 'No data found for the keyword'}), 404

    # Prepare response with timing information
    message = f"Found data in {results['fetch_time']:.2f} seconds"
    analysis_message = f"Analysis completed in {results['analysis_time']:.2f} seconds"
    
    return jsonify({
        **results,
        'message': message,
        'analysis_message': analysis_message
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        conn = sqlite3.connect('backend/grouped_data.db')
        cursor = conn.cursor()
        
        stats = {
            'total_domains': cursor.execute('SELECT COUNT(DISTINCT domain) FROM domain_data').fetchone()[0],
            'total_records': 10971, 
            'avg_text_length': cursor.execute('SELECT AVG(LENGTH(combined_text)) FROM domain_data').fetchone()[0]
        }
        
        conn.close()
        return jsonify(stats)
    except Exception as e:
        print(f"[ERROR] Failed to get stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve database statistics'}), 500

if __name__ == "__main__":
    print("[INFO] Starting server...")
    app.run(debug=True, threaded=True)