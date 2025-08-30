import os
import json
import logging
import requests
from flask import Flask, request, render_template_string, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Environment variables
NOTION_TOKEN = os.environ.get('NOTION_TOKEN', '')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID', '')
GOOGLE_BOOKS_API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY', '')

# HTML template
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
            font-family: Arial, sans-serif;
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
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            border: 2px solid #f0f0f0;
            border-radius: 10px;
            background: #fafafa;
        }
        .section-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #444;
            margin-bottom: 15px;
        }
        .status {
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
            font-weight: bold;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .info {
            background-color: #cce7ff;
            color: #004085;
        }
        .loading {
            background-color: #fff3cd;
            color: #856404;
        }
        input, button {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 16px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .scan-button {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }
        .notion-button {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
        .book-preview {
            display: flex;
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .book-cover {
            width: 60px;
            height: 90px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Book Scanner</h1>
        
        <!-- ISBN Input Section -->
        <div class="section">
            <div class="section-title">📖 Add Book to Collection</div>
            <label for="isbn">ISBN Number:</label>
            <input type="text" id="isbn" placeholder="Enter ISBN or scan barcode below">
            <button onclick="scanBarcode()" class="scan-button">📷 Scan Barcode with Camera</button>
            <button onclick="lookupBook()">🔍 Look Up Book Details</button>
            <button onclick="addToNotion()" class="notion-button">📚 Add to Notion Library</button>
        </div>

        <!-- Barcode Scanner -->
        <div id="scanner-container">
            <div class="section-title">📷 Camera Scanner</div>
            <div id="scanner"></div>
            <button onclick="stopScanner()">❌ Stop Scanner</button>
        </div>
        
        <!-- Results -->
        <div id="results"></div>
    </div>

    <script>
        var scanner = null;
        
        function scanBarcode() {
            var container = document.getElementById('scanner-container');
            var scannerDiv = document.getElementById('scanner');
            
            container.style.display = 'block';
            scannerDiv.innerHTML = '';
            
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                showResult('📷 Starting camera...', 'loading');
                
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
                    showResult('📷 Camera ready! Point at a barcode.', 'info');
                });

                Quagga.onDetected(function(result) {
                    var isbn = result.codeResult.code;
                    document.getElementById('isbn').value = isbn;
                    stopScanner();
                    showResult('✅ Barcode detected: ' + isbn, 'success');
                    
                    setTimeout(function() {
                        lookupBook();
                    }, 1000);
                });
            } else {
                showResult('❌ Camera not supported. Please use manual entry.', 'error');
            }
        }

        function stopScanner() {
            if (typeof Quagga !== 'undefined' && Quagga.stop) {
                Quagga.stop();
            }
            document.getElementById('scanner-container').style.display = 'none';
        }

        function lookupBook() {
            var isbn = document.getElementById('isbn').value.trim();
            if (!isbn) {
                showResult('❌ Please enter an ISBN', 'error');
                return;
            }

            if (!isValidISBN(isbn)) {
                showResult('❌ Invalid ISBN format', 'error');
                return;
            }

            showResult('🔍 Looking up book...', 'loading');
            
            fetch('/test-isbn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({isbn: isbn})
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(result) {
                if (result.success) {
                    displayBook(result);
                } else {
                    showResult('❌ Error: ' + result.error, 'error');
                }
            })
            .catch(function(error) {
                showResult('❌ Network error: ' + error.message, 'error');
            });
        }

        function addToNotion() {
            var isbn = document.getElementById('isbn').value.trim();
            if (!isbn) {
                showResult('❌ Please enter an ISBN first', 'error');
                return;
            }

            if (!isValidISBN(isbn)) {
                showResult('❌ Invalid ISBN format', 'error');
                return;
            }

            showResult('📚 Adding to Notion...', 'loading');
            
            fetch('/test-isbn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    isbn: isbn,
                    save_to_notion: true
                })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(result) {
                if (result.success) {
                    if (result.saved_to_notion) {
                        displayBookWithNotion(result, true);
                    } else {
                        showResult('❌ Notion not configured or failed to save', 'error');
                    }
                } else {
                    showResult('❌ Error: ' + result.error, 'error');
                }
            })
            .catch(function(error) {
                showResult('❌ Network error: ' + error.message, 'error');
            });
        }

        function isValidISBN(isbn) {
            var cleaned = isbn.replace(/[-\\s]/g, '');
            return /^\\d{10}$|^\\d{13}$/.test(cleaned);
        }

        function showResult(message, type) {
            var results = document.getElementById('results');
            results.innerHTML = '<div class="status ' + type + '">' + message + '</div>';
        }

        function displayBook(book) {
            var results = document.getElementById('results');
            var coverImg = book.cover_image ? 
                '<img src="' + book.cover_image + '" alt="Cover" class="book-cover">' : 
                '<div class="book-cover" style="background: #ddd; display: flex; align-items: center; justify-content: center;">No Cover</div>';
            
            var html = '<div class="status success">' +
                '<strong>✅ Book Found!</strong>' +
                '<div class="book-preview">' +
                coverImg +
                '<div class="book-info">' +
                '<h3>' + book.title + '</h3>' +
                '<p><strong>Author:</strong> ' + book.author + '</p>' +
                '<p><strong>ISBN:</strong> ' + book.isbn + '</p>';
                
            if (book.publisher) {
                html += '<p><strong>Publisher:</strong> ' + book.publisher + '</p>';
            }
            if (book.published_date) {
                html += '<p><strong>Published:</strong> ' + book.published_date + '</p>';
            }
            if (book.page_count) {
                html += '<p><strong>Pages:</strong> ' + book.page_count + '</p>';
            }
            
            html += '</div></div></div>';
            
            results.innerHTML = html;
        }

        function displayBookWithNotion(book, saved) {
            var results = document.getElementById('results');
            var coverImg = book.cover_image ? 
                '<img src="' + book.cover_image + '" alt="Cover" class="book-cover">' : 
                '<div class="book-cover" style="background: #ddd;">No Cover</div>';
            
            var message = saved ? '✅ Successfully added to Notion!' : '❌ Failed to save to Notion';
            var statusClass = saved ? 'success' : 'error';
            
            var html = '<div class="status ' + statusClass + '">' +
                '<strong>' + message + '</strong>' +
                '<div class="book-preview">' +
                coverImg +
                '<div class="book-info">' +
                '<h3>' + book.title + '</h3>' +
                '<p><strong>Author:</strong> ' + book.author + '</p>' +
                '<p><strong>ISBN:</strong> ' + book.isbn + '</p>';
                
            if (book.publisher) {
                html += '<p><strong>Publisher:</strong> ' + book.publisher + '</p>';
            }
            
            html += '</div></div>';
            
            if (saved) {
                html += '<p>🎉 Check your Notion database!</p>';
            }
            
            html += '</div>';
            
            results.innerHTML = html;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Serve the main web interface"""
    return HTML_TEMPLATE

@app.route('/test-isbn', methods=['POST'])
def test_isbn():
    """Test Google Books API and optionally save to Notion"""
    try:
        data = request.get_json()
        isbn = data.get('isbn', '').strip()
        save_to_notion = data.get('save_to_notion', False)
        
        if not isbn:
            return jsonify({'success': False, 'error': 'ISBN required'})
        
        # Clean ISBN
        isbn = isbn.replace('-', '').replace(' ', '').strip()
        
        # Test Google Books API
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        if GOOGLE_BOOKS_API_KEY and GOOGLE_BOOKS_API_KEY not in ['', 'dummy_token']:
            url += f"&key={GOOGLE_BOOKS_API_KEY}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        api_data = response.json()
        
        if api_data.get('totalItems', 0) == 0:
            return jsonify({'success': False, 'error': 'Book not found'})
        
        book_info = api_data['items'][0]['volumeInfo']
        
        # Extract book information
        book_data = {
            'success': True,
            'isbn': isbn,
            'title': book_info.get('title', 'Unknown Title'),
            'author': ', '.join(book_info.get('authors', ['Unknown Author'])),
            'publisher': book_info.get('publisher', ''),
            'published_date': book_info.get('publishedDate', ''),
            'page_count': book_info.get('pageCount'),
            'categories': ', '.join(book_info.get('categories', [])),
            'description': book_info.get('description', '')[:200] + '...' if book_info.get('description', '') else '',
            'language': book_info.get('language', 'en'),
            'cover_image': None,
            'saved_to_notion': False
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
        
        # Save to Notion if requested
        if save_to_notion and is_notion_configured():
            notion_result = add_book_to_notion(book_data)
            if notion_result:
                book_data['saved_to_notion'] = True
                book_data['notion_id'] = notion_result.get('id')
        
        return jsonify(book_data)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def is_notion_configured():
    """Check if Notion is configured"""
    return (NOTION_TOKEN and NOTION_TOKEN not in ['', 'dummy_token'] and 
            NOTION_DATABASE_ID and NOTION_DATABASE_ID not in ['', 'dummy_database_id'])

def add_book_to_notion(book_data):
    """Add book to Notion database - minimal working version"""
    if not is_notion_configured():
        logger.error("Notion not configured")
        return None
    
    try:
        url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Go back to the minimal properties that worked before
        properties = {
            "BookName": {"title": [{"text": {"content": book_data['title']}}]},
            "ISBN": {"rich_text": [{"text": {"content": book_data['isbn']}}]},
            "Author": {"rich_text": [{"text": {"content": book_data['author']}}]}
        }
        
        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": properties
        }
        
        logger.info(f"Adding book with minimal properties: {book_data['title']}")
        logger.info(f"Database ID: {NOTION_DATABASE_ID}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Response status: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            
        response.raise_for_status()
        
        logger.info(f"Successfully added to Notion: {book_data['title']}")
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        logger.error(f"Response status: {e.response.status_code}")
        logger.error(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Notion error: {str(e)}")
        return None

def parse_date(date_string):
    """Parse date from Google Books"""
    try:
        from datetime import datetime
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

@app.route('/debug-notion')
def debug_notion():
    """Debug: Check Notion configuration and test simple API call"""
    try:
        result = {
            "token_configured": bool(NOTION_TOKEN and NOTION_TOKEN not in ['', 'dummy_token']),
            "database_configured": bool(NOTION_DATABASE_ID and NOTION_DATABASE_ID not in ['', 'dummy_database_id']),
            "token_starts_with": NOTION_TOKEN[:10] if NOTION_TOKEN else "None",
            "database_id": NOTION_DATABASE_ID if NOTION_DATABASE_ID else "None",
            "database_id_length": len(NOTION_DATABASE_ID) if NOTION_DATABASE_ID else 0
        }
        
        # Test simple database access
        if NOTION_TOKEN and NOTION_DATABASE_ID:
            headers = {
                "Authorization": f"Bearer {NOTION_TOKEN}",
                "Notion-Version": "2022-06-28"
            }
            
            try:
                # Try to get database info
                url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}"
                response = requests.get(url, headers=headers, timeout=10)
                
                result["api_test"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "error": response.json() if response.status_code != 200 else None
                }
                
                if response.status_code == 200:
                    db_info = response.json()
                    result["database_info"] = {
                        "title": db_info.get("title", [{}])[0].get("plain_text", "Unknown"),
                        "properties": list(db_info.get("properties", {}).keys())
                    }
                
            except Exception as e:
                result["api_test"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        })

@app.route('/debug-databases')
def debug_databases():
    """Debug: Test database access with different ID formats"""
    try:
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28"
        }
        
        # Test different possible ID formats
        test_ids = [
            "25e000024da7805f9506d68b013290da",  # Original
            "25e00002-4da7-805f-9506-d68b013290da",  # From error message
            "25e00002-4da7-805f-9506-d68b013290da"  # Alternative format
        ]
        
        results = {}
        
        for test_id in test_ids:
            try:
                url = f"https://api.notion.com/v1/databases/{test_id}"
                response = requests.get(url, headers=headers, timeout=10)
                
                results[test_id] = {
                    "status_code": response.status_code,
                    "accessible": response.status_code == 200,
                    "error": response.json() if response.status_code != 200 else "Success"
                }
                
            except Exception as e:
                results[test_id] = {
                    "status_code": "error",
                    "accessible": False,
                    "error": str(e)
                }
        
        return jsonify({
            "status": "testing_complete",
            "token_configured": bool(NOTION_TOKEN and NOTION_TOKEN != 'dummy_token'),
            "test_results": results,
            "current_database_id": NOTION_DATABASE_ID
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e),
            "token_configured": bool(NOTION_TOKEN and NOTION_TOKEN != 'dummy_token')
        })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)