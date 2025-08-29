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

# Simple HTML template for testing
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 Book Scanner - Test Version</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
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
        input, button {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
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
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Book Scanner</h1>
        
        <div class="status info">
            <strong>Status:</strong> Basic version running successfully! ✅
        </div>
        
        <div class="status info">
            <strong>Configuration:</strong><br>
            Notion Token: {{ 'Set' if notion_token else 'Not Set' }}<br>
            Database ID: {{ 'Set' if database_id else 'Not Set' }}<br>
            Google Books API: {{ 'Set' if api_key else 'Not Set' }}
        </div>
        
        <div>
            <label for="isbn">Test ISBN Lookup:</label>
            <input type="text" id="isbn" placeholder="Enter ISBN (e.g., 9780545010221)">
            <button onclick="testISBN()">Test Google Books API</button>
        </div>
        
        <div id="results"></div>
    </div>

    <script>
        async function testISBN() {
            const isbn = document.getElementById('isbn').value.trim();
            if (!isbn) {
                showResult('Please enter an ISBN', 'error');
                return;
            }
            
            showResult('Testing Google Books API...', 'info');
            
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
                    showResult(`Found book: ${result.title} by ${result.author}`, 'success');
                } else {
                    showResult('Error: ' + result.error, 'error');
                }
            } catch (error) {
                showResult('Network error: ' + error.message, 'error');
            }
        }
        
        function showResult(message, type) {
            const results = document.getElementById('results');
            results.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
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
    """Test Google Books API"""
    try:
        data = request.get_json()
        isbn = data.get('isbn', '').strip()
        
        if not isbn:
            return jsonify({'success': False, 'error': 'ISBN required'})
        
        # Test Google Books API
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        if GOOGLE_BOOKS_API_KEY and GOOGLE_BOOKS_API_KEY != 'dummy_token':
            url += f"&key={GOOGLE_BOOKS_API_KEY}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('totalItems', 0) == 0:
            return jsonify({'success': False, 'error': 'Book not found'})
        
        book_info = data['items'][0]['volumeInfo']
        
        return jsonify({
            'success': True,
            'title': book_info.get('title', 'Unknown'),
            'author': ', '.join(book_info.get('authors', ['Unknown'])),
            'isbn': isbn
        })
        
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
