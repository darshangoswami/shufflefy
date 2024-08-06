import { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { ScrollArea } from "@/components/ui/scroll-area";

function Playlists() {
  const [playlists, setPlaylists] = useState([]);

  useEffect(() => {
    fetchPlaylists();
  }, []);

  const fetchPlaylists = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/playlists");
      setPlaylists(response.data.items);
    } catch (error) {
      console.error("Error fetching playlists:", error);
    }
  };

  return (
    <div>
      <h1>Your Playlists</h1>
      <ScrollArea className="h-[200px] w-[350px] rounded-md border p-4">
        <ul>
          {playlists.map((playlist) => (
            <li key={playlist.id}>
              <Link
                to={`/shuffle/${playlist.id}`}
                state={{ playlistName: playlist.name }}
              >
                {playlist.name}
              </Link>
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}

export default Playlists;
