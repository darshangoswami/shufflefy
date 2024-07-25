import { useState } from "react";
import axios from "axios";

function ShuffleQueueButton() {
  const [isShuffling, setIsShuffling] = useState(false);

  const handleShuffleQueue = async () => {
    setIsShuffling(true);
    try {
      const response = await axios.get(
        "http://127.0.0.1:5000/shuffle-current-queue",
        { withCredentials: true }
      );
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
    <button onClick={handleShuffleQueue} disabled={isShuffling}>
      {isShuffling ? "Shuffling..." : "Shuffle Current Queue"}
    </button>
  );
}

export default ShuffleQueueButton;
