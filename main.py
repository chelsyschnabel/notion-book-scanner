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

# HTML template with barcode scanning
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 Book Scanner with Barcode</title>
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
        .test-button {
            background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
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
        
        <!-- Status Section -->
        <div class="section">
            <div class="section-title">🔧 System Status</div>
            <div class="status info">
                <strong>Configuration:</strong><br>
                Notion Token: {{ 'Set' if notion_token else 'Not Set' }}<br>
                Database ID: {{ 'Set' if database_id else 'Not Set' }}<br>
                Google Books API: {{ 'Set' if api_key else 'Not Set' }}
            </div>
        </div>
        
        <!-- ISBN Input Section -->
        <div class="section">
            <div class="section-title">📖 Add Book to Collection</div>
            <label for="isbn">ISBN Number:</label>
            <input type="text" id="isbn" placeholder="Enter ISBN or scan barcode below">
            <button onclick="scanBarcode()" class="scan-button">📷 Scan Barcode with Camera</button>
            <button onclick="lookupBook()" class="test-button">🔍 Look Up Book Details</button>
        </div>

        <!-- Barcode Scanner -->
        <div id="scanner-container">
            <div class="section-title">📷 Camera Scanner</div>
            <div id="scanner"></div>
            <button onclick="stopScanner()" class="error">❌ Stop Scanner</button>
        </div>
        
        <!-- Results -->
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
                        showResult('❌ Error starting camera: ' + err.message + '. Please try manual entry instead.', 'error');
                        container.style.display = 'none';
                        return;
                    }
                    Quagga.start();
                    showResult('📷 Camera ready! Point at a barcode on a book.', 'info');
                });

                Quagga.onDetected(function(result) {
                    const isbn = result.codeResult.code;
                    document.getElementById('isbn').value = isbn;
                    stopScanner();
                    showResult('✅ Barcode detected: ' + isbn, 'success');
                    
                    // Automatically look up the book
                    setTimeout(() => {
                        lookupBook();
                    }, 1000);
                });
            } else {
                showResult('❌ Camera not supported in this browser. Please use manual ISBN entry.', 'error');
            }
        }

        function stopScanner() {
            if (Quagga && typeof Quagga.stop === 'function') {
                Quagga.stop();
            }
            document.getElementById('scanner-container').style.display = 'none';
            showResult('📷 Scanner stopped.', 'info');
        }

        async function lookupBook() {
            const isbn = document.getElementById('isbn').value.trim();
            if (!isbn) {
                showResult('❌ Please enter an ISBN or scan a barcode', 'error');
                return;
            }

            if (!isValidISBN(isbn)) {
                showResult('❌ Invalid ISBN format. Please enter 10 or 13 digits.', 'error');
                return;
            }

            showResult('🔍 Looking up book details...', 'loading');
            
            try {
                const response = await fetch('/test-isbn', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({isbn: isbn})
                });

                const result = await response.json();
                
                if (result.success) {
                    showBookResult(result);
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
            results.innerHTML = `<div class="status ${type}">${message}</div>`;
        }

        function showBookResult(book) {
            const results = document.getElementById('results');
            const coverImg = book.cover_image ? 
                `<img src="${book.cover_image}" alt="Book cover" class="book-cover" onerror="this.style.display='none'">` : 
                '<div class="book-cover" style="background: #ddd; display: flex; align-items: center; justify-content: center; color: #666; font-size: 12px;">No Cover</div>';
            
            results.innerHTML = `
                <div class="status success">
                    <strong>✅ Book found!</strong>
                    <div class="book-preview">
                        ${coverImg}
                        <div class="book-info">
                            <h3>${book.title}</h3>
                            <p><strong>Author:</strong> ${book.author}</p>
                            <p><strong>ISBN:</strong> ${book.isbn}</p>
                            ${book.publisher ? `<p><strong>Publisher:</strong> ${book.publisher}</p>` : ''}
                            ${book.published_date ? `<p><strong>Published:</strong> ${book.published_date}</p>` : ''}
                            ${book.page_count ? `<p><strong>Pages:</strong> ${book.page_count}</p>` : ''}
                        </div>
                    </div>
                    <em>📝 Ready to add Notion integration next!</em>
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
    return render_template_string(
        HTML_TEMPLATE,
        notion_token=bool(NOTION_TOKEN and NOTION_TOKEN != 'dummy_token'),
        database_id=bool(NOTION_DATABASE_ID and NOTION_DATABASE_ID != 'dummy_database_id'),
        api_key=bool(GOOGLE_BOOKS_API_KEY)
    )

@app.route('/test-isbn', methods=['POST'])
def test_isbn():
    """Test Google Books API and return detailed book info"""
    try:
        data = request.get_json()
        isbn = data.get('isbn', '').strip()
        
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
            return jsonify({'success': False, 'error': 'Book not found in Google Books'})
        
        book_info = api_data['items'][0]['volumeInfo']
        
        # Extract detailed book information
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
        
        return jsonify(book_data)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching book data: {str(e)}")
        return jsonify({'success': False, 'error': f'Google Books API error: {str(e)}'})
    except Exception as e:
        logger.error(f"Error testing ISBN: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'notion_configured': bool(NOTION_TOKEN and NOTION_TOKEN != 'dummy_token'),
        'database_configured': bool(NOTION_DATABASE_ID and NOTION_DATABASE_ID != 'dummy_database_id')
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
