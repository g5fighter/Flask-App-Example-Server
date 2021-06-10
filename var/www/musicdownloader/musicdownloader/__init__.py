from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, abort
import youtube_dl
import ffmpeg
import zipfile
import io
from os.path import basename

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '/var/www/musicdownloader/musicdownloader/downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'reactrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_addreacs': '0.0.0.0',  # bind to ipv4 since ipv6 addreacses cause issues sometimes
    'output': r'youtube-dl',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '320',
}]
} 

ydl_opts_playlist = {'outtmpl': '%(id)s%(ext)s', 'quiet':True,}

def dwl_vid(zxt): 
    with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
        download = ydl.extract_info(zxt, True)
        filename = ydl.prepare_filename(download)
        return filename

def correctExt(file):
    return file.replace(".webm",".mp3")

def get_playlist_links(playlist_url):
    with youtube_dl.YoutubeDL(ydl_opts_playlist) as ydl: 
        result = ydl.extract_info(playlist_url, download=False)
        if 'entries' in result:
            video = result['entries']
            files = []
            for i, item in enumerate(video):
                video = result['entries'][i]['webpage_url'] 
                actualfile=correctExt(dwl_vid(video))
                files.append(actualfile)
            return files

def request_zip(files):
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for f_name in files:
            z.write(f_name, basename(f_name))
    data.seek(0)
    return data

app = Flask(__name__)

@app.route('/', methods=["POST","GET"])
def musicdownloader():
    if request.method == "POST":
        zxt = request.form["urlintro"]
        if "playlist" in zxt:             
            files =  get_playlist_links(zxt)                             
            return send_file(request_zip(files), mimetype='application/zip', as_attachment=True, attachment_filename='data.zip')
        name=dwl_vid(zxt)
        return send_file(correctExt(name), as_attachment=True)
    return render_template('index.html')
        
@app.route('/download/<file>', methods=["POST","GET"])
def linkurl(file):
    return send_from_directory('/var/www/musicdownloader/musicdownloader/downloads/', file, as_attachment=True)
