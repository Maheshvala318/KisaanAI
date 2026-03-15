import React, { useEffect, useState } from "react";

const API_BASE = "http://localhost:8000"; 
// ⬆️ change this to your actual FastAPI base URL
// e.g. "https://your-kaggle-url.ngrok.app"

export default function PlantImageGallery() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const fetchImages = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/list`);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setImages(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load dataset images.");
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, []);

  const filteredImages = images.filter(item =>
    item.label.toLowerCase().includes(filter.toLowerCase())
  );

  if (loading) {
    return <div style={{ padding: 20 }}>Loading images…</div>;
  }

  if (error) {
    return <div style={{ padding: 20, color: "red" }}>{error}</div>;
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Plant Disease Dataset Viewer</h2>

      <div style={{ marginBottom: 16 }}>
        <input
          type="text"
          placeholder="Filter by label (e.g. Tomato, Apple…) "
          value={filter}
          onChange={e => setFilter(e.target.value)}
          style={{
            padding: 8,
            width: "100%",
            maxWidth: 400,
            borderRadius: 4,
            border: "1px solid #ccc",
          }}
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
          gap: 16,
        }}
      >
        {filteredImages.map((item, idx) => (
          <div
            key={idx}
            style={{
              border: "1px solid #eee",
              borderRadius: 8,
              overflow: "hidden",
              boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
            }}
          >
            <div
              style={{
                width: "100%",
                aspectRatio: "1 / 1",
                overflow: "hidden",
                background: "#fafafa",
              }}
            >
              <img
                src={`${API_BASE}${item.image}`} // important: prepend API_BASE
                alt={item.label}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  display: "block",
                }}
              />
            </div>
            <div style={{ padding: "8px 10px" }}>
              <div
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  wordBreak: "break-word",
                }}
              >
                {item.label}
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredImages.length === 0 && (
        <p style={{ marginTop: 20 }}>No images match this filter.</p>
      )}
    </div>
  );
}
