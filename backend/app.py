from flask import Flask, request, jsonify, session
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from shuffle import fisher_yates_shuffle

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key_here'

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope='playlist-read-private')
    auth_url = sp_oauth.get_authorize_url()
    return jsonify({"auth_url": auth_url})

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope='playlist-read-private')
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return "Login successful!"

@app.route('/playlists')
def get_playlists():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return jsonify({"error": "Not authorized"})
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    playlists = sp.current_user_playlists()
    return jsonify(playlists)

@app.route('/shuffle/<playlist_id>')
def shuffle_playlist(playlist_id):
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return jsonify({"error": "Not authorized"})
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    tracks = sp.playlist_tracks(playlist_id)
    track_list = [item['track'] for item in tracks['items']]
    shuffled_tracks = fisher_yates_shuffle(track_list)
    return jsonify(shuffled_tracks)

def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    if (is_token_expired):
        sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, scope='playlist-read-private')
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid

if __name__ == '__main__':
    app.run(debug=True)