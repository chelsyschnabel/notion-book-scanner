# 📚 Book Scanner & Notion Library Manager

A modern web application that allows you to scan book barcodes or enter ISBNs to automatically add books to your Notion library database. Built with Flask and featuring a mobile-friendly interface with barcode scanning capabilities.

## ✨ Features

### 🔍 **Multiple Book Input Methods**
- **Barcode Scanning**: Use your device camera to scan book barcodes
- **ISBN Lookup**: Manually enter ISBN numbers for book lookup
- **Manual Entry**: Add books manually when automated lookup fails

### 📖 **Comprehensive Book Data**
- **Google Books Integration**: Automatic book data retrieval
- **Rich Information**: Title, Author, Publisher, Publication Date, Page Count, Categories, Description
- **Cover Images**: Dual cover image support (URL + Files & media)

### 🗂️ **Notion Integration** 
- **Automatic Database Population**: Seamlessly adds books to your Notion database
- **Multiple Cover Formats**: Both URL and Files & media cover image types
- **Gallery View Support**: Cover images display perfectly in Notion's Gallery view
- **Error Handling**: Graceful handling of API failures and network issues

### 📱 **Modern User Experience**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Intuitive Interface**: Clean, Figma-inspired design
- **Real-time Feedback**: Loading states and progress indicators
- **Smart Navigation**: Seamless transitions between different input methods

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Google Cloud Platform account (for deployment)
- Notion account with API access
- Google Books API key (optional but recommended)

### Environment Variables
Set up the following environment variables:

```bash
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
GOOGLE_BOOKS_API_KEY=your_google_books_api_key  # Optional
PORT=8080  # Optional, defaults to 8080
```

### Local Development

1. **Clone the repository**
   ```bash
   git clone your-repo-url
   cd book-scanner
   ```

2. **Install dependencies**
   ```bash
   pip install flask requests
   ```

3. **Set environment variables**
   ```bash
   export NOTION_TOKEN="your_token_here"
   export NOTION_DATABASE_ID="your_database_id_here"
   export GOOGLE_BOOKS_API_KEY="your_api_key_here"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   ```
   http://localhost:8080
   ```

## 🔧 Notion Database Setup

### Required Database Properties

Create a Notion database with these properties:

| Property Name | Property Type | Description |
|---------------|---------------|-------------|
| `BookName` | Title | Book title (primary key) |
| `Author` | Rich text | Book author(s) |
| `ISBN` | Rich text | ISBN number |
| `Publisher` | Rich text | Publishing company |
| `Published Date` | Date | Publication date |
| `Page Count` | Number | Number of pages |
| `Category` | Rich text | Book categories/genres |
| `Descriptions` | Rich text | Book description |
| `Cover image` | URL | Cover image URL |
| `Cover PNG` | Files & media | Cover image file attachment |

### Gallery View Setup

To display cover images in Notion's Gallery view:

1. **Switch to Gallery view** in your database
2. **Click the "Gallery" dropdown** at the top
3. **Select "Properties"**
4. **Under "Card preview"**, choose `Cover PNG`
5. **Your books will now display with cover images!**

### Getting Your Notion Credentials

#### 1. Create a Notion Integration
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Name it **"Book Scanner"**
4. Select your workspace
5. Copy the **Internal Integration Token** → This is your `NOTION_TOKEN`

#### 2. Get Database ID
1. Open your book database in Notion
2. Copy the URL - it looks like: `https://notion.so/workspace/DATABASE_ID?v=...`
3. Extract the 32-character `DATABASE_ID` → This is your `NOTION_DATABASE_ID`

#### 3. Share Database with Integration
1. In your database, click **"Share"**
2. **"Invite"** → Search for your integration name
3. **Select your integration** and click "Invite"

## 🌐 Google Cloud Deployment

### Deploy to Google Cloud Run

1. **Enable required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

2. **Deploy the application**
   ```bash
   gcloud run deploy book-scanner \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars NOTION_TOKEN=your_token,NOTION_DATABASE_ID=your_db_id,GOOGLE_BOOKS_API_KEY=your_api_key
   ```

3. **Access your deployed app**
   - Google Cloud will provide a URL like: `https://book-scanner-xxx-uc.a.run.app`

### Continuous Deployment with GitHub

1. **Connect your repository** to Google Cloud Build
2. **Set up environment variables** in Cloud Run
3. **Push changes** to trigger automatic deployments

## 📱 How to Use

### Method 1: Barcode Scanning
1. **Click "Scan Barcode"**
2. **Allow camera permissions**
3. **Point camera at book barcode**
4. **Book automatically detected and looked up**
5. **Click "Add to Notion Library"** to save

### Method 2: ISBN Entry
1. **Click "Enter ISBN"**
2. **Type the 10 or 13-digit ISBN**
3. **Click "Look Up Book"** or press Enter
4. **Review book details**
5. **Click "Add to Notion Library"** to save

### Method 3: Manual Entry
1. **If book lookup fails**, click **"Add Book Manually"**
2. **Fill in book details** (Title and Author required)
3. **Add optional information** (Publisher, Date, Pages, etc.)
4. **Click "Add Book to Notion"** to save

## 🛠️ API Endpoints

### `GET /`
Serves the main web interface

### `POST /test-isbn`
Tests Google Books API and optionally saves to Notion

**Request Body:**
```json
{
  "isbn": "9780134685991",
  "save_to_notion": true
}
```

### `POST /add-manual-book`
Adds manually entered book directly to Notion

**Request Body:**
```json
{
  "title": "Book Title",
  "author": "Author Name",
  "isbn": "1234567890",
  "publisher": "Publisher Name",
  "published_date": "2023",
  "page_count": 300,
  "categories": "Fiction",
  "description": "Book description"
}
```

### `GET /health`
Health check endpoint

## 🔍 Troubleshooting

### Common Issues

#### **Barcode Scanner Not Working**
- **Check camera permissions** in your browser
- **Use HTTPS** (required for camera access)
- **Try different lighting conditions**
- **Use manual ISBN entry** as backup

#### **Books Not Found**
- **Verify ISBN** is correct (10 or 13 digits)
- **Try different ISBN** if book has multiple
- **Use manual entry** for books not in Google Books

#### **Notion Integration Errors**
- **Check environment variables** are set correctly
- **Verify integration permissions** in Notion
- **Ensure database is shared** with your integration
- **Check database property names** match exactly

#### **Cover Images Not Showing in Gallery View**
- **Use `Cover PNG`** (Files & media) not `Cover image` (URL)
- **Set Gallery card preview** to `Cover PNG`
- **Check image URLs** are accessible

### Debug Mode

Enable debug logging by setting:
```python
app.run(host='0.0.0.0', port=port, debug=True)
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Books API** for book data
- **Notion API** for database integration
- **Quagga.js** for barcode scanning
- **Flask** for the web framework

## 📞 Support

If you encounter any issues:

1. **Check the troubleshooting section** above
2. **Review your environment variables**
3. **Check browser console** for JavaScript errors
4. **Verify Notion database setup**
5. **Open an issue** with detailed error information

---

**Happy reading!** 📖✨
