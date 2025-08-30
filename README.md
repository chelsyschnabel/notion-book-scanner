# 📚 Book Scanner - Notion Integration

A web application that allows you to scan book barcodes or manually enter ISBNs to automatically populate a Notion database with complete book information from Google Books API.

## ✨ Features

- 📱 **Barcode scanning** using phone camera
- 📝 **Manual ISBN entry** for any device
- 🔄 **Automatic data population** from Google Books API
- 📊 **Complete book information** in your Notion database
- 💻 **Multi-device support** - works everywhere
- 🎨 **Beautiful interface** with book cover images
- 📚 **Personal library management** in Notion

## 🎯 What Gets Populated Automatically

When you scan or enter a book, these fields are automatically filled:

- **BookName** (Title) - Book title
- **ISBN** (Text) - ISBN number
- **Author** (Text) - Author names
- **Publisher** (Text) - Publishing company
- **Page Count** (Number) - Number of pages
- **Cover image** (URL) - Book cover image
- **Published Date** (Date) - Publication date
- **Descriptions** (Text) - Book summary/description
- **Category** (Text) - Book genre/topics

## 🚀 Quick Start

### 1. Set Up Notion Database

Create a new Notion database with these **exact column names and types**:

| Column Name | Property Type | Purpose |
|-------------|---------------|---------|
| BookName | Title | Book title (primary column) |
| ISBN | Text | ISBN number |
| Author | Text | Book author(s) |
| Publisher | Text | Publishing company |
| Page Count | Number | Number of pages |
| Cover image | URL | Book cover image |
| Published Date | Date | Publication date |
| Descriptions | Text | Book description |
| Category | Text | Book genres/topics |

⚠️ **Important**: Column names are case-sensitive and must include spaces exactly as shown (e.g., "Page Count" not "PageCount").

### 2. Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New Integration"
3. Name it "Book Scanner"
4. Copy the **Internal Integration Token** (starts with `ntn_`)
5. In your database, click "..." → "Connections" → Add your integration

### 3. Get Your Database ID

1. Go to your Notion database
2. Copy the URL from your browser
3. Extract the database ID from the URL:
   - URL format: `https://www.notion.so/workspace/DATABASE_ID?v=view_id`
   - The DATABASE_ID is the 32-character string before `?v=`

### 4. Deploy to Google Cloud Run

#### Option A: Deploy from GitHub (Recommended)

1. Fork this repository
2. Go to Google Cloud Run
3. Click "CREATE SERVICE"
4. Select "Deploy from source repository"
5. Connect your GitHub account and select this repository
6. Deploy with default settings

#### Option B: Clone and Deploy

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/notion-book-scanner.git
cd notion-book-scanner

# Deploy to Cloud Run
gcloud run deploy book-scanner \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 5. Set Environment Variables

After deployment, configure these environment variables in Cloud Run:

1. Go to your Cloud Run service
2. Click "EDIT & DEPLOY NEW REVISION"
3. Go to "Variables & Secrets" tab
4. Add these variables:

- `NOTION_TOKEN` - Your Notion integration token (starts with `ntn_`)
- `NOTION_DATABASE_ID` - Your 32-character database ID
- `GOOGLE_BOOKS_API_KEY` - Optional, for higher rate limits

**To get Google Books API key (optional):**
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create project and enable "Books API"
3. Create credentials → API Key

## 📱 How to Use

### Web Interface
1. Visit your deployed Cloud Run URL
2. **Scan a barcode**: Click "📷 Scan Barcode with Camera"
3. **Manual entry**: Type ISBN in the text field
4. **Add to library**: Click "📚 Add to Notion Library"
5. **Check your Notion database** - the book appears instantly!

### Mobile Usage
- Works great on phones and tablets
- Camera permission required for barcode scanning
- Fallback to manual entry if camera unavailable

## 🎯 Reading Workflow

1. **Discovery**: Scan books at bookstores, libraries, or your home collection
2. **Automatic cataloging**: All book information populates instantly
3. **Personal management**: Add your own columns in Notion for:
   - Reading status (Want to Read, Reading, Read, DNF)
   - Start and finish dates
   - Personal rating and notes
   - Reading progress tracking
   - Favorite books

## 📊 Optional Personal Tracking Columns

You can add these columns to your Notion database for personal reading management:

| Column Name | Property Type | Purpose |
|-------------|---------------|---------|
| Status | Select | New, Reading, Read, On Hold, DNF |
| ReadStatus | Select | Want to Read, Reading, Read, DNF |
| StartDate | Date | When you started reading |
| FinishDate | Date | When you finished |
| Favorite | Checkbox | Mark favorite books |
| Currentpage | Number | Current page progress |
| MyRate | Number | Your personal rating (1-5 or 1-10) |
| ReadLog | Text | Your reading notes and thoughts |
| My Progress | Number | Reading percentage |

## 🔧 Technical Details

### Requirements
- Python 3.11+
- Flask web framework
- Google Books API (free)
- Notion API integration
- Google Cloud Run (free tier available)

### Dependencies
```
Flask==2.3.3
requests==2.31.0
gunicorn==21.2.0
```

### Architecture
- **Frontend**: HTML/CSS/JavaScript with camera barcode scanning
- **Backend**: Python Flask application
- **APIs**: Google Books API for book data, Notion API for database
- **Hosting**: Google Cloud Run (serverless)

## 🐛 Troubleshooting

### Common Issues

**"Book not found":**
- Verify ISBN is correct (10 or 13 digits)
- Some older books may not be in Google Books database
- Try manual search with title/author

**"Notion not configured":**
- Check environment variables are set correctly
- Verify integration has access to database
- Confirm database ID is correct (32 characters)

**Camera not working:**
- Use HTTPS (required for camera access)
- Grant camera permissions in browser
- Try manual ISBN entry as backup

**Database errors:**
- Ensure all column names match exactly (case-sensitive)
- Column names must include spaces: "Page Count" not "PageCount"
- Verify column types match requirements

### Database Column Troubleshooting
- **BookName**: Must be "Title" property type (first column)
- **Page Count**: Must be "Number" type with exact spacing
- **Published Date**: Must be "Date" type with exact spacing
- **Cover image**: Must be "URL" type with exact spacing

## 🔒 Security & Privacy

- **No personal data stored** in the application
- **Your books remain private** in your Notion workspace
- **Environment variables protect** your API keys
- **HTTPS required** for camera functionality

## 🤝 Contributing

Contributions welcome! Please:
- Test thoroughly before submitting
- Update documentation for new features
- Follow existing code style
- Add clear commit messages

## 📄 License

MIT License - feel free to use and modify!

## 🎉 Acknowledgments

- [Notion API](https://developers.notion.com/) for database integration
- [Google Books API](https://developers.google.com/books) for book data
- [QuaggaJS](https://serratus.github.io/quaggaJS/) for barcode scanning
- [Google Cloud Run](https://cloud.google.com/run) for hosting

---

**Happy Reading! 📚✨**

*Built with ❤️ for book lovers who want to digitize and organize their libraries.*
