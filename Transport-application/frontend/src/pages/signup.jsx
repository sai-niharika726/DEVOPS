import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";

export default function Signup() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [mobile, setMobile] = useState("");
  const [dob, setDob] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.signup({
        full_name: fullName,
        mobile,
        dob,
        password,
      });
      localStorage.setItem("token", data.token);
      navigate("/apply");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h1>Create account</h1>
      {error && <div className="error-text">{error}</div>}
      <div className="field">
        <label>Full name</label>
        <input
          type="text"
          placeholder="Candidate name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
      </div>
      <div className="field">
        <label>Mobile number</label>
        <input
          type="text"
          placeholder="98765 43210"
          value={mobile}
          onChange={(e) => setMobile(e.target.value)}
          required
        />
      </div>
      <div className="field">
        <label>Date of birth</label>
        <input type="date" value={dob} onChange={(e) => setDob(e.target.value)} />
      </div>
      <div className="field">
        <label>Password</label>
        <input
          type="password"
          placeholder="Create password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? "Creating account..." : "Sign up"}
      </button>
      <p className="link-row">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </form>
  );
}

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";

export default function Login() {
  const navigate = useNavigate();
  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.login({ mobile, password });
      localStorage.setItem("token", data.token);
      navigate("/apply");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h1>Transit pass</h1>
      {error && <div className="error-text">{error}</div>}
      <div className="field">
        <label>Mobile number</label>
        <input
          type="text"
          placeholder="98765 43210"
          value={mobile}
          onChange={(e) => setMobile(e.target.value)}
          required
        />
      </div>
      <div className="field">
        <label>Password</label>
        <input
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? "Logging in..." : "Log in"}
      </button>
      <p className="link-row">
        New here? <Link to="/signup">Create account</Link>
      </p>
    </form>
  );
}
