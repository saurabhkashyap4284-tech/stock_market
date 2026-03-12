import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI } from "../api";

export default function RegisterPage() {
  const [formData, setFormData] = useState({ email: "", password: "", first_name: "", last_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authAPI.register(formData);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "60px auto", padding: "20px" }}>
      <h1>FO Monitor Register</h1>
      {error && <div style={{ color: "#ff4757", marginBottom: "15px" }}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="first_name"
          placeholder="First Name"
          value={formData.first_name}
          onChange={handleChange}
          style={{ width: "100%", padding: "10px", marginBottom: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
        />
        <input
          type="text"
          name="last_name"
          placeholder="Last Name"
          value={formData.last_name}
          onChange={handleChange}
          style={{ width: "100%", padding: "10px", marginBottom: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          style={{ width: "100%", padding: "10px", marginBottom: "10px", borderRadius: "4px", border: "1px solid #ccc" }}
          required
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          style={{ width: "100%", padding: "10px", marginBottom: "15px", borderRadius: "4px", border: "1px solid #ccc" }}
          required
        />
        <button
          type="submit"
          disabled={loading}
          style={{ width: "100%", padding: "10px", backgroundColor: "#00f5a0", border: "none", borderRadius: "4px", cursor: "pointer" }}
        >
          {loading ? "Registering..." : "Register"}
        </button>
      </form>
      <p style={{ marginTop: "15px", textAlign: "center" }}>
        Already have account? <a href="/login">Login here</a>
      </p>
    </div>
  );
}
