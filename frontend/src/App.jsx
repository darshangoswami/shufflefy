import { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import axios from "axios";
import Login from "./components/Login";
import Playlists from "./components/Playlists";
import ShuffledPlaylist from "./components/ShuffledPlaylist";
import fetchPlaylists from "./components/Playlists";
import ShuffleQueueButton from "./components/ShuffleQueueButton";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button";

axios.defaults.withCredentials = true;

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if the user just logged in
    const checkLoginStatus = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/check-login", {
          withCredentials: true,
        });
        setIsLoggedIn(response.data.logged_in);
      } catch (error) {
        console.error("Error checking login status:", error);
      }
    };

    checkLoginStatus();
  }, []);

  const handleLogout = async () => {
    try {
      await axios.get("http://127.0.0.1:5000/logout", {
        withCredentials: true,
      });
      // Handle logout on the client side (e.g., clear local state, redirect)
      setIsLoggedIn(false);
      window.location.href = "/";
    } catch (error) {
      console.error("Error logging out:", error);
    }
  };

  return (
    <Router>
      <div className="flex flex-col w-full max-w-screen-md mx-auto p-5">
        <nav>
          <ul className="flex justify-between">
            <div className="flex gap-2">
              <li>
                <Link className={buttonVariants({ variant: "primary" })} to="/">
                  Shufflefy
                </Link>
              </li>
              {isLoggedIn && (
                <li>
                  <Link
                    className={buttonVariants({ variant: "outline" })}
                    onClick={fetchPlaylists}
                    to="/playlists"
                  >
                    Playlists
                  </Link>
                </li>
              )}
              <li>
                <ShuffleQueueButton />
              </li>
            </div>
            <div className="flex justify-end">
              <li>
                <Button variant="destructive" onClick={handleLogout}>
                  Logout
                </Button>
              </li>
            </div>
          </ul>
        </nav>

        <Routes>
          <Route path="/" element={isLoggedIn ? <Playlists /> : <Login />} />
          <Route path="/playlists" element={<Playlists />} />
          <Route path="/shuffle/:playlistId" element={<ShuffledPlaylist />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
