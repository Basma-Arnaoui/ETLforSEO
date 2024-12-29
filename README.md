# Web Crawling and Keyword Analysis System: An ETL Pipeline for SEO Analysis

## Overview
This project implements a comprehensive Extract, Transform, Load (ETL) pipeline designed for web crawling and keyword analysis. The system processes datasets of company websites, extracts their textual content through intelligent crawling mechanisms, and provides sophisticated analysis tools for keyword insights. By combining parallel processing techniques with natural language processing, it creates a scalable and efficient SEO analysis platform.

🔗 **Live Demo:** [BasmaETLProject.pythonanywhere.com](https://basmaetlproject.pythonanywhere.com)

## System Architecture

### 1. Data Extraction
- **URL Validation:** Enforces proper protocols (http/https) and tests server responses
- **Domain Locks:** Prevents simultaneous requests to ensure respectful crawling
- **Parallel Crawling:** Multiple domains scraped concurrently using thread pools
- **Depth and Link Limits:** Prevents overloading through controlled crawling
- **Content Extraction:** HTML parsing using BeautifulSoup
- **Error Logging:** Tracks inaccessible URLs while storing successful scrapes

### 2. Data Storage
The system uses multiple SQLite databases:

- **scraped_data.db:** Raw HTML content and extracted text
- **inaccessible_sites.db:** Failed URLs with error details
- **cleaned_data.db:** Processed text without HTML tags/special characters
- **grouped_data.db:** Content aggregated by domain

### 3. Data Transformation
Key processing steps include:

**Text Cleaning:**
- Remove non-alphanumeric characters and excess whitespace
- Convert text to lowercase
- Eliminate stop words using NLTK
- Exclude common website terms

**Data Processing Pipeline:**
- Multi-threaded cleaning of raw text
- Domain-level content aggregation
- Short/irrelevant word removal
- Content optimization for analysis

### 4. Analysis System

#### Keyword Analysis Engine
The system provides multiple analysis types:

1. **Domain Analysis**
   - Tracks keyword frequency across domains
   - Identifies market leaders and trends
   - Visualizes top domains using interactive charts

2. **Related Terms Analysis**
   - Uses TF-IDF to find associated keywords
   - Analyzes single words and bigrams
   - Highlights significant term relationships

3. **Context Analysis**
   - Examines words within 5-word windows
   - Maps keyword usage patterns
   - Provides insight into term associations

4. **Network Analysis**
   - Detects three-word sequences (trigrams)
   - Reveals common phrase patterns
   - Helps understand keyword context

5. **Location Analysis**
   - Tracks keyword positioning in content
   - Categories: top, middle, bottom
   - Aids in optimization strategies


## Web Interface

### Frontend Features
- Real-time keyword analysis
- Interactive Plotly visualizations
- Responsive Tailwind CSS design
- Database statistics dashboard



## Deployment
The system is deployed on PythonAnywhere, offering:
- 24/7 accessibility
- Web-based analysis tools
- Configuration-free testing
- Streamlined deployment process

## Challenges and Solutions

### 1. Concurrent Access
**Challenge:** Multiple threads attempting to access the same domain
**Solution:** Implemented domain-level locking using threading.Lock()

### 2. Resource Management
**Challenge:** Potential for infinite crawling depth
**Solution:** Implemented depth limits and maximum sublink restrictions

## Future Improvements

1. **Selenium Integration**
   - Simulate real user behavior
   - Access JavaScript-rendered content
   - Bypass bot detection mechanisms

2. **Advanced NLP Techniques**
   - Enhance text analysis accuracy
   - Implement more sophisticated algorithms

3. **Sentiment Analysis**
   - Extract emotional context
   - Analyze content tone
   - Provide deeper content insights

## Technologies Used
- Python
- Flask
- SQLite
- BeautifulSoup
- NLTK
- Plotly
- Tailwind CSS
- Threading
- TF-IDF

## Getting Started

1. Clone the repository
2. Install dependencies
3. Run the Flask application: `python app.py`
4. Access the web interface at `localhost:5000`

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
