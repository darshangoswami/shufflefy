import React, { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Link,
  useNavigate,
} from "react-router-dom";
import axios from "axios";
import Login from "./components/Login";
import Playlists from "./components/Playlists";
import ShuffledPlaylist from "./components/ShuffledPlaylist";

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
        console.log(isLoggedIn);
      } catch (error) {
        console.error("Error checking login status:", error);
      }
    };

    checkLoginStatus();
  }, []);

  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            {isLoggedIn && (
              <li>
                <Link to="/playlists">Playlists</Link>
              </li>
            )}
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
