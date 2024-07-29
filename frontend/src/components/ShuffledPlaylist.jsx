import { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

axios.defaults.withCredentials = true;

function ShuffledPlaylist() {
  const { playlistId } = useParams();

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
      <button>Play with Shufflefy</button>
      <button onClick={createShuffledPlaylist}>Create Shuffled Playlist</button>
    </div>
  );
}

export default ShuffledPlaylist;
