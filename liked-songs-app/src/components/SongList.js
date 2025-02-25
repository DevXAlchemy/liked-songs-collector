import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { FaSpotify, FaYoutube } from "react-icons/fa";
import { ImSpinner2 } from "react-icons/im";
import "bootstrap/dist/css/bootstrap.min.css";

export default function SongList() {
  const location = useLocation();
  const songs = location.state?.songs || [];
  const [creatingPlaylist, setCreatingPlaylist] = useState(false);
  const [creatingSpotifyPlaylist, setCreatingSpotifyPlaylist] = useState(false);
  const navigate = useNavigate();
  const backendUrl = "http://192.168.0.106:8000/v1"; // Update if hosted elsewhere

  const createYoutubePlaylist = async () => {
    setCreatingPlaylist(true);
    try {
      const response = await axios.get(`${backendUrl}/youtube/create-playlist-from-spotify`);
      alert("Songs added to Youtube Playlist successfully!");
    } catch (error) {
      console.error("Error creating playlist:", error);
      alert("Failed to create playlist.");
    }
    setCreatingPlaylist(false);
  };

  const createSpotifyPlaylist = async () => {
    setCreatingSpotifyPlaylist(true);
    try {
      const response = await axios.get(`${backendUrl}/spotify/create-playlist-from-youtube`);
      alert("Songs added to Spotify Playlist successfully!");
    } catch (error) {
      console.error("Error creating Spotify playlist:", error);
      alert("Failed to create Spotify playlist.");
    }
    setCreatingSpotifyPlaylist(false);
  };

  return (
    <div className="d-flex align-items-center justify-content-center min-vh-100 bg-dark text-light p-4">
      <div className="w-100 max-w-lg bg-secondary p-5 rounded shadow-lg">
        <h1 className="text-center fw-bold">Your Liked Songs</h1>
        {songs.length === 0 ? (
          <p className="text-center mt-3">No songs found.</p>
        ) : (
          <>
            <button 
              onClick={createYoutubePlaylist} 
              className="btn btn-primary w-100 d-flex align-items-center justify-content-center gap-2 fs-5 fw-semibold shadow mt-3"
              disabled={creatingPlaylist}
            >
              {creatingPlaylist ? <ImSpinner2 className="spinner-border text-light" /> : "Add Most Played Songs to YouTube Playlist"}
            </button>
            {/* <button 
              onClick={createSpotifyPlaylist} 
              className="btn btn-success w-100 d-flex align-items-center justify-content-center gap-2 fs-5 fw-semibold shadow mt-3"
              disabled={creatingSpotifyPlaylist}
            >
              {creatingSpotifyPlaylist ? <ImSpinner2 className="spinner-border text-light" /> : "Add Most Played Songs to Spotify Playlist"}
            </button> */}
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
          </>
        )}
      </div>
    </div>
  );
}
