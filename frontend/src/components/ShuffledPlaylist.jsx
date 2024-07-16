import React, { useState, useEffect } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

function ShuffledPlaylist() {
  const [tracks, setTracks] = useState([]);
  const { playlistId } = useParams();

  useEffect(() => {
    const fetchShuffledPlaylist = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/shuffle/${playlistId}`
        );
        setTracks(response.data);
      } catch (error) {
        console.error("Error fetching shuffled playlist:", error);
      }
    };

    fetchShuffledPlaylist();
  }, [playlistId]);

  return (
    <div>
      <h1>Shuffled Playlist</h1>
      <ul>
        {tracks.map((track) => (
          <li key={track.id}>
            {track.name} - {track.artists[0].name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ShuffledPlaylist;
