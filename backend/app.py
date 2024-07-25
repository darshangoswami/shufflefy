from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, APP_SECRET_KEY
from shuffle import fisher_yates_shuffle
from spotipy.exceptions import SpotifyException
from functools import wraps
import time

app = Flask(__name__)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # Use this in production with HTTPS
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5173", "http://localhost:5173"], "supports_credentials": True}})
app.secret_key = APP_SECRET_KEY

def add_cors_headers(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    return decorated_function

scope = 'playlist-read-private playlist-modify-public playlist-modify-private streaming'

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
    session['token_info'], authorized = get_token()
    if not authorized:
        return jsonify({"error": "Not authorized"})
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    tracks = sp.playlist_tracks(playlist_id)
    track_list = [{'id': item['track']['id'], 'name': item['track']['name'], 'artists': [artist['name'] for artist in item['track']['artists']]} for item in tracks['items']]
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
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        
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

@app.route('/check-login')
def check_login():
    token_info = session.get('token_info', None)
    if token_info:
        return jsonify({'logged_in': True})
    else:
        return jsonify({'logged_in': False})


if __name__ == '__main__':
    app.run(debug=True)