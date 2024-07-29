import { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

axios.defaults.withCredentials = true;

function ShuffledPlaylist() {
  const [tracks, setTracks] = useState([]);
  const [isShuffling, setIsShuffling] = useState(false);
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

  const playWithShuffle = async () => {
    setIsShuffling(true);
    try {
      const response = await axios.get(
        `http://127.0.0.1:5000/play-with-shuffle/${playlistId}`,
        { withCredentials: true }
      );
      alert(response.data.message);
      console.log(response.data);
    } catch (error) {
      if (error.response) {
        alert(`Error: ${error.response.data.error}`);
      } else {
        alert("An error occurred while shuffling the queue");
      }
      console.error("Error shuffling queue:", error);
    } finally {
      setIsShuffling(false);
    }
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
      <ul>
        <h3>Before Playing with Shufflefy:</h3>
        <li>
          <p>1. Make sure Spotify is active on the device you want to play.</p>
        </li>
        <li>
          <p>2. Clear your queue before shuffling.</p>
        </li>
      </ul>

      <button onClick={playWithShuffle} disabled={isShuffling}>
        {isShuffling ? "Shuffling..." : "Play With Shufflefy"}
      </button>
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
