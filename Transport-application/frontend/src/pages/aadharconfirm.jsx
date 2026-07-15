import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api.js";

export default function AadharConfirm() {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  const [aadharNumber, setAadharNumber] = useState("");
  const [aadharName, setAadharName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.confirmPass(applicationId, {
        aadhar_number: aadharNumber,
        aadhar_name: aadharName,
      });
      setDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (done) {
    return (
      <div className="card">
        <h1>Pass confirmed</h1>
        <p style={{ textAlign: "center", color: "#6b6a65", fontSize: 14 }}>
          Your monthly pass application has been verified and confirmed.
        </p>
        <button className="btn-primary" onClick={() => navigate("/apply")}>
          Apply for another pass
        </button>
      </div>
    );
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h1>Identity confirmation</h1>
      <p style={{ fontSize: 13, color: "#6b6a65", marginTop: -12, marginBottom: 14 }}>
        Aadhar verification is required to issue a concession pass.
      </p>
      {error && <div className="error-text">{error}</div>}
      <div className="field">
        <label>Aadhar number</label>
        <input
          type="text"
          placeholder="XXXX XXXX XXXX"
          maxLength={12}
          value={aadharNumber}
          onChange={(e) => setAadharNumber(e.target.value.replace(/\D/g, ""))}
          required
        />
      </div>
      <div className="field">
        <label>Name as per Aadhar</label>
        <input
          type="text"
          placeholder="Full name"
          value={aadharName}
          onChange={(e) => setAadharName(e.target.value)}
          required
        />
      </div>
      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? "Confirming..." : "Confirm and pay"}
      </button>
    </form>
  );
}
