import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { FaSpotify, FaYoutube } from "react-icons/fa";
import { ImSpinner2 } from "react-icons/im";
import "bootstrap/dist/css/bootstrap.min.css";

export default function LikedSongs() {
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loggedIn, setLoggedIn] = useState({ spotify: false, youtube: false });
  const navigate = useNavigate();

  const backendUrl = "http://192.168.0.106:8000/v1"; // Update if hosted elsewhere
  // 192.168.0.106:3000 -> to access in mobile (command to check ip - ifconfig | grep inet)

  const fetchLikedSongs = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/merged-liked-songs`);
      setSongs(response.data.data);
      if (response.data.login_info.loggedIn.spotify) setLoggedIn((prev) => ({ ...prev, spotify: true }));
      if (response.data.login_info.loggedIn.youtube) setLoggedIn((prev) => ({ ...prev, youtube: true }));
      if (response.data.login_info.loggedIn.spotify && response.data.login_info.loggedIn.youtube) {
        navigate("/songs", { state: { songs: response.data.data } });
      }
      // if (response.data.login_info.loggedIn.spotify || response.data.login_info.loggedIn.youtube) {
      //   navigate("/");
      // }
    } catch (error) {
      console.error("Error fetching liked songs:", error);
    }
    setLoading(false);
  };

  const loginSpotify = async () => {
    try {
      const response = await axios.get(`${backendUrl}/spotify/login`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("Spotify login error:", error);
    }
  };

  const loginYouTube = async () => {
    try {
      const response = await axios.get(`${backendUrl}/youtube/login`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("YouTube login error:", error);
    }
  };

  useEffect(() => {
    fetchLikedSongs();
  }, []);

  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100 bg-dark text-light p-4">
      <div className="d-flex flex-column align-items-center gap-4 w-100 max-w-lg bg-secondary p-5 rounded shadow-lg">
        <h1 className="text-center fw-bold">
          {loggedIn.spotify && loggedIn.youtube ? "Your Liked Songs" : "Login to Fetch Your Liked Songs"}
        </h1>
        {!loggedIn.spotify && (
          <button onClick={loginSpotify} className="btn btn-success w-100 d-flex align-items-center justify-content-center gap-2 fs-5 fw-semibold shadow">
            <FaSpotify className="fs-3" /> Login with Spotify
          </button>
        )}
        {!loggedIn.youtube && (
          <button onClick={loginYouTube} className="btn btn-danger w-100 d-flex align-items-center justify-content-center gap-2 fs-5 fw-semibold shadow">
            <FaYoutube className="fs-3" /> Login with YouTube
          </button>
        )}
        {loading ? (
          <div className="mt-4 d-flex justify-content-center">
            <ImSpinner2 className="spinner-border text-light" />
          </div>
        ) : (
          <ul className="mt-4 w-100 list-group bg-dark p-3 rounded shadow">
            {songs.map((song, index) => (
              <li key={index} className="list-group-item bg-secondary text-light d-flex justify-content-between align-items-center">
                <div>
                  <strong>{song.title}</strong> - {song.artist}
                </div>
                <span className="badge bg-light text-dark">{song.platform}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
