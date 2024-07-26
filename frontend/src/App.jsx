import { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import axios from "axios";
import Login from "./components/Login";
import Playlists from "./components/Playlists";
import ShuffledPlaylist from "./components/ShuffledPlaylist";
import fetchPlaylists from "./components/Playlists";
import ShuffleQueueButton from "./components/ShuffleQueueButton";

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
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <button onClick={handleLogout}>Logout</button>
            </li>
            {isLoggedIn && (
              <li>
                <Link onClick={fetchPlaylists} to="/playlists">
                  Playlists
                </Link>
              </li>
            )}
            <li>
              <ShuffleQueueButton />
            </li>
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
