import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";

function ShuffleQueueButton() {
  const apiUrl = import.meta.env.VITE_API_URL;

  const [isShuffling, setIsShuffling] = useState(false);

  const handleShuffleQueue = async () => {
    setIsShuffling(true);
    try {
      const response = await axios.get(apiUrl + "/shuffle-current-queue", {
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

  return (
    <Button onClick={handleShuffleQueue} disabled={isShuffling}>
      {isShuffling ? "Shuffling..." : "Shuffle Current Queue"}
    </Button>
  );
}

export default ShuffleQueueButton;
