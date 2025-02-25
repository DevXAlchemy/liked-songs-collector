import logo from './logo.svg';
import './App.css';
import { Routes, Route } from "react-router-dom";
import LikedSongs from "./components/LikedSongs";
import SongList from "./components/SongList";
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LikedSongs />} />
      <Route path="/songs" element={<SongList />} />
    </Routes>
  );
}

export default App;

// function App() {
//   return <LikedSongs />;
  // return (
  //   <div className="App">
  //     <header className="App-header">
  //       <img src={logo} className="App-logo" alt="logo" />
  //       <p>
  //         Edit <code>src/App.js</code> and save to reload.
  //       </p>
  //       <a
  //         className="App-link"
  //         href="https://reactjs.org"
  //         target="_blank"
  //         rel="noopener noreferrer"
  //       >
  //         Learn React
  //       </a>
  //     </header>
  //   </div>
  // );
// }
