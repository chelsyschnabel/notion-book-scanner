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

# HTML template with Figma-inspired design
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Scanner</title>
    <script src="https://cdn.jsdelivr.net/npm/quagga@0.12.1/dist/quagga.min.js"></script>
    <style>
        :root {
            --font-size: 14px;
            --background: #ffffff;
            --foreground: oklch(0.145 0 0);
            --card: #ffffff;
            --card-foreground: oklch(0.145 0 0);
            --primary: #030213;
            --primary-foreground: oklch(1 0 0);
            --secondary: oklch(0.95 0.0058 264.53);
            --secondary-foreground: #030213;
            --muted: #ececf0;
            --muted-foreground: #717182;
            --accent: #e9ebef;
            --accent-foreground: #030213;
            --destructive: #d4183d;
            --destructive-foreground: #ffffff;
            --border: rgba(0, 0, 0, 0.1);
            --input-background: #f3f3f5;
            --font-weight-medium: 500;
            --font-weight-normal: 400;
            --radius: 0.625rem;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: var(--font-size);
            background-color: var(--background);
            color: var(--foreground);
            line-height: 1.5;
            min-height: 100vh;
            padding: 1rem;
        }

        .container {
            max-width: 28rem;
            margin: 0 auto;
            space-y: 1.5rem;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .header-icon {
            width: 3rem;
            height: 3rem;
            margin: 0 auto 1rem;
            background: var(--primary);
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary-foreground);
        }

        h1 {
            font-size: 1.5rem;
            font-weight: var(--font-weight-medium);
            margin-bottom: 0.5rem;
        }

        .subtitle {
            color: var(--muted-foreground);
            font-size: 0.875rem;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }

        .card:hover {
            background: var(--accent);
        }

        .card-content {
            padding: 1.5rem;
        }

        .option-card {
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .option-icon {
            width: 3rem;
            height: 3rem;
            background: oklch(0.95 0.02 264.53);
            border-radius: var(--radius);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
            flex-shrink: 0;
        }

        .option-content h3 {
            font-weight: var(--font-weight-medium);
            margin-bottom: 0.25rem;
        }

        .option-content p {
            color: var(--muted-foreground);
            font-size: 0.875rem;
        }

        .scanner-section {
            margin: 2rem 0;
        }

        .scanner-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .back-button {
            width: 2rem;
            height: 2rem;
            background: none;
            border: none;
            border-radius: 0.375rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--muted-foreground);
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .back-button:hover {
            background: var(--muted);
        }

        .scanner-title {
            font-size: 1.25rem;
            font-weight: var(--font-weight-medium);
        }

        .input-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            font-weight: var(--font-weight-medium);
            margin-bottom: 0.5rem;
            color: var(--foreground);
        }

        input[type="text"] {
            width: 100%;
            padding: 0.75rem;
            background: var(--input-background);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            font-size: inherit;
            transition: all 0.2s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: var(--primary);
            background: var(--background);
        }

        .button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: var(--primary);
            color: var(--primary-foreground);
            border: none;
            border-radius: var(--radius);
            font-weight: var(--font-weight-medium);
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
            margin-bottom: 0.75rem;
        }

        .button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }

        .button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .button-secondary {
            background: var(--secondary);
            color: var(--secondary-foreground);
        }

        .button-outline {
            background: transparent;
            color: var(--primary);
            border: 1px solid var(--border);
        }

        #scanner-container {
            display: none;
            margin: 1.5rem 0;
        }

        #scanner {
            width: 100%;
            max-width: 400px;
            aspect-ratio: 4/3;
            border-radius: var(--radius);
            overflow: hidden;
            border: 1px solid var(--border);
        }

        .scanner-overlay {
            position: relative;
            aspect-ratio: 4/3;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: var(--radius);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            border: 1px solid var(--border);
        }

        .scanner-frame {
            width: 12rem;
            height: 8rem;
            border: 2px dashed var(--primary);
            border-radius: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .scanner-icon {
            width: 2rem;
            height: 2rem;
            color: var(--primary);
        }

        .scanner-progress {
            width: 12rem;
            height: 0.5rem;
            background: var(--muted);
            border-radius: 0.25rem;
            overflow: hidden;
        }

        .scanner-progress-bar {
            height: 100%;
            background: var(--primary);
            transition: width 0.2s;
            border-radius: 0.25rem;
        }

        .result {
            padding: 1rem;
            border-radius: var(--radius);
            margin: 1rem 0;
        }

        .result-success {
            background: #d1f7c4;
            color: #15803d;
            border: 1px solid #bbf7d0;
        }

        .result-error {
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }

        .result-loading {
            background: #fef3c7;
            color: #d97706;
            border: 1px solid #fed7aa;
        }

        .book-preview {
            display: flex;
            gap: 1rem;
            margin: 1rem 0;
            padding: 1rem;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
        }

        .book-cover {
            width: 4rem;
            height: 6rem;
            background: var(--muted);
            border-radius: 0.375rem;
            object-fit: cover;
            flex-shrink: 0;
        }

        .book-cover-placeholder {
            width: 4rem;
            height: 6rem;
            background: var(--muted);
            border-radius: 0.375rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--muted-foreground);
            font-size: 0.75rem;
            text-align: center;
        }

        .book-info h3 {
            font-weight: var(--font-weight-medium);
            margin-bottom: 0.25rem;
            line-height: 1.4;
        }

        .book-info p {
            color: var(--muted-foreground);
            font-size: 0.875rem;
            margin-bottom: 0.25rem;
        }

        .animate-pulse {
            animation: pulse 1s ease-in-out infinite;
        }

        .animate-spin {
            animation: spin 1s linear infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        @media (max-width: 640px) {
            body {
                padding: 0.75rem;
            }
            
            .card-content {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Home View -->
        <div id="home-view">
            <div class="header">
                <div class="header-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                    </svg>
                </div>
                <h1>Book Scanner</h1>
                <p class="subtitle">Scan barcodes or enter ISBN to add books to your library</p>
            </div>

            <div class="card" onclick="showScanner()">
                <div class="card-content">
                    <div class="option-card">
                        <div class="option-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path>
                                <circle cx="12" cy="13" r="3"></circle>
                            </svg>
                        </div>
                        <div class="option-content">
                            <h3>Scan Barcode</h3>
                            <p>Use your camera to scan book barcodes</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card" onclick="showManualEntry()">
                <div class="card-content">
                    <div class="option-card">
                        <div class="option-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                                <line x1="8" y1="21" x2="16" y2="21"></line>
                                <line x1="12" y1="17" x2="12" y2="21"></line>
                            </svg>
                        </div>
                        <div class="option-content">
                            <h3>Enter ISBN</h3>
                            <p>Manually type in the book's ISBN number</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Scanner View -->
        <div id="scanner-view" style="display: none;">
            <div class="scanner-header">
                <button class="back-button" onclick="showHome()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="m12 19-7-7 7-7"></path>
                        <path d="M19 12H5"></path>
                    </svg>
                </button>
                <h2 class="scanner-title">Scan Barcode</h2>
            </div>

            <div class="card">
                <div class="card-content">
                    <div class="scanner-overlay">
                        <div class="scanner-frame">
                            <svg class="scanner-icon animate-pulse" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 7V5a2 2 0 0 1 2-2h2"></path>
                                <path d="M17 3h2a2 2 0 0 1 2 2v2"></path>
                                <path d="M21 17v2a2 2 0 0 1-2 2h-2"></path>
                                <path d="M7 21H5a2 2 0 0 1-2-2v-2"></path>
                            </svg>
                        </div>
                        
                        <div id="scanner-progress" style="display: none;">
                            <div class="scanner-progress">
                                <div id="progress-bar" class="scanner-progress-bar" style="width: 0%"></div>
                            </div>
                        </div>
                        
                        <p id="scanner-status">Position barcode within the frame</p>
                    </div>
                </div>
            </div>

            <div id="scanner-container"></div>

            <button class="button" onclick="startScanning()" id="scan-button">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path>
                    <circle cx="12" cy="13" r="3"></circle>
                </svg>
                Start Scanning
            </button>

            <p style="text-align: center; color: var(--muted-foreground); font-size: 0.875rem;">
                Point your camera at the book's barcode
            </p>
        </div>

        <!-- Manual Book Entry View -->
        <div id="manual-book-view" style="display: none;">
            <div class="scanner-header">
                <button class="back-button" onclick="showHome()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="m12 19-7-7 7-7"></path>
                        <path d="M19 12H5"></path>
                    </svg>
                </button>
                <h2 class="scanner-title">Add Book Manually</h2>
            </div>

            <div class="card">
                <div class="card-content">
                    <div class="input-group">
                        <label for="manual-title">Book Title *</label>
                        <input type="text" id="manual-title" placeholder="Enter book title">
                    </div>
                    
                    <div class="input-group">
                        <label for="manual-author">Author *</label>
                        <input type="text" id="manual-author" placeholder="Enter author name">
                    </div>
                    
                    <div class="input-group">
                        <label for="manual-isbn">ISBN</label>
                        <input type="text" id="manual-isbn" placeholder="Enter ISBN (optional)">
                    </div>
                    
                    <div class="input-group">
                        <label for="manual-publisher">Publisher</label>
                        <input type="text" id="manual-publisher" placeholder="Enter publisher">
                    </div>
                    
                    <div class="input-group">
                        <label for="manual-pages">Number of Pages</label>
                        <input type="number" id="manual-pages" placeholder="Enter page count">
                    </div>
                    
                    <div class="input-group">
                        <label for="manual-year">Publication Year</label>
                        <input type="number" id="manual-year" placeholder="Enter year (e.g., 2023)">
                    </div>
                    
                    <div class="input-group">
                        <label for="manual-description">Description</label>
                        <textarea id="manual-description" placeholder="Enter book description" rows="3" style="width: 100%; padding: 0.75rem; background: var(--input-background); border: 1px solid var(--border); border-radius: var(--radius); font-size: inherit; resize: vertical; font-family: inherit;"></textarea>
                    </div>
                    
                    <button class="button" onclick="saveManualBook()" id="save-manual-button">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                            <polyline points="17,21 17,13 7,13 7,21"></polyline>
                            <polyline points="7,3 7,8 15,8"></polyline>
                        </svg>
                        Add Book to Notion
                    </button>
                </div>
            </div>

            <div style="text-align: center; color: var(--muted-foreground); font-size: 0.875rem;">
                * Required fields
            </div>
        </div>

        <!-- Manual Entry View -->
        <div id="manual-view" style="display: none;">
            <div class="scanner-header">
                <button class="back-button" onclick="showHome()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="m12 19-7-7 7-7"></path>
                        <path d="M19 12H5"></path>
                    </svg>
                </button>
                <h2 class="scanner-title">Enter ISBN</h2>
            </div>

            <div class="card">
                <div class="card-content">
                    <div class="input-group">
                        <label for="isbn-input">ISBN Number</label>
                        <input type="text" id="isbn-input" placeholder="Enter ISBN (10 or 13 digits)">
                    </div>
                    
                    <button class="button" onclick="lookupBook()" id="lookup-button">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="11" cy="11" r="8"></circle>
                            <path d="m21 21-4.35-4.35"></path>
                        </svg>
                        Look Up Book
                    </button>

                    <button class="button" onclick="addToNotion()" id="add-notion-button" style="display: none;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 5v14"></path>
                            <path d="M5 12h14"></path>
                        </svg>
                        Add to Notion Library
                    </button>
                </div>
            </div>

            <div style="text-align: center; color: var(--muted-foreground); font-size: 0.875rem;">
                Enter the 10 or 13-digit ISBN found on the book
            </div>
        </div>

        <!-- Results -->
        <div id="results"></div>
    </div>

    <script>
        var scanner = null;
        var currentBook = null;

        function showHome() {
            document.getElementById('home-view').style.display = 'block';
            document.getElementById('scanner-view').style.display = 'none';
            document.getElementById('manual-view').style.display = 'none';
            document.getElementById('manual-book-view').style.display = 'none';
            stopScanner();
            clearResults();
        }

        function showScanner() {
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('scanner-view').style.display = 'block';
            document.getElementById('manual-view').style.display = 'none';
            document.getElementById('manual-book-view').style.display = 'none';
            clearResults();
        }

        function showManualEntry() {
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('scanner-view').style.display = 'none';
            document.getElementById('manual-view').style.display = 'block';
            document.getElementById('manual-book-view').style.display = 'none';
            clearResults();
        }

        function showManualBookEntry() {
            document.getElementById('home-view').style.display = 'none';
            document.getElementById('scanner-view').style.display = 'none';
            document.getElementById('manual-view').style.display = 'none';
            document.getElementById('manual-book-view').style.display = 'block';
            clearResults();
        }

        function clearResults() {
            document.getElementById('results').innerHTML = '';
            currentBook = null;
            document.getElementById('add-notion-button').style.display = 'none';
        }

        function startScanning() {
            var container = document.getElementById('scanner-container');
            var scanButton = document.getElementById('scan-button');
            var status = document.getElementById('scanner-status');
            var progress = document.getElementById('scanner-progress');

            container.style.display = 'block';
            progress.style.display = 'block';
            scanButton.disabled = true;
            scanButton.innerHTML = '<svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>Starting...';
            status.textContent = 'Starting camera...';

            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                Quagga.init({
                    inputStream: {
                        name: "Live",
                        type: "LiveStream",
                        target: container,
                        constraints: {
                            width: 400,
                            height: 300,
                            facingMode: "environment"
                        },
                    },
                    decoder: {
                        readers: ["ean_reader", "ean_8_reader", "code_128_reader", "code_39_reader"]
                    },
                }, function(err) {
                    if (err) {
                        showResult('Camera error: ' + err.message + '. Please try manual entry.', 'error');
                        resetScanButton();
                        return;
                    }
                    Quagga.start();
                    status.textContent = 'Camera ready! Point at a barcode.';
                    simulateProgress();
                });

                Quagga.onDetected(function(result) {
                    var isbn = result.codeResult.code;
                    document.getElementById('isbn-input').value = isbn;
                    stopScanner();
                    showResult('Barcode detected: ' + isbn, 'success');
                    setTimeout(function() {
                        lookupBookByISBN(isbn);
                    }, 1000);
                });
            } else {
                showResult('Camera not supported. Please use manual entry.', 'error');
                resetScanButton();
            }
        }

        function simulateProgress() {
            var progressBar = document.getElementById('progress-bar');
            var width = 0;
            var interval = setInterval(function() {
                if (width >= 100) {
                    clearInterval(interval);
                    return;
                }
                width += Math.random() * 10;
                if (width > 100) width = 100;
                progressBar.style.width = width + '%';
            }, 200);
        }

        function stopScanner() {
            if (typeof Quagga !== 'undefined' && Quagga.stop) {
                Quagga.stop();
            }
            document.getElementById('scanner-container').style.display = 'none';
            document.getElementById('scanner-progress').style.display = 'none';
            resetScanButton();
        }

        function resetScanButton() {
            var scanButton = document.getElementById('scan-button');
            scanButton.disabled = false;
            scanButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"></path><circle cx="12" cy="13" r="3"></circle></svg>Start Scanning';
            document.getElementById('scanner-status').textContent = 'Position barcode within the frame';
        }

        function lookupBook() {
            var isbn = document.getElementById('isbn-input').value.trim();
            if (!isbn) {
                showResult('Please enter an ISBN', 'error');
                return;
            }

            if (!isValidISBN(isbn)) {
                showResult('Invalid ISBN format. Please enter 10 or 13 digits.', 'error');
                return;
            }

            lookupBookByISBN(isbn);
        }

        function lookupBookByISBN(isbn) {
            var lookupButton = document.getElementById('lookup-button');
            lookupButton.disabled = true;
            lookupButton.innerHTML = '<svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>Looking up...';
            
            showResult('Looking up book details...', 'loading');
            
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
                lookupButton.disabled = false;
                lookupButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>Look Up Book';
                
                if (result.success) {
                    currentBook = result;
                    displayBookWithActions(result);
                } else {
                    showBookNotFoundOptions(isbn);
                }
            })
            .catch(function(error) {
                lookupButton.disabled = false;
                lookupButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg>Look Up Book';
                showResult('Network error: ' + error.message, 'error');
            });
        }

        function showBookNotFoundOptions(isbn) {
            var html = '<div class="result result-error">' +
                '<strong>Book Not Found</strong>' +
                '<p>We couldn\'t find this book in our database. You have two options:</p>' +
                '<div style="margin-top: 1rem;">' +
                '<button class="button" onclick="showManualBookEntry(); document.getElementById(\'manual-isbn\').value=\'' + isbn + '\';">' +
                '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
                '<path d="M12 5v14"></path><path d="M5 12h14"></path>' +
                '</svg>Add Book Details Manually</button>' +
                '<button class="button button-outline" onclick="document.getElementById(\'isbn-input\').value=\'\'; clearResults();">' +
                '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
                '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path>' +
                '<path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path>' +
                '</svg>Try Different ISBN</button>' +
                '</div>' +
                '</div>';
            
            document.getElementById('results').innerHTML = html;
        }

        function displayBookWithActions(book) {
            var results = document.getElementById('results');
            var coverImg = book.cover_image ? 
                '<img src="' + book.cover_image + '" alt="Cover" class="book-cover">' : 
                '<div class="book-cover-placeholder">No Cover</div>';
            
            var html = '<div class="result result-success">' +
                '<strong>Book Found!</strong>' +
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
            
            html += '</div></div>' +
                '<button class="button" onclick="addToNotionDirect()" id="direct-notion-button" style="margin-top: 1rem;">' +
                '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
                '<path d="M12 5v14"></path><path d="M5 12h14"></path>' +
                '</svg>Add to Notion Library</button>' +
                '</div>';
            
            results.innerHTML = html;
        }

        function addToNotionDirect() {
            if (!currentBook) {
                showResult('No book selected', 'error');
                return;
            }

            var addButton = document.getElementById('direct-notion-button');
            addButton.disabled = true;
            addButton.innerHTML = '<svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>Adding to Notion...';

            fetch('/test-isbn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    isbn: currentBook.isbn,
                    save_to_notion: true
                })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(result) {
                if (result.success && result.saved_to_notion) {
                    addButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"></path></svg>Successfully Added!';
                    addButton.style.background = '#22c55e';
                    
                    // Show success message after a delay
                    setTimeout(function() {
                        displayBookWithNotion(result, true);
                    }, 1000);
                } else {
                    showResult('Failed to add to Notion. Please check your configuration.', 'error');
                    addButton.disabled = false;
                    addButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>Add to Notion Library';
                }
            })
            .catch(function(error) {
                showResult('Network error: ' + error.message, 'error');
                addButton.disabled = false;
                addButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>Add to Notion Library';
            });
        }

        function saveManualBook() {
            var title = document.getElementById('manual-title').value.trim();
            var author = document.getElementById('manual-author').value.trim();
            var isbn = document.getElementById('manual-isbn').value.trim();
            var publisher = document.getElementById('manual-publisher').value.trim();
            var pages = document.getElementById('manual-pages').value.trim();
            var year = document.getElementById('manual-year').value.trim();
            var description = document.getElementById('manual-description').value.trim();

            if (!title || !author) {
                showResult('Please fill in the required fields (Title and Author)', 'error');
                return;
            }

            var publishedDate = year ? year + '-01-01' : '';
            
            var manualBook = {
                isbn: isbn || 'manual-' + Date.now(),
                title: title,
                author: author,
                publisher: publisher,
                published_date: publishedDate,
                page_count: pages ? parseInt(pages) : null,
                categories: '',
                description: description,
                cover_image: null,
                success: true
            };

            var saveButton = document.getElementById('save-manual-button');
            saveButton.disabled = true;
            saveButton.innerHTML = '<svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>Adding to Notion...';

            // Send to Notion directly
            fetch('/manual-book', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(manualBook)
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(result) {
                if (result.success) {
                    saveButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"></path></svg>Successfully Added!';
                    saveButton.style.background = '#22c55e';
                    
                    showResult('Book successfully added to your Notion library!', 'success');
                    
                    // Clear form after success
                    setTimeout(function() {
                        clearManualForm();
                        showHome();
                    }, 2000);
                } else {
                    showResult('Failed to add book to Notion: ' + (result.error || 'Unknown error'), 'error');
                    saveButton.disabled = false;
                    saveButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17,21 17,13 7,13 7,21"></polyline><polyline points="7,3 7,8 15,8"></polyline></svg>Add Book to Notion';
                }
            })
            .catch(function(error) {
                showResult('Network error: ' + error.message, 'error');
                saveButton.disabled = false;
                saveButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17,21 17,13 7,13 7,21"></polyline><polyline points="7,3 7,8 15,8"></polyline></svg>Add Book to Notion';
            });
        }

        function clearManualForm() {
            document.getElementById('manual-title').value = '';
            document.getElementById('manual-author').value = '';
            document.getElementById('manual-isbn').value = '';
            document.getElementById('manual-publisher').value = '';
            document.getElementById('manual-pages').value = '';
            document.getElementById('manual-year').value = '';
            document.getElementById('manual-description').value = '';
        }

        function addToNotion() {
            if (!currentBook) {
                showResult('No book selected', 'error');
                return;
            }

            var addButton = document.getElementById('add-notion-button');
            addButton.disabled = true;
            addButton.innerHTML = '<svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 11-6.219-8.56"/></svg>Adding to Notion...';

            fetch('/test-isbn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    isbn: currentBook.isbn,
                    save_to_notion: true
                })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(result) {
                if (result.success && result.saved_to_notion) {
                    displayBookWithNotion(result, true);
                    addButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"></path></svg>Added to Notion!';
                } else {
                    showResult('Failed to add to Notion. Please check your configuration.', 'error');
                    addButton.disabled = false;
                    addButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>Add to Notion Library';
                }
            })
            .catch(function(error) {
                showResult('Network error: ' + error.message, 'error');
                addButton.disabled = false;
                addButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>Add to Notion Library';
            });
        }

        function isValidISBN(isbn) {
            var cleaned = isbn.replace(/[-\\s]/g, '');
            return /^\\d{10}$|^\\d{13}$/.test(cleaned);
        }

        function showResult(message, type) {
            var results = document.getElementById('results');
            var className = 'result result-' + type;
            results.innerHTML = '<div class="' + className + '">' + message + '</div>';
        }

        function displayBook(book) {
            var results = document.getElementById('results');
            var coverImg = book.cover_image ? 
                '<img src="' + book.cover_image + '" alt="Cover" class="book-cover">' : 
                '<div class="book-cover-placeholder">No Cover</div>';
            
            var html = '<div class="result result-success">' +
                '<strong>Book Found!</strong>' +
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
                '<div class="book-cover-placeholder">No Cover</div>';
            
            var message = saved ? 'Successfully added to your Notion library!' : 'Failed to save to Notion';
            var statusClass = saved ? 'success' : 'error';
            
            var html = '<div class="result result-' + statusClass + '">' +
                '<strong>' + message + '</strong>' +
                '<div class="book-preview">' +
                coverImg +
                '<div class="book-info">' +
                '<h3>' + book.title + '</h3>' +
                '<p><strong>Author:</strong> ' + book.author + '</p>';
                
            if (book.publisher) {
                html += '<p><strong>Publisher:</strong> ' + book.publisher + '</p>';
            }
            
            html += '</div></div>';
            
            if (saved) {
                html += '<p style="margin-top: 1rem; text-align: center; color: var(--muted-foreground); font-size: 0.875rem;">Check your Notion database to see the book!</p>';
            }
            
            html += '</div>';
            
            results.innerHTML = html;
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
    """Add book to Notion database - working version with all columns"""
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
        
        # Core automatic data from Google Books API
        properties = {
            "BookName": {"title": [{"text": {"content": book_data['title']}}]},
            "ISBN": {"rich_text": [{"text": {"content": book_data['isbn']}}]},
            "Author": {"rich_text": [{"text": {"content": book_data['author']}}]}
        }
        
        # Add Publisher (automatic)
        if book_data.get('publisher'):
            properties["Publisher"] = {"rich_text": [{"text": {"content": book_data['publisher']}}]}
        
        # Add Page Count (automatic)
        if book_data.get('page_count'):
            properties["Page Count"] = {"number": book_data['page_count']}
        
        # Add Cover image (automatic)
        if book_data.get('cover_image'):
            properties["Cover image"] = {"url": book_data['cover_image']}
        
        # Add Published Date (automatic)
        if book_data.get('published_date'):
            parsed_date = parse_date(book_data['published_date'])
            if parsed_date:
                properties["Published Date"] = {"date": {"start": parsed_date}}
        
        # Add Descriptions (automatic)
        if book_data.get('description'):
            properties["Descriptions"] = {"rich_text": [{"text": {"content": book_data['description']}}]}
        
        # Add Category (automatic)
        if book_data.get('categories'):
            properties["Category"] = {"rich_text": [{"text": {"content": book_data['categories']}}]}
        
        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": properties
        }
        
        logger.info(f"Adding book with all properties: {book_data['title']}")
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

@app.route('/manual-book', methods=['POST'])
def manual_book():
    """Handle manually entered book data and save to Notion"""
    try:
        data = request.get_json()
        
        if not data.get('title') or not data.get('author'):
            return jsonify({'success': False, 'error': 'Title and author are required'})
        
        if not is_notion_configured():
            return jsonify({'success': False, 'error': 'Notion is not configured'})
        
        # Save manual book to Notion
        notion_result = add_book_to_notion(data)
        
        if notion_result:
            return jsonify({
                'success': True,
                'notion_id': notion_result.get('id')
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save book to Notion'})
            
    except Exception as e:
        logger.error(f"Error saving manual book: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
