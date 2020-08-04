import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env
import os
from flask import Flask, render_template, url_for

app = Flask(__name__)
scope = "playlist-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=env.CLIENT_ID,
                                               client_secret=env.CLIENT_SECRET, cache_path=os.getcwd(), redirect_uri='http://localhost:8888/callback'))


@app.route('/login')
def login():
    return render_template('home/login.html')


@app.route('/')
def index():
    playlists = sp.current_user_playlists()['items']
    return render_template('home/index.html', playlists=playlists)


@app.route('/playlist/<playlist_id>')
def playlist_detail_view(playlist_id):
    playlist = sp.playlist_tracks(playlist_id)['items']
    return render_template('home/playlist-detail.html', playlist=playlist)
