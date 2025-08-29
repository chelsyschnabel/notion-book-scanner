# 📚 Book Scanner - Notion Integration

A web application that allows you to scan book barcodes or manually enter ISBNs to automatically populate a Notion database with complete book information from Google Books API.

## ✨ Features

- 📱 **Barcode scanning** using phone camera
- 📝 **Manual ISBN entry** for any device
- 📦 **Batch processing** multiple books at once
- 🔄 **Automatic data population** from Google Books API
- 📊 **Complete book tracking** in Notion database
- 🎯 **Reading progress management**
- 💻 **Multi-device support** - works everywhere

## 🚀 Quick Start

### 1. Set Up Notion Database

Create a new Notion database with these **exact column names and types**:

| Column Name | Property Type | Purpose |
|-------------|---------------|---------|
| BookName | Title | Book title (primary) |
| ISBN | Text | ISBN number |
| Status | Select | Book status (New, Reading, etc.) |
| Author | Text | Book author(s) |
| Publisher | Text | Publishing company |
| Published Date | Date | Publication date |
| Descriptions | Text | Book description |
| Page Count | Number | Number of pages |
| Category | Text | Book genres |
| ReadStatus | Select | Reading status (Want to Read, Reading, Read, DNF) |
| StartDate | Date | When you started reading |
| FinishDate | Date | When you finished reading |
| Favorite | Checkbox | Mark as favorite |
| Currentpage | Number | Current page number |
| PublishPlace | Text | Place of publication |
| Language | Text | Book language |
| MyRate | Number | Your personal rating |
| Cover image | URL | Book cover image |
| AMZ-CoverImage | Text | Alternative cover image URL |
| My Progress | Number | Reading progress (0-100) |
| ReadLog | Text | Your reading notes |

### 2. Create Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New Integration"
3. Name it "Book Scanner"
4. Copy the **Internal Integration Token**
5. In your database, click "..." → "Connections" → Add your integration

### 3. Get Google Books API Key (Optional)

1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a project and enable "Books API"
3. Create credentials → API Key
4. Copy the API key

### 4. Deploy to Cloud Run

#### Option A: Using Google Cloud Shell

```bash
# Clone this repository
git clone https://github.com/YOUR-USERNAME/book-scanner.git
cd book-scanner

# Deploy to Cloud Run
gcloud run deploy book-scanner \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Option B: Using Cloud Run Console

1. Go to Google Cloud Run
2. Click "CREATE SERVICE"
3. Select "Deploy from source repository"
4. Connect to this GitHub repository
5. Deploy

### 5. Set Environment Variables

After deployment, add these environment variables in Cloud Run:

- `NOTION_TOKEN` - Your Notion integration token
- `NOTION_DATABASE_ID` - Your Notion database ID (from the URL)
- `GOOGLE_BOOKS_API_KEY` - Your Google Books API key (optional)

**To find your Database ID:**
- Open your Notion database
- Copy the URL: `https://notion.so/workspace/DATABASE_ID?v=...`
- The DATABASE_ID is the long string between workspace name and `?v=`

## 📱 How to Use

1. **Visit your deployed URL** (provided after Cloud Run deployment)
2. **Scan a barcode** with your phone camera, or
3. **Type an ISBN** manually, or
4. **Batch add** multiple ISBNs at once
5. **Watch your Notion database** populate automatically!

## 🎯 Reading Workflow

1. **Scan books** to add to your "Want to Read" list
2. **Update ReadStatus** when you start reading
3. **Track progress** using Currentpage and My Progress
4. **Add notes** in ReadLog as you read
5. **Rate and favorite** completed books

## 🔧 Configuration

### Notion Select Field Options

For best experience, add these options to your Select fields:

**Status Options:**
- New
- Reading  
- Read
- On Hold
- DNF (Did Not Finish)

**ReadStatus Options:**
- Want to Read
- Reading
- Read
- DNF

### Customization

You can modify `main.py` to:
- Add more book data fields
- Change default values
- Modify the web interface
- Add custom validation

## 🐛 Troubleshooting

**Book not found:**
- Verify the ISBN is correct (10 or 13 digits)
- Some older books may not be in Google Books database

**Notion errors:**
- Check that all database columns exist with exact names
- Verify your integration has access to the database
- Ensure NOTION_TOKEN and NOTION_DATABASE_ID are set correctly

**Camera not working:**
- Use HTTPS (required for camera access)
- Grant camera permissions in your browser
- Try manual ISBN entry as backup

## 📄 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Pull requests welcome! Please:
- Test thoroughly
- Update documentation
- Follow existing code style

## 🔒 Security Note

Never commit your actual tokens to GitHub. Always use environment variables for sensitive information.

---

**Happy Reading! 📚✨**