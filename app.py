import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env
import os
from flask import Flask, render_template, url_for

app = Flask(__name__)
scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=env.CLIENT_ID,
                                               client_secret=env.CLIENT_SECRET, cache_path=os.getcwd(), redirect_uri='http://localhost:8888/callback'))


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/spotify-auth')
def spotify_auth_view():
    playlists = sp.current_user_playlists()['items']
    return render_template('spotify-test.html', playlists=playlists)
