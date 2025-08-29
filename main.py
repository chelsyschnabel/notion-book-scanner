# main.py - Cloud Run Book Scanner
import os
import json
import logging
import requests
from flask import Flask, request, render_template_string, jsonify
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Environment variables
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
GOOGLE_BOOKS_API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY', '')

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 Book Scanner</title>
    <script src="https://cdn.jsdelivr.net/npm/quagga@0.12.1/dist/quagga.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .method-section {
            margin: 30px 0;
            padding: 20px;
            border: 2px solid #f0f0f0;
            border-radius: 10px;
            background: #fafafa;
        }
        .method-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #444;
            margin-bottom: 15px;
        }
        .input-group {
            margin: 15px 0;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, textarea:focus {
            border-color: #667eea;
            outline: none;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
            margin: 5px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .scan-button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            width: 100%;
        }
        .batch-button {
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
            width: 100%;
        }
        .add-button {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
            width: 100%;
        }
        #scanner-container {
            display: none;
            margin: 20px 0;
            text-align: center;
        }
        #scanner {
            width: 100%;
            max-width: 400px;
            border: 2px solid #ddd;
            border-radius: 8px;
        }
        .result {
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            font-weight: 500;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .loading {
            background-color: #cce7ff;
            color: #004085;
            border: 1px solid #b3d7ff;
            text-align: center;
        }
        .book-preview {
            display: flex;
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .book-cover {
            width: 80px;
            height: 120px;
            object-fit: cover;
            border-radius: 5px;
            margin-right: 15px;
        }
        .book-info h3 {
            margin: 0 0 5px 0;
            color: #333;
        }
        .book-info p {
            margin: 5px 0;
            color: #666;
            font-size: 14px;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            h1 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Book Scanner</h1>
        
        <!-- Single ISBN Method -->
        <div class="method-section">
            <div class="method-title">🔍 Single Book Scanner</div>
            <div class="input-group">
                <label for="isbn">ISBN Number:</label>
                <input type="text" id="isbn" placeholder="Enter ISBN (10 or 13 digits) or scan barcode">
                <button onclick="scanBarcode()" class="scan-button">📷 Scan Barcode with Camera</button>
                <button onclick="addSingleBook()" class="add-button">➕ Add Book to Collection</button>
            </div>
        </div>

        <!-- Barcode Scanner -->
        <div id="scanner-container">
            <div id="scanner"></div>
            <button onclick="stopScanner()">Stop Scanner</button>
        </div>

        <!-- Batch Method -->
        <div class="method-section">
            <div class="method-title">📚 Batch Book Import</div>
            <div class="input-group">
                <label for="isbn-batch">Multiple ISBNs (one per line):</label>
                <textarea id="isbn-batch" rows="6" placeholder="9781234567890&#10;9780987654321&#10;9781111222333&#10;..."></textarea>
                <button onclick="addBatchBooks()" class="batch-button">📦 Add All Books</button>
            </div>
        </div>

        <!-- Results Display -->
        <div id="results"></div>
    </div>

    <script>
        let scanner = null;

        function scanBarcode() {
            const container = document.getElementById('scanner-container');
            const scannerDiv = document.getElementById('scanner');
            
            container.style.display = 'block';
            scannerDiv.innerHTML = '';
            
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                Quagga.init({
                    inputStream: {
                        name: "Live",
                        type: "LiveStream",
                        target: scannerDiv,
                        constraints: {
                            width: 400,
                            height: 300,
                            facingMode: "environment"
                        },
                    },
                    decoder: {
                        readers: [
                            "ean_reader", 
                            "ean_8_reader", 
                            "code_128_reader",
                            "code_39_reader"
                        ]
                    },
                }, function(err) {
                    if (err) {
                        showResult('❌ Error starting camera: ' + err.message, 'error');
                        container.style.display = 'none';
                        return;
                    }
                    Quagga.start();
                    showResult('📷 Camera started! Point at a barcode...', 'loading');
                });

                Quagga.onDetected(function(result) {
                    const isbn = result.codeResult.code;
                    document.getElementById('isbn').value = isbn;
                    stopScanner();
                    showResult('✅ Barcode detected: ' + isbn, 'success');
                });
            } else {
                showResult('❌ Camera not supported in this browser. Please use manual entry.', 'error');
            }
        }

        function stopScanner() {
            if (Quagga && typeof Quagga.stop === 'function') {
                Quagga.stop();
            }
            document.getElementById('scanner-container').style.display = 'none';
        }

        async function addSingleBook() {
            const isbn = document.getElementById('isbn').value.trim();
            if (!isbn) {
                showResult('❌ Please enter an ISBN or scan a barcode', 'error');
                return;
            }

            if (!isValidISBN(isbn)) {
                showResult('❌ Invalid ISBN format. Please enter 10 or 13 digits.', 'error');
                return;
            }

            showResult('🔄 Processing book...', 'loading');
            
            try {
                const response = await fetch('/add-book', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'single_book',
                        isbn: isbn
                    })
                });

                const result = await response.json();
                
                if (result.success) {
                    showBookResult(result.book);
                    document.getElementById('isbn').value = '';
                } else {
                    showResult('❌ Error: ' + result.error, 'error');
                }
            } catch (error) {
                showResult('❌ Network error: ' + error.message, 'error');
            }
        }

        async function addBatchBooks() {
            const isbns = document.getElementById('isbn-batch').value
                .split('\n')
                .map(isbn => isbn.trim())
                .filter(isbn => isbn && isValidISBN(isbn));

            if (isbns.length === 0) {
                showResult('❌ Please enter at least one valid ISBN', 'error');
                return;
            }

            showResult(`🔄 Processing ${isbns.length} books...`, 'loading');

            try {
                const response = await fetch('/add-books', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'batch_books',
                        isbns: isbns
                    })
                });

                const result = await response.json();
                
                if (result.success) {
                    let message = `✅ Successfully processed ${result.processed} out of ${result.total} books`;
                    if (result.errors && result.errors.length > 0) {
                        message += `\\n\\n❌ Errors:\\n${result.errors.join('\\n')}`;
                    }
                    showResult(message, result.errors.length > 0 ? 'error' : 'success');
                    document.getElementById('isbn-batch').value = '';
                } else {
                    showResult('❌ Error: ' + result.error, 'error');
                }
            } catch (error) {
                showResult('❌ Network error: ' + error.message, 'error');
            }
        }

        function isValidISBN(isbn) {
            const cleaned = isbn.replace(/[-\\s]/g, '');
            return /^\\d{10}$|^\\d{13}$/.test(cleaned);
        }

        function showResult(message, type) {
            const results = document.getElementById('results');
            results.innerHTML = `<div class="result ${type}">${message.replace(/\\n/g, '<br>')}</div>`;
        }

        function showBookResult(book) {
            const results = document.getElementById('results');
            const coverImg = book.cover_image ? 
                `<img src="${book.cover_image}" alt="Book cover" class="book-cover" onerror="this.style.display='none'">` : 
                '<div class="book-cover" style="background: #ddd; display: flex; align-items: center; justify-content: center; color: #666;">No Cover</div>';
            
            results.innerHTML = `
                <div class="result success">
                    <strong>✅ Successfully added to your Notion library!</strong>
                    <div class="book-preview">
                        ${coverImg}
                        <div class="book-info">
                            <h3>${book.title}</h3>
                            <p><strong>Author:</strong> ${book.author}</p>
                            <p><strong>ISBN:</strong> ${book.isbn}</p>
                            ${book.published_date ? `<p><strong>Published:</strong> ${book.published_date}</p>` : ''}
                            ${book.page_count ? `<p><strong>Pages:</strong> ${book.page_count}</p>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }

        // Clean up scanner when page unloads
        window.addEventListener('beforeunload', stopScanner);
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/add-book', methods=['POST'])
def add_single_book():
    """Handle single book addition"""
    try:
        data = request.get_json()
        isbn = data.get('isbn')
        
        if not isbn:
            return jsonify({'success': False, 'error': 'ISBN is required'}), 400
        
        result = process_single_book(isbn)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in add_single_book: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/add-books', methods=['POST'])
def add_batch_books():
    """Handle batch book addition"""
    try:
        data = request.get_json()
        isbns = data.get('isbns', [])
        
        if not isbns:
            return jsonify({'success': False, 'error': 'ISBN list is required'}), 400
        
        result = process_batch_books(isbns)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in add_batch_books: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

def process_single_book(isbn):
    """Process a single book by ISBN"""
    if not isbn:
        return {'success': False, 'error': 'ISBN is required'}
    
    # Clean ISBN
    isbn = isbn.replace('-', '').replace(' ', '').strip()
    
    # Validate ISBN
    if not (len(isbn) in [10, 13] and isbn.isdigit()):
        return {'success': False, 'error': 'Invalid ISBN format'}
    
    try:
        # Fetch book data
        book_data = fetch_book_from_google_books(isbn)
        
        if not book_data:
            return {'success': False, 'error': 'Book not found in Google Books'}
        
        # Add to Notion
        notion_response = add_book_to_notion(book_data)
        
        if notion_response:
            return {
                'success': True,
                'book': book_data,
                'notion_id': notion_response.get('id')
            }
        else:
            return {'success': False, 'error': 'Failed to add book to Notion'}
            
    except Exception as e:
        logger.error(f"Error processing book {isbn}: {str(e)}")
        return {'success': False, 'error': f'Processing error: {str(e)}'}

def process_batch_books(isbns):
    """Process multiple books by ISBN"""
    if not isbns or not isinstance(isbns, list):
        return {'success': False, 'error': 'ISBN list is required'}
    
    processed = 0
    errors = []
    
    for isbn in isbns:
        try:
            result = process_single_book(isbn)
            if result['success']:
                processed += 1
                logger.info(f"Successfully processed ISBN: {isbn}")
            else:
                errors.append(f"ISBN {isbn}: {result['error']}")
                logger.warning(f"Failed to process ISBN {isbn}: {result['error']}")
        except Exception as e:
            error_msg = f"ISBN {isbn}: {str(e)}"
            errors.append(error_msg)
            logger.error(f"Exception processing ISBN {isbn}: {str(e)}")
    
    return {
        'success': True,
        'processed': processed,
        'total': len(isbns),
        'errors': errors[:10]  # Limit errors shown to prevent huge responses
    }

def fetch_book_from_google_books(isbn):
    """Fetch book information from Google Books API"""
    try:
        base_url = "https://www.googleapis.com/books/v1/volumes"
        params = {'q': f'isbn:{isbn}'}
        
        if GOOGLE_BOOKS_API_KEY:
            params['key'] = GOOGLE_BOOKS_API_KEY
        
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('totalItems', 0) == 0:
            logger.warning(f"No book found for ISBN: {isbn}")
            return None
        
        # Extract book information
        book_info = data['items'][0]['volumeInfo']
        
        # Get publisher information
        publisher = book_info.get('publisher', '')
        
        # Get publish place (not always available from Google Books)
        # This field is rarely provided by Google Books API
        publish_place = book_info.get('publishedPlace', '')
        
        book_data = {
            'isbn': isbn,
            'title': book_info.get('title', 'Unknown Title'),
            'authors': book_info.get('authors', ['Unknown Author']),
            'author': ', '.join(book_info.get('authors', ['Unknown Author'])),
            'publisher': publisher,
            'published_date': book_info.get('publishedDate', ''),
            'description': book_info.get('description', ''),
            'page_count': book_info.get('pageCount'),
            'categories': book_info.get('categories', []),
            'language': book_info.get('language', 'en'),
            'publish_place': publish_place,
            'cover_image': None
        }
        
        # Get cover image
        image_links = book_info.get('imageLinks', {})
        if image_links:
            book_data['cover_image'] = (
                image_links.get('large') or 
                image_links.get('medium') or 
                image_links.get('small') or 
                image_links.get('thumbnail')
            )
            
        return book_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching book data for ISBN {isbn}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching book data for ISBN {isbn}: {str(e)}")
        return None data['items'][0]['volumeInfo']
        
        book_data = {
            'isbn': isbn,
            'title': book_info.get('title', 'Unknown Title'),
            'authors': book_info.get('authors', ['Unknown Author']),
            'author': ', '.join(book_info.get('authors', ['Unknown Author'])),
            'published_date': book_info.get('publishedDate', ''),
            'description': book_info.get('description', ''),
            'page_count': book_info.get('pageCount'),
            'categories': book_info.get('categories', []),
            'language': book_info.get('language', 'en'),
            'cover_image': None
        }
        
        # Get cover image
        image_links = book_info.get('imageLinks', {})
        if image_links:
            book_data['cover_image'] = (
                image_links.get('large') or 
                image_links.get('medium') or 
                image_links.get('small') or 
                image_links.get('thumbnail')
            )
            
        return book_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching book data for ISBN {isbn}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching book data for ISBN {isbn}: {str(e)}")
        return None

def add_book_to_notion(book_data):
    """Add book to Notion database with all specified columns"""
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        logger.error("Notion credentials not configured")
        return None
    
    try:
        url = "https://api.notion.com/v1/pages"
        
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Build properties for all your specified columns
        properties = {
            # BookName (using Title property type)
            "BookName": {
                "title": [{"text": {"content": book_data['title']}}]
            },
            
            # ISBN
            "ISBN": {
                "rich_text": [{"text": {"content": book_data['isbn']}}]
            },
            
            # Status (will be set to "New" by default)
            "Status": {
                "select": {"name": "New"}
            },
            
            # Author
            "Author": {
                "rich_text": [{"text": {"content": book_data['author']}}]
            },
            
            # Publisher
            "Publisher": {
                "rich_text": [{"text": {"content": book_data.get('publisher', '')}}]
            },
            
            # Published Date
            "Published Date": {},
            
            # Descriptions
            "Descriptions": {},
            
            # Page Count
            "Page Count": {},
            
            # Category
            "Category": {},
            
            # ReadStatus (default to "Want to Read")
            "ReadStatus": {
                "select": {"name": "Want to Read"}
            },
            
            # StartDate (empty by default)
            "StartDate": {"date": None},
            
            # FinishDate (empty by default) 
            "FinishDate": {"date": None},
            
            # Favorite (default to false)
            "Favorite": {"checkbox": False},
            
            # Currentpage (default to 0)
            "Currentpage": {"number": 0},
            
            # PublishPlace
            "PublishPlace": {
                "rich_text": [{"text": {"content": book_data.get('publish_place', '')}}]
            },
            
            # Language
            "Language": {
                "rich_text": [{"text": {"content": book_data.get('language', 'en')}}]
            },
            
            # MyRate (empty by default, user can fill in)
            "MyRate": {"number": None},
            
            # Cover image
            "Cover image": {},
            
            # AMZ-CoverImage (empty by default)
            "AMZ-CoverImage": {
                "rich_text": [{"text": {"content": ""}}]
            },
            
            # My Progress (default to 0%)
            "My Progress": {"number": 0},
            
            # ReadLog (empty by default for user notes)
            "ReadLog": {
                "rich_text": [{"text": {"content": ""}}]
            }
        }
        
        # Fill in the conditional fields
        
        # Published Date
        if book_data['published_date']:
            parsed_date = parse_date(book_data['published_date'])
            if parsed_date:
                properties["Published Date"] = {"date": {"start": parsed_date}}
            else:
                properties["Published Date"] = {"rich_text": [{"text": {"content": book_data['published_date']}}]}
        else:
            properties["Published Date"] = {"rich_text": [{"text": {"content": ""}}]}
        
        # Descriptions
        if book_data['description']:
            description = book_data['description'][:2000]  # Notion limit
            properties["Descriptions"] = {
                "rich_text": [{"text": {"content": description}}]
            }
        else:
            properties["Descriptions"] = {"rich_text": [{"text": {"content": ""}}]}
        
        # Page Count
        if book_data['page_count']:
            properties["Page Count"] = {"number": book_data['page_count']}
        else:
            properties["Page Count"] = {"number": None}
        
        # Category
        if book_data['categories']:
            # Join categories with commas
            category_text = ', '.join(book_data['categories'])
            properties["Category"] = {
                "rich_text": [{"text": {"content": category_text}}]
            }
        else:
            properties["Category"] = {"rich_text": [{"text": {"content": ""}}]}
        
        # Cover image
        if book_data['cover_image']:
            properties["Cover image"] = {"url": book_data['cover_image']}
        else:
            properties["Cover image"] = {"rich_text": [{"text": {"content": ""}}]}
        
        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": properties
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        logger.info(f"Successfully added book to Notion: {book_data['title']}")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error adding book to Notion: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error adding book to Notion: {str(e)}")
        return None

def parse_date(date_string):
    """Parse date from Google Books API"""
    try:
        formats = ['%Y-%m-%d', '%Y-%m', '%Y']
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    except Exception:
        return None

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)