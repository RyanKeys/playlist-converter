import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env
import os
from flask import Flask, render_template, url_for
import gmusic

app = Flask(__name__)
# spotipy init
scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=env.S_CLIENT_ID,
                                               client_secret=env.S_CLIENT_SECRET, cache_path=os.getcwd(), redirect_uri='http://localhost:8888/callback'))


@app.route('/login')
def login():
    return render_template('home/login.html')


@app.route('/')
def index():
    spotify_playlists = sp.current_user_playlists()['items']
    google_playlists = gmusic.get_all_playlists()
    return render_template('home/index.html', spotify_playlists=spotify_playlists, google_playlists=google_playlists)


@app.route('/spotify_playlist/<playlist_id>')
def spotify_playlist_detail_view(playlist_id):
    playlist = sp.playlist_tracks(playlist_id)['items']
    return render_template('home/spotify-playlist-detail.html', playlist=playlist)


@app.route('/google_playlist/<playlist_id>')
def google_playlist_detail_view(playlist_id):
    playlist = gmusic.get_playlist_contents(playlist_id)
    return render_template('home/google-playlist-detail.html', playlist=playlist)
