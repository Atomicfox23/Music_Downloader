from flask import Flask, render_template, request, redirect, url_for, send_file
import yt_dlp
import os
import pathlib

app = Flask(__name__)

print(pathlib.Path.home()/"Downloads")
destination = pathlib.Path.home()/"Downloads"
@app.route('/')
def index():
    return render_template('index.html')

@app.post('/link')
def download():
    url = request.form['link']

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(destination, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return redirect("/")
if __name__ == '__main__':
    app.run(debug=True, port=5000)

