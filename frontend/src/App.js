// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Chat from "./Chat";
import Home from "./Home";
import PlantImageGallery from "./PlantImageGallery";

function App() {
  return (
    <Router>
      <Routes>
        {/* Home page */}
        <Route path="/" element={<Home />} />

        {/* Chat page */}
        <Route path="/chat" element={<Chat />} />

        {/* Plant gallery page */}
        <Route path="/plants" element={<PlantImageGallery />} />
      </Routes>
    </Router>
  );
}

export default App;
