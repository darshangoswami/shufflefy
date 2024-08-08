import { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

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
    <div className="flex flex-col w-full p-2 justify-center mx-auto mt-5">
      <h1>Your Playlists</h1>
      <ScrollArea className="h-96 w-full rounded-md border py-4 px-6 mt-2 shadow-md">
        <ul>
          {playlists.map((playlist) => (
            <li key={playlist.id}>
              <Link
                className="hover:text-green-400"
                to={`/shuffle/${playlist.id}`}
                state={{ playlistName: playlist.name }}
              >
                {playlist.name}
              </Link>
              <Separator className="my-2" />
            </li>
          ))}
        </ul>
      </ScrollArea>
    </div>
  );
}

export default Playlists;
