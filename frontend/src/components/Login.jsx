import React from "react";
import axios from "axios";

function Login() {
  const handleLogin = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/login");
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("Error during login:", error);
    }
  };

  return (
    <div>
      <h1>Spotify Shuffler</h1>
      <button onClick={handleLogin}>Login with Spotify</button>
    </div>
  );
}

export default Login;
