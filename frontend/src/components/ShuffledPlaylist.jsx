import { useState, useEffect } from "react";
import axios from "axios";
import { useParams, useLocation } from "react-router-dom";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

axios.defaults.withCredentials = true;

function ShuffledPlaylist() {
  const [tracks, setTracks] = useState([]);
  const [isShuffling, setIsShuffling] = useState(false);
  const { playlistId } = useParams();
  const location = useLocation();
  const playlistName = location.state?.playlistName || "Unknown Playlist";

  useEffect(() => {
    fetchPlaylist();
  }, [playlistId]);

  const fetchPlaylist = async () => {
    try {
      const response = await axios.get(`/playlist/${playlistId}`);
      setTracks(response.data);
    } catch (error) {
      console.error("Error fetching playlist:", error);
    }
  };

  const playWithShuffle = async () => {
    setIsShuffling(true);
    try {
      const response = await axios.get(`/play-with-shuffle/${playlistId}`, {
        withCredentials: true,
      });
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
        `/create-shuffled-playlist/${playlistId}`
      );
      alert(
        `New shuffled playlist created with ID: ${response.data.new_playlist_id}`
      );
    } catch (error) {
      console.error("Error creating shuffled playlist:", error);
    }
  };

  return (
    <div className="flex flex-col w-full p-2 h-2/3 md:h-4/5 justify-center mx-auto mt-5">
      <h1 className="text-lg text-green-400">Playlist - {playlistName}</h1>
      <h3 className="mt-4 mb-3">
        Before Playing with Shufflefy: Make sure Spotify is active on the device
        you want to play.
      </h3>

      <div className="flex flex-row justify-center mb-2">
        <Button onClick={playWithShuffle} disabled={isShuffling}>
          {isShuffling ? "Shuffling..." : "Play With Shufflefy"}
        </Button>
        <Button onClick={createShuffledPlaylist} className="ml-2">
          Create Shuffled Playlist
        </Button>
      </div>

      <ScrollArea className="w-full rounded-md border py-4 px-6 mt-2 shadow-md">
        <ul>
          {tracks.map((track) => (
            <li key={track.id}>
              {track.name} - {track.artists.join(", ")}
              <Separator className="my-1" />
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}

export default ShuffledPlaylist;
