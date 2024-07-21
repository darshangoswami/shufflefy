import { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

axios.defaults.withCredentials = true;

function ShuffledPlaylist() {
  const [tracks, setTracks] = useState([]);
  const { playlistId } = useParams();

  useEffect(() => {
    fetchPlaylist();
  }, [playlistId]);

  const fetchPlaylist = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:5000/playlist/${playlistId}`
      );
      setTracks(response.data);
    } catch (error) {
      console.error("Error fetching playlist:", error);
    }
  };

  const shuffleTracks = () => {
    const shuffled = [...tracks];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    setTracks(shuffled);
  };

  const createShuffledPlaylist = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:5000/create-shuffled-playlist/${playlistId}`
      );
      alert(
        `New shuffled playlist created with ID: ${response.data.new_playlist_id}`
      );
    } catch (error) {
      console.error("Error creating shuffled playlist:", error);
    }
  };

  return (
    <div>
      <h1>Playlist</h1>
      <button onClick={fetchPlaylist}>Reset to Original</button>
      <button onClick={shuffleTracks}>Shuffle Queue</button>
      <button onClick={createShuffledPlaylist}>Create Shuffled Playlist</button>
      <ul>
        {tracks.map((track) => (
          <li key={track.id}>
            {track.name} - {track.artists.join(", ")}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ShuffledPlaylist;
