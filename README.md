# Social Media Video Downloader

A powerful web application for downloading videos from YouTube, TikTok, Instagram, Facebook, Twitter/X, and 1000+ other platforms. Features both server-side processing for social media platforms and client-side downloads for direct video URLs.

## Features

- 🎥 **Social Media Downloader** - Download from YouTube, TikTok, Instagram, Facebook, Twitter, and more
- 📊 **Quality Selection** - Choose from Best, 1080p, 720p, 480p, or Audio-only
- 📹 **Direct URL Download** - Download direct video links (.mp4, .webm, etc.)
- 🔍 **HTML Extractor** - Extract video URLs from webpage source code
- 🔖 **Bookmarklet Tool** - Browser bookmark to extract videos from any page
- 📈 **Real-time Progress** - Live download progress with speed and ETA
- ℹ️ **Video Information** - Preview video details before downloading

## Supported Platforms

- YouTube (videos & playlists)
- TikTok
- Instagram (Reels, Videos)
- Facebook
- Twitter/X
- Reddit
- Vimeo
- Dailymotion
- Twitch
- SoundCloud
- And 1000+ more via yt-dlp

## Installation

### Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - Required for video processing

#### Install FFmpeg:

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add FFmpeg to your system PATH

### Setup Steps

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Start the backend server:**
```bash
python server.py
```

The server will start on `http://localhost:5000`

4. **Open the web interface:**

Simply open `index.html` in your web browser, or serve it with:
```bash
python -m http.server 8000
```

Then visit `http://localhost:8000` in your browser.

## Usage

### Social Media Downloads

1. Navigate to the "Social Media" tab
2. Paste the video URL (YouTube, TikTok, Instagram, etc.)
3. Select your desired quality
4. Click "Get Info" to preview video details (optional)
5. Click "Download Video" to start the download
6. Wait for processing - progress will be shown in real-time
7. Video will automatically download to your browser

### Direct URL Downloads

For direct video links (.mp4, .webm, etc.):
1. Go to the "Direct URL" tab
2. Paste the direct video URL
3. Optionally customize the filename
4. Click "Download Video"

### HTML Extractor

Extract video URLs from webpage source:
1. Go to the page with the video
2. Right-click → "View Page Source" (Ctrl+U)
3. Copy all HTML (Ctrl+A, Ctrl+C)
4. Paste in the "HTML Extractor" tab
5. Click "Extract Videos"
6. Download any found videos

### Bookmarklet Tool

1. Go to the "Bookmarklet Tool" tab
2. Drag the "Extract Videos" button to your bookmarks bar
3. Visit any webpage with videos
4. Click the bookmarklet to find and download videos

## API Documentation

The backend server provides the following API endpoints:

### GET /api/health
Health check endpoint
```json
{"status": "ok", "message": "Server is running"}
```

### POST /api/info
Get video information without downloading
```json
Request: {"url": "https://youtube.com/watch?v=..."}
Response: {
  "title": "Video Title",
  "thumbnail": "https://...",
  "duration": 180,
  "uploader": "Channel Name",
  "formats": [...]
}
```

### POST /api/download
Start a video download
```json
Request: {
  "url": "https://youtube.com/watch?v=...",
  "quality": "best"  // best, 1080p, 720p, 480p, audio
}
Response: {"download_id": "uuid"}
```

### GET /api/progress/{download_id}
Check download progress
```json
Response: {
  "status": "downloading",
  "percent": "45%",
  "speed": "2.5MiB/s",
  "eta": "00:30"
}
```

### GET /api/file/{download_id}
Download the completed file

### GET /api/supported-sites
Get list of supported platforms

## Configuration

### Change Server Port

Edit `server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

Then update the frontend API URL in `index.html`:
```javascript
const API_URL = 'http://localhost:5000/api';  // Update port here
```

### File Cleanup

Downloaded files are automatically deleted after 1 hour. To change this, edit `server.py`:
```python
if current_time - os.path.getmtime(filepath) > 3600:  # Change 3600 (1 hour)
```

## Troubleshooting

### "Cannot connect to server" error
- Make sure the backend server is running: `python server.py`
- Check that the server is running on port 5000
- Verify no firewall is blocking the connection

### "FFmpeg not found" error
- Install FFmpeg following the instructions above
- Restart the server after installing FFmpeg
- Verify FFmpeg is in your system PATH: `ffmpeg -version`

### Downloads failing for specific sites
- Some platforms may have regional restrictions
- Private videos cannot be downloaded
- Some sites may require authentication (not currently supported)
- Try updating yt-dlp: `pip install --upgrade yt-dlp`

### CORS errors
- Make sure you're accessing the frontend through a web server (not file://)
- Backend has CORS enabled for all origins

## Legal Notice

⚠️ **Important:** This tool is for educational purposes only. Only download videos that:
- You own or created
- You have explicit permission to download
- Are in the public domain or have appropriate licenses

Respect copyright laws, terms of service, and content creators' rights. Unauthorized downloading may violate laws and platform terms of service.

## Technical Details

**Frontend:**
- Pure HTML/CSS/JavaScript
- No frameworks required
- Responsive design
- Real-time progress tracking

**Backend:**
- Flask web framework
- yt-dlp for video downloading
- FFmpeg for video processing
- Async download processing with threading

## Contributing

Feel free to submit issues or pull requests for improvements!

## License

MIT License - See LICENSE file for details

## Credits

- Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- Powered by [Flask](https://flask.palletsprojects.com/)
- Video processing by [FFmpeg](https://ffmpeg.org/)
