import axios from "axios";
import { Button } from "@/components/ui/button";

function Login() {
  const handleLogin = async () => {
    try {
      const response = await axios.get("http://backend:5001/login");
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("Error during login:", error);
    }
  };

  return (
    <div className="flex w-full p-2 mt-2 justify-center">
      <Button onClick={handleLogin}>Login with Spotify</Button>
    </div>
  );
}

export default Login;
