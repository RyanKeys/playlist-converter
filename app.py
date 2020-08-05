import spotipy
from spotipy.oauth2 import SpotifyOAuth
import env
import os
from flask import Flask, render_template, url_for, redirect, request
import gmusic

app = Flask(__name__)
# spotipy init
scope = "playlist-modify-public"
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


@app.route('/spotify-playlist/<playlist_id>')
def spotify_playlist_detail_view(playlist_id):
    playlist = sp.playlist_tracks(playlist_id)['items']
    return render_template('home/spotify-playlist-detail.html', playlist=playlist)


@app.route('/google-playlist/<playlist_id>')
def google_playlist_detail_view(playlist_id):
    playlist = gmusic.get_playlist_contents(playlist_id)
    return render_template('home/google-playlist-detail.html', playlist=playlist)


@app.route('/create_spotify_playlist', methods=['POST', 'GET'])
def create_playlist_view():
    playlists = gmusic.get_all_playlists()
    count = 0
    available_playlists = {}
    for playlist in playlists:
        available_playlists.update({count: playlist['name']})
        count += 1

    if request.method == 'POST':
        name = request.form['playlist_name']
        gplaylist = request.form
        for playlist in playlists:
            if playlist['name'] in gplaylist:
                songs = gmusic.get_playlist_contents(playlist['id'])
                for song in songs:
                    print(
                        f"{song['track']['title']} by {song['track']['artist']}")
        user = sp.current_user()['id']
        new_playlist = sp.user_playlist_create(user=user, name=name)
        # NEEDS TRACK ID FROM SPOTIFY BY SEARCHING SONG NAME
        
        spotify_id = sp.search()
        sp.user_playlist_add_tracks(user)
        return redirect(location=new_playlist['owner']['external_urls']['spotify'], code=200)
    return render_template('home/create-playlist.html', playlists=playlists, count=count, available_playlists=available_playlists)
