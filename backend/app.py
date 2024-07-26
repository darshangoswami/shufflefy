from flask import Flask, make_response, request, jsonify, session, redirect
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from shuffle import fisher_yates_shuffle
from spotipy.exceptions import SpotifyException
from functools import wraps
import time

app = Flask(__name__)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # Use this in production with HTTPS
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"], "supports_credentials": True}})
app.secret_key = 'your_secret_key_here'

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

scope = 'playlist-read-private playlist-modify-public playlist-modify-private streaming user-read-playback-state user-modify-playback-state'

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect('http://127.0.0.1:5173/')

@app.route('/playlists')
def get_playlists():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return jsonify({"error": "Not authorized"})
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    playlists = sp.current_user_playlists()
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
        if playback['context']['type'] == "playlist":
            playlist_id = playback['context']['uri'].split(':')[-1]
            
            # Fetch all tracks from the playlist
            tracks = get_tracks(playlist_id)
            
            queue_tracks = [item['track'] for item in tracks if item['track'] is not None]
        else:
            queue = sp.queue()
            queue_tracks = queue['queue']
        
        # Shuffle the queue
        shuffled_queue = fisher_yates_shuffle(queue_tracks)
        
        # Clear the current queue (if possible) and add shuffled tracks
        # Note: Spotify API doesn't provide a direct method to clear the queue
        track_add_count = 0
        for track in shuffled_queue:
            sp.add_to_queue(track['uri'])
            track_add_count += 1

        unique_tracks = list(set(track['id'] for track in queue_tracks))
        total_tracks = len(queue_tracks)
        unique_count = len(unique_tracks)
        context = playback["context"]

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

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if (is_token_expired):
        sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope=scope)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

def get_tracks(playlist_id):
    session['token_info'], authorized = get_token()
    if not authorized:
        return jsonify({"error": "Not authorized"}), 401
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    tracks = []
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