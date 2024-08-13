from flask import Flask, make_response, request, jsonify, session, redirect
from flask_session import Session
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, APP_SECRET_KEY, FRONTEND_URL
from shuffle import fisher_yates_shuffle
from spotipy.exceptions import SpotifyException
from functools import wraps
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

CORS(app, resources={r"/*": {"origins": 'http://localhost', "supports_credentials": True}})
def add_cors_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    return decorated_function

scope = 'playlist-read-private playlist-modify-public playlist-modify-private streaming user-read-playback-state user-modify-playback-state user-library-read'

def get_auth_manager():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    return spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=scope,
        cache_handler=cache_handler,
        show_dialog=True
    )

@app.route('/login')
def login():
    auth_manager = get_auth_manager()
    
    if not auth_manager.validate_token(auth_manager.cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return jsonify({"auth_url": auth_url})
    
    return jsonify({"message": "Already logged in"})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/callback')
def callback():
    auth_manager = get_auth_manager()
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
    return redirect("http://localhost")

@app.route('/get-playlists')
def get_playlists():
    auth_manager = get_auth_manager()
    if not auth_manager.validate_token(auth_manager.cache_handler.get_cached_token()):
        return jsonify({"error": "Not authorized"}), 401
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    playlists = spotify.current_user_playlists()
    return jsonify(playlists)

@app.route('/playlist/<playlist_id>')
@add_cors_headers
def get_playlist(playlist_id):
    tracks = get_tracks(playlist_id)
    track_list = [{'id': item['track']['id'], 'name': item['track']['name'], 'artists': [artist['name'] for artist in item['track']['artists']]} for item in tracks]
    print(f"Number of tracks in the playlist: {len(tracks)}")

    return jsonify(track_list)

@app.route('/create-shuffled-playlist/<playlist_id>')
@add_cors_headers
def create_shuffled_playlist(playlist_id):
    session['token_info'], authorized = get_token()
    if not authorized:
        return jsonify({"error": "Not authorized"}), 401
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    try:
        # Get original playlist details
        original_playlist = sp.playlist(playlist_id)
        
        # Create a new playlist
        user_id = sp.me()['id']
        new_playlist = sp.user_playlist_create(user_id, f"Shuffled: {original_playlist['name']}")
        
        # Get all tracks from the original playlist
        tracks = get_tracks(playlist_id)
        
        # Shuffle the tracks
        shuffled_tracks = fisher_yates_shuffle(tracks)
        
        # Add tracks to the new playlist in batches
        track_uris = [item['track']['uri'] for item in shuffled_tracks if item['track']['uri']]
        batch_size = 100  # Spotify allows up to 100 tracks per request
        for i in range(0, len(track_uris), batch_size):
            batch = track_uris[i:i+batch_size]
            sp.user_playlist_add_tracks(user_id, new_playlist['id'], batch)
            time.sleep(1)  # Add a small delay to avoid rate limiting
        
        return jsonify({"new_playlist_id": new_playlist['id']})
    except SpotifyException as e:
        if e.http_status == 403 and 'Insufficient client scope' in str(e):
            # Token might be expired or missing scopes, clear the session to force re-authentication
            session.clear()
            return jsonify({"error": "Insufficient permissions. Please log in again."}), 403
        else:
            # Handle other Spotify API errors
            return jsonify({"error": str(e)}), e.http_status
        
@app.route('/shuffle-current-queue')
@add_cors_headers
def shuffle_current_queue():
    session['token_info'], authorized = get_token()
    if not authorized:
        return jsonify({"error": "Not authorized"}), 401
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    
    try:
        # Get the user's current playback state
        playback = sp.current_playback()
        if not playback:
            return jsonify({"error": "No active playback found"}), 404
        
        # Get the current queue
        if not playback['context']:
            queue = sp.queue()
            queue_tracks = queue['queue']

        elif playback['context']['type'] == "playlist":
            playlist_id = playback['context']['uri'].split(':')[-1]
            # Fetch all tracks from the playlist
            tracks = get_tracks(playlist_id)
            queue_tracks = [item['track'] for item in tracks if item['track'] is not None]

        elif playback['context']['type'] == "collection":
            tracks = get_tracks(0)
            queue_tracks = [item['track'] for item in tracks if item['track'] is not None]
        
        # Shuffle the queue
        shuffled_queue = fisher_yates_shuffle(queue_tracks)
        
        track_uris = [track['uri'] for track in shuffled_queue[:81]]

        # Start playback with the shuffled tracks
        sp.start_playback(uris=track_uris)

        unique_tracks = list(set(track['id'] for track in queue_tracks))
        total_tracks = len(queue_tracks)
        unique_count = len(unique_tracks)
        context = playback["context"]
        track_add_count = len(track_uris)

        return jsonify({
            "context": context,
            "message": "Queue shuffled successfully",
            "total_tracks": total_tracks,
            "unique_tracks": unique_count,
            "duplicate_count": total_tracks - unique_count,
            "tracks_added": track_add_count
        }), 200
    except SpotifyException as e:
        return jsonify({"error": str(e)}), e.http_status
    
@app.route('/play-with-shuffle/<playlist_id>')
@add_cors_headers
def play_with_shuffle(playlist_id):
    session['token_info'], authorized = get_token()
    if not authorized:
        return jsonify({"error": "Not authorized"}), 401
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    try:
        tracks = get_tracks(playlist_id)
        queue_tracks = [item['track'] for item in tracks if item['track'] is not None]

        shuffled_queue = fisher_yates_shuffle(queue_tracks)

        track_uris = [track['uri'] for track in shuffled_queue[:81]]

        # Start playback with the shuffled tracks
        sp.start_playback(uris=track_uris)
        
        unique_tracks = list(set(track['id'] for track in queue_tracks))
        total_tracks = len(queue_tracks)
        unique_count = len(unique_tracks)
        track_add_count = len(track_uris)

        return jsonify({
            "message": "Playing with Shufflefy!",
            "total_tracks": total_tracks,
            "unique_tracks": unique_count,
            "duplicate_count": total_tracks - unique_count,
            "tracks_added": track_add_count
        }), 200
    
    except SpotifyException as e:
        return jsonify({"error": str(e)}), e.http_status
        

def get_tracks(playlist_id):
    session['token_info'], authorized = get_token()
    if not authorized:
        return jsonify({"error": "Not authorized"}), 401
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    tracks = []
    if playlist_id == 0:
        results = sp.current_user_saved_tracks(limit=50)
    else:
        results = sp.playlist_tracks(playlist_id)
    tracks.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    return tracks

@app.route('/check-login')
def check_login():
    token_info = session.get('token_info', None)
    if token_info:
        return jsonify({'logged_in': True})
    else:
        return jsonify({'logged_in': False})


if __name__ == '__main__':
    app.run(debug=True)