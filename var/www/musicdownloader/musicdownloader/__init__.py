from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, abort
import youtube_dl,spotipy,ffmpeg,zipfile,io
from os.path import basename
from spotipy.oauth2 import SpotifyOAuth

# Download Youtube-Dl Option
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

# Playlist extract Youtube-Dl Option
ydl_opts_playlist = {'outtmpl': '%(id)s%(ext)s', 'quiet':True,}

# Get spotify client
def getSpotifyCredentials():
    # You can set this variables as enviroment variables so you don't need to put them on the code
    # return spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials())
    return spotipy.Spotify(auth_manager=spotipy.SpotifyClientCredentials(client_id='SPOTIFY CLIENT TOKEN',client_secret='SPOTIFY CLIENT SECRET TOKEN'))

# Get spotify song info
def getSpotifyData(song):
    readedSong = ''
    sp = getSpotifyCredentials()
    if 'playlist' in song:
        songCount = 0
        songIterationCount = 100
        files = []
        while songIterationCount == 100:
            songIterationCount = 0
            results = sp.playlist_tracks(song, limit=None,offset=songCount)
            for items in results['items']:
                songCount+=1
                songIterationCount+=1
                entry = items['track']['name']
                for artist in items['track']['artists']:
                    entry += ' '+artist['name']
                actualfile=correctExt(dwl_vid(search_by_name(entry)))
                files.append(actualfile)
        return files, 1
    elif 'track' in song:
        data = sp.track(song)
        readedSong = data['name']
        for artist in data['artists']:
            readedSong += ' '+artist['name']
        return readedSong, 0    

# Search by name on Youtube
def search_by_name(song):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
        infosearched = ydl.extract_info("ytsearch:"+song, False)
        return infosearched['entries'][0]['webpage_url']

# Download given video url
def dwl_vid(zxt): 
    with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
        download = ydl.extract_info(zxt, True)
        filename = ydl.prepare_filename(download)
        return filename

# Corrects the extension of the audio file
def correctExt(file):
    if '.webm' in file:
        return file.replace(".webm",".mp3")
    if '.m4a' in file:
        return file.replace(".m4a",".mp3")
    return file

# Get links of the videos of the given playlist
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

# Creates a zip with de given files
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
        # UNCOMMENT if you are going to use Spotify API
        # if 'spotify.com' in zxt:
        #     song,type = getSpotifyData(zxt)
        #     if type == 0:
        #         name=dwl_vid(search_by_name(song))
        #     elif type == 1:                          
        #         return send_file(request_zip(song), mimetype='application/zip', as_attachment=True, attachment_filename='data.zip')
        if "playlist" in zxt and ('https://www.youtube.com/' in zxt or 'https://youtube.com/' in zxt):             
            files =  get_playlist_links(zxt)                             
            return send_file(request_zip(files), mimetype='application/zip', as_attachment=True, attachment_filename='data.zip')
        elif "https://www.youtube.com/" in zxt or 'https://youtu.be/' in zxt:
            name = dwl_vid(zxt)
        else:
            name=dwl_vid(search_by_name(zxt))
        return send_file(correctExt(name), as_attachment=True)
    return render_template('index.html')
        
@app.route('/download/<file>', methods=["POST","GET"])
def linkurl(file):
    return send_from_directory('/var/www/musicdownloader/musicdownloader/downloads/', file, as_attachment=True)
