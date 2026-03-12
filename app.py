from flask import Flask, render_template, request, redirect
import yt_dlp
import os
import pathlib
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
 
app = Flask(__name__)
 
# Use /downloads for Render's persistent disk, fallback to ~/Downloads for local
import os
if os.path.exists('/downloads'):
    destination = pathlib.Path('/downloads')
else:
    destination = pathlib.Path.home() / "Downloads"
 
download_history = []
progress_data = {
    "progress": 0,
    "current_item": 0,
    "total_items": 0,
    "current_title": "",
    "is_playlist": False,
    "completed_items": set()  # Track which items have been completed
}
ansi_escape = re.compile(r'\x1b\[([0-9]+)(;[0-9]+)*m')
 
# YouTube Mix/Radio playlist IDs always start with these prefixes
RADIO_PLAYLIST_PREFIXES = ('RD', 'RL', 'RQ', 'RDMM', 'RDEM', 'RDCLAK')
 
 
def strip_playlist_if_radio(url: str) -> tuple[str, bool]:
    """
    Returns (cleaned_url, is_real_playlist).
    - Real playlists (PLxxx, OLAKxxx) → keep list param, return True
    - Radio/Mix playlists (RDxxx, RLxxx) → strip list param, return False
    - Single videos with no list param → unchanged, return False
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
 
    playlist_id = params.get('list', [None])[0]
 
    if not playlist_id:
        return url, False  # plain single video
 
    if playlist_id.startswith(RADIO_PLAYLIST_PREFIXES):
        # It's a Mix/Radio — drop the list param entirely, just download the video
        params.pop('list', None)
        params.pop('index', None)
        new_query = urlencode({k: v[0] for k, v in params.items()})
        clean = urlunparse(parsed._replace(query=new_query))
        return clean, False
 
    # It's a real user-created playlist (PL..., OLAK...)
    return url, True
 
 
def hook(d):
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0.0%')
        clean_percent = ansi_escape.sub('', percent_str).strip().strip('%')
        try:
            progress_data["progress"] = float(clean_percent)
        except ValueError:
            pass
        
        # Update current title if available
        if 'info_dict' in d:
            title = d['info_dict'].get('title', '')
            if title and title != progress_data["current_title"]:
                # New item started - mark previous as complete
                if progress_data["current_title"]:
                    progress_data["completed_items"].add(progress_data["current_title"])
                    progress_data["current_item"] = len(progress_data["completed_items"]) + 1
                progress_data["current_title"] = title
                progress_data["progress"] = 0
            
    elif d['status'] == 'finished':
        progress_data["progress"] = 100
        # Mark current item as complete
        if progress_data["current_title"]:
            progress_data["completed_items"].add(progress_data["current_title"])
            if progress_data["is_playlist"]:
                progress_data["current_item"] = len(progress_data["completed_items"])
    
    elif d['status'] == 'processing':
        # Keep progress at 100 during post-processing
        progress_data["progress"] = 100
 
 
def make_ydl_opts(output_template):
    return {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
        'outtmpl': output_template,
        'updatetime': False,
        'progress_hooks': [hook],
        'retries': 10,
        'fragment_retries': 10,
        'extractor_retries': 3,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        # Add these to bypass bot detection
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'extract_flat': False,
        'writethumbnail': True,
        'embedthumbnail': True,
        'keepvideo': False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'EmbedThumbnail',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
        ],
    }
 
 
@app.route('/')
def index():
    return render_template('index.html', downloads=download_history)
 
 
@app.post('/link')
def download():
    raw_url = request.form['link'].strip()
    
    # Reset progress data
    progress_data["progress"] = 0
    progress_data["current_item"] = 0
    progress_data["total_items"] = 0
    progress_data["current_title"] = ""
    progress_data["is_playlist"] = False
    progress_data["completed_items"] = set()  # Reset completed items tracking
 
    # Step 1: Detect and strip radio/mix playlists before doing anything else
    url, could_be_real_playlist = strip_playlist_if_radio(raw_url)
 
    try:
        if could_be_real_playlist:
            # Step 2a: Probe only for confirmed real playlists
            with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': 'in_playlist'}) as ydl:
                info = ydl.extract_info(url, download=False)
 
            is_playlist = (
                info.get('_type') == 'playlist' and
                bool(info.get('entries')) and
                len(info['entries']) > 1
            )
        else:
            is_playlist = False
            info = None
 
        if is_playlist:
            # ── REAL PLAYLIST → named subfolder ─────────────────────────────
            progress_data["is_playlist"] = True
            progress_data["total_items"] = len(info.get('entries', []))
            progress_data["current_item"] = 1  # Start at 1
            
            playlist_name = info.get('title') or info.get('playlist_title') or 'Playlist'
            safe_name = re.sub(r'[\\/:*?"<>|]', '_', playlist_name)
            output_template = os.path.join(str(destination), safe_name, '%(title)s.%(ext)s')
            opts = make_ydl_opts(output_template)
 
            with yt_dlp.YoutubeDL(opts) as ydl:
                full_info = ydl.extract_info(url, download=True)
                for entry in full_info.get('entries', []):
                    if entry:
                        filename = ydl.prepare_filename(entry)
                        final_file = os.path.splitext(filename)[0] + '.mp3'
                        download_history.append(f"[{safe_name}] {os.path.basename(final_file)}")
 
        else:
            # ── SINGLE VIDEO (or stripped mix) → straight into Downloads ────
            progress_data["is_playlist"] = False
            progress_data["total_items"] = 1
            progress_data["current_item"] = 1
            
            output_template = os.path.join(str(destination), '%(title)s.%(ext)s')
            opts = make_ydl_opts(output_template)
 
            with yt_dlp.YoutubeDL(opts) as ydl:
                full_info = ydl.extract_info(url, download=True)
                if full_info.get('entries'):
                    full_info = full_info['entries'][0]
                
                progress_data["current_title"] = full_info.get('title', '')
                filename = ydl.prepare_filename(full_info)
                final_file = os.path.splitext(filename)[0] + '.mp3'
                download_history.append(os.path.basename(final_file))
 
    except yt_dlp.utils.DownloadError as e:
        print(f"Download error: {e}")
        return f"<h3>Download failed:</h3><pre>{e}</pre><a href='/'>Go back</a>", 500
 
    # Reset progress on completion
    progress_data["progress"] = 100
    return redirect("/")
 
 
@app.route('/progress')
def get_progress():
    return {
        "progress": progress_data["progress"],
        "current_item": progress_data["current_item"],
        "total_items": progress_data["total_items"],
        "current_title": progress_data["current_title"],
        "is_playlist": progress_data["is_playlist"]
    }
 
 
if __name__ == '__main__':
    # Get port from environment variable (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    # For local development with debug
    # app.run(debug=True, port=5000)
    
    # For production (Render, Railway, etc.)
    app.run(host='0.0.0.0', port=port, debug=False)