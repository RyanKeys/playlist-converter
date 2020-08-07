"""
TODO Prerequisites

    pip3 install spotipy Flask Flask-Session

    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
   
"""
import uuid
import spotipy
from flask_session import Session
from flask import Flask, session, request, redirect, render_template, url_for
import os
from gmusicapi import Mobileclient
import gmusicapi

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
mc = Mobileclient()

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path(cache):
    return cache + session.get('uuid')


@app.route('/login', methods=['GET', 'POST'])
def login():

    return render_template('home/login.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(email, password)
        mc.login(email, password, Mobileclient.FROM_MAC_ADDRESS)
        print("logged in")
        return redirect(url_for('index'))

    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())
        return redirect(url_for('login'))

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                               cache_path=session_cache_path(
                                                   caches_folder),
                                               show_dialog=True)
    if gmusicapi.exceptions.NotLoggedIn:
        google_playlists = None
        pass
    else:
        google_playlists = mc.get_all_playlists()

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    spotify_playlists = spotify.current_user_playlists()['items']
    return render_template('home/index.html', spotify_playlists=spotify_playlists, google_playlists=google_playlists)


@app.route('/logout')
def logout():
    os.remove(session_cache_path(caches_folder))
    mc.logout()
    session.clear()
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path(caches_folder))
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    finally:
        return redirect('/')


@app.route('/playlists')
def playlists():
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        cache_path=session_cache_path(caches_folder))
    if not auth_manager.get_cached_token():
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        cache_path=session_cache_path(caches_folder))
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return spotify.audio_analysis(track['item']['id'])
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        cache_path=session_cache_path(caches_folder))
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return spotify.current_user()


def get_playlist_contents(playlist_id):
    playlists = mc.get_all_playlists(
        incremental=False, include_deleted=None, updated_after=None)

    for playlist in playlists:
        if playlist['id'] == playlist_id:
            return mc.get_shared_playlist_contents(share_token=playlist['shareToken'])


@app.route('/create_spotify_playlist', methods=['POST', 'GET'])
def create_playlist_view():

    playlists = mc.get_all_playlists()

    auth_manager = spotipy.oauth2.SpotifyOAuth(
        cache_path=session_cache_path(caches_folder))
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    if request.method == 'GET':
        count = 0
        available_playlists = {}
        for playlist in playlists:
            available_playlists.update({count: playlist['name']})
            count += 1

        return render_template('home/create-playlist.html', playlists=playlists, count=count, available_playlists=available_playlists)

    if request.method == 'POST':
        name = request.form['playlist_name']
        gplaylist = request.form
        user = spotify.current_user()['id']
        new_playlist = spotify.user_playlist_create(user=user, name=name)

        for playlist in playlists:
            if playlist['name'] in gplaylist:
                print(playlist['name'])
                songs = get_playlist_contents(playlist['id'])
        while True:
            for song in songs:
                spotify.trace = False
                try:
                    song_name = str(song['track']['title']).replace(" ", "%")
                    spotify_id = spotify.search(q=song_name, type="track", limit=1)[
                        'tracks']['items'][0]['uri']
                    spotify.user_playlist_add_tracks(
                        user=user, playlist_id=new_playlist['id'], tracks=[spotify_id])
                except IndexError:
                    pass
            break
        return redirect(location=new_playlist['owner']['external_urls']['spotify'], code=200)


@app.route('/google-playlist/<playlist_id>')
def google_playlist_detail_view(playlist_id):

    playlist = get_playlist_contents(playlist_id)
    return render_template('home/google-playlist-detail.html', playlist=playlist)


@app.route('/spotify-playlist/<playlist_id>')
def spotify_playlist_detail_view(playlist_id):
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        cache_path=session_cache_path(caches_folder))
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlist = spotify.playlist_tracks(playlist_id)['items']
    return render_template('home/spotify-playlist-detail.html', playlist=playlist)
