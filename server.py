from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import uuid
import time
from threading import Thread
import json
from curl_cffi import requests as curl_requests

app = Flask(__name__)
CORS(app)

# Configuration
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Store download progress
download_progress = {}

class ProgressHook:
    def __init__(self, download_id):
        self.download_id = download_id

    def __call__(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A').strip()
            eta = d.get('_eta_str', 'N/A').strip()

            download_progress[self.download_id] = {
                'status': 'downloading',
                'percent': percent,
                'speed': speed,
                'eta': eta
            }
        elif d['status'] == 'finished':
            download_progress[self.download_id] = {
                'status': 'processing',
                'percent': '100%',
                'message': 'Processing video...'
            }
        elif d['status'] == 'error':
            download_progress[self.download_id] = {
                'status': 'error',
                'message': d.get('error', 'Unknown error')
            }

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    current_time = time.time()
    for filename in os.listdir(DOWNLOAD_DIR):
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.isfile(filepath):
            if current_time - os.path.getmtime(filepath) > 3600:  # 1 hour
                try:
                    os.remove(filepath)
                except:
                    pass

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """Get video information without downloading"""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            return jsonify({
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration'),
                'uploader': info.get('uploader', 'Unknown'),
                'formats': [
                    {
                        'format_id': f.get('format_id'),
                        'ext': f.get('ext'),
                        'quality': f.get('format_note', 'Unknown'),
                        'filesize': f.get('filesize'),
                    }
                    for f in info.get('formats', [])
                    if f.get('vcodec') != 'none'  # Only video formats
                ][:10]  # Limit to 10 formats
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/download', methods=['POST'])
def download_video():
    """Download video from URL"""
    data = request.json
    url = data.get('url')
    format_quality = data.get('quality', 'best')  # best, 1080p, 720p, 480p, audio

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    download_id = str(uuid.uuid4())

    # Initialize progress
    download_progress[download_id] = {
        'status': 'starting',
        'percent': '0%'
    }

    # Start download in background thread
    thread = Thread(target=process_download, args=(url, format_quality, download_id))
    thread.start()

    return jsonify({'download_id': download_id})

def process_download(url, format_quality, download_id):
    """Process the download in background"""
    try:
        # Format selection with fallback options
        if format_quality == 'audio':
            format_string = 'bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            ext = 'mp3'
        elif format_quality == '1080p':
            format_string = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
            postprocessors = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
            ext = 'mp4'
        elif format_quality == '720p':
            format_string = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]/best'
            postprocessors = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
            ext = 'mp4'
        elif format_quality == '480p':
            format_string = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]/best'
            postprocessors = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
            ext = 'mp4'
        else:  # best
            format_string = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
            ext = 'mp4'

        filename = f'{download_id}.{ext}'
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        ydl_opts = {
            'format': format_string,
            'outtmpl': os.path.join(DOWNLOAD_DIR, f'{download_id}.%(ext)s'),
            'progress_hooks': [ProgressHook(download_id)],
            'postprocessors': postprocessors,
            'merge_output_format': 'mp4' if ext == 'mp4' else None,
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': False,
            'no_color': True,
            'extract_flat': False,
            'fragment_retries': 10,
            'retries': 10,
            'file_access_retries': 3,
            'extractor_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
            'extractor_args': {
                'generic': {
                    'impersonate': 'chrome'
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            original_title = info.get('title', 'video')

            # Find the actual downloaded file
            actual_filepath = None
            for file in os.listdir(DOWNLOAD_DIR):
                if file.startswith(download_id):
                    actual_filepath = os.path.join(DOWNLOAD_DIR, file)
                    break

            if actual_filepath:
                download_progress[download_id] = {
                    'status': 'completed',
                    'percent': '100%',
                    'filepath': actual_filepath,
                    'filename': f"{original_title}.{ext}",
                    'title': original_title
                }
            else:
                download_progress[download_id] = {
                    'status': 'error',
                    'message': 'File not found after download'
                }

    except Exception as e:
        download_progress[download_id] = {
            'status': 'error',
            'message': str(e)
        }

@app.route('/api/progress/<download_id>', methods=['GET'])
def get_progress(download_id):
    """Get download progress"""
    progress = download_progress.get(download_id, {'status': 'not_found'})
    return jsonify(progress)

@app.route('/api/file/<download_id>', methods=['GET'])
def download_file(download_id):
    """Download the completed file"""
    progress = download_progress.get(download_id)

    if not progress or progress.get('status') != 'completed':
        return jsonify({'error': 'File not ready'}), 404

    filepath = progress.get('filepath')
    filename = progress.get('filename', 'video.mp4')

    if not filepath or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/supported-sites', methods=['GET'])
def supported_sites():
    """Return list of supported sites"""
    return jsonify({
        'sites': [
            'YouTube', 'TikTok', 'Instagram', 'Facebook', 'Twitter/X',
            'Reddit', 'Vimeo', 'Dailymotion', 'Twitch', 'SoundCloud',
            'and 1000+ more sites supported by yt-dlp'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'})

# Cleanup old files on startup and periodically
cleanup_old_files()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("Starting Social Media Downloader Server...")
    print(f"Download directory: {DOWNLOAD_DIR}")
    print(f"Server running on http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
