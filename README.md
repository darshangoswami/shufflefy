# Shufflefy

Shufflefy is a web application that enhances the Spotify experience by providing improved playlist shuffling capabilities.

## Features

- Improved shuffling algorithm for Spotify playlists
- Create new shuffled playlists from existing ones

### Upcoming Features

- Shuffle queues on remote device
- Web-based player for shuffled playlists
- Integration with Spotify Web API and Web Playback SDK

## Tech Stack

- Backend: Python with Flask
- Frontend: React with Vite
- Authentication: Spotify OAuth 2.0
- API: Spotify Web API
- Spotify API Wrapper: Spotipy

## Prerequisites

- Python 3.7+
- Node.js 14+
- Spotify Developer Account
- Spotify Premium Account (for playback features)

## Setup

### Backend

1. Clone the repository:

```
git clone https://github.com/yourusername/spotify-shuffler.git
cd spotify-shuffler
```

2. Set up a virtual environment:

```
python3 -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the backend directory and add:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:5000/callback
```

To get the client ID and secret:

- Go to: https://developer.spotify.com/dashboard
- Create App: Fill out the necessary details and save.
- Go to your created app > settings and you can find the client id and secret over there.

5. Run the Flask server:

```
cd backend
python3 app.py
```

### Frontend

1. Navigate to the frontend directory:

```
cd frontend
```

2. Install dependencies:

```
npm install
```

3. Run the development server:

```
npm run dev
```

## Usage

1. Open your browser and go to `http://localhost:5173`
2. Log in with your Spotify account
3. Select a playlist to shuffle
4. Enjoy your newly shuffled playlist!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Spotify Web Playback SDK](https://developer.spotify.com/documentation/web-playback-sdk/)
- [Spotipy](https://spotipy.readthedocs.io/) - Lightweight Python library for the Spotify Web API
- [Flask](https://flask.palletsprojects.com/)
- [React](https://reactjs.org/)
- [Vite](https://vitejs.dev/)
