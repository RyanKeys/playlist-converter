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
        tracks = []
        name = request.form['playlist_name']
        gplaylist = request.form
        user = sp.current_user()['id']
        new_playlist = sp.user_playlist_create(user=user, name=name)
        for playlist in playlists:
            if playlist['name'] in gplaylist:
                songs = gmusic.get_playlist_contents(playlist['id'])
        while True:
            try:
                for song in songs:
                    song_name = str(song['track']['title']).replace(" ", "%")
                    spotify_id = sp.search(q=song_name, type="track", limit=1)[
                        'tracks']['items'][0]['uri']
                    print(spotify_id)
                    tracks.append(spotify_id)
            except IndexError:
                pass

            finally:
                sp.user_playlist_add_tracks(
                    user=user, playlist_id=new_playlist['id'], tracks=tracks)
        return redirect(location=new_playlist['owner']['external_urls']['spotify'], code=200)
    return render_template('home/create-playlist.html', playlists=playlists, count=count, available_playlists=available_playlists)
