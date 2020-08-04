import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env
import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'



def spotify_authentication():
    scope = "user-library-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,client_id=env.CLIENT_ID,client_secret=env.CLIENT_SECRET,cache_path=os.getcwd()))
    playlists = sp.current_user_playlists()['items']

    for playlist in playlists:
        print(playlist) 
    return playlists

@app.route('/spotify-auth')
def spotify_auth_view():
    context = spotify_authentication()

    return render_template('spotify-test.html',context=context)