import { useState, useEffect } from "react";
import { usersAPI } from "../api";
import Header from "../components/layout/Header";

export default function WatchlistPage() {
  const [watchlists, setWatchlists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newWatchlist, setNewWatchlist] = useState("");

  useEffect(() => {
    fetchWatchlists();
  }, []);

  const fetchWatchlists = async () => {
    try {
      const res = await usersAPI.getWatchlists();
      setWatchlists(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    try {
      await usersAPI.createWatchlist({ name: newWatchlist });
      setNewWatchlist("");
      fetchWatchlists();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteWatchlist = async (id) => {
    try {
      await usersAPI.deleteWatchlist(id);
      fetchWatchlists();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0f172a" }}>
      <Header />
      <div style={{ padding: "20px", maxWidth: "1000px", margin: "0 auto" }}>
        <h2>My Watchlists</h2>

        <form onSubmit={handleCreateWatchlist} style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>
          <input
            type="text"
            placeholder="New watchlist name"
            value={newWatchlist}
            onChange={(e) => setNewWatchlist(e.target.value)}
            style={{ flex: 1, padding: "8px", borderRadius: "4px", border: "1px solid #475569", backgroundColor: "#0f172a", color: "white" }}
            required
          />
          <button
            type="submit"
            style={{ padding: "8px 16px", backgroundColor: "#00f5a0", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold" }}
          >
            Create
          </button>
        </form>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <div>
            {watchlists.map((wl) => (
              <div
                key={wl.id}
                style={{
                  padding: "15px",
                  marginBottom: "10px",
                  borderRadius: "8px",
                  backgroundColor: "#1e293b",
                  border: "1px solid #334155",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <h3 style={{ margin: "0 0 5px 0" }}>{wl.name}</h3>
                    <p style={{ margin: 0, color: "#94a3b8", fontSize: "12px" }}>
                      {wl.symbols?.length || 0} symbols
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteWatchlist(wl.id)}
                    style={{ padding: "5px 10px", backgroundColor: "#ff4757", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
