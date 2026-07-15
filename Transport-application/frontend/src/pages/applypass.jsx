import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api.js";

const CATEGORY_LABELS = {
  regular: "Regular",
  student: "Student (age 10-20)",
  oldage: "Old age (50+)",
  handicapped: "Handicapped",
};

export default function ApplyPass() {
  const navigate = useNavigate();
  const [candidateName, setCandidateName] = useState("");
  const [mobile, setMobile] = useState("");
  const [age, setAge] = useState("");
  const [category, setCategory] = useState("regular");
  const [quote, setQuote] = useState({ base_fare: 1000, discount_pct: 0, payable: 1000 });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const ageNum = parseInt(age, 10);
    if (!ageNum || ageNum <= 0) return;
    const timeout = setTimeout(() => {
      api
        .quote({ age: ageNum, category })
        .then(setQuote)
        .catch((err) => setError(err.message));
    }, 300);
    return () => clearTimeout(timeout);
  }, [age, category]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.applyPass({
        candidate_name: candidateName,
        mobile,
        age: parseInt(age, 10),
        category,
      });
      navigate(`/confirm/${data.application.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h1>Monthly pass application</h1>
      {error && <div className="error-text">{error}</div>}
      <div className="field">
        <label>Candidate name</label>
        <input
          type="text"
          placeholder="Full name"
          value={candidateName}
          onChange={(e) => setCandidateName(e.target.value)}
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
        <label>Age</label>
        <input
          type="number"
          placeholder="Enter age"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          required
        />
      </div>
      <div className="field">
        <label>Category</label>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <div className="summary-box">
        <div className="summary-row">
          <span>Base fare</span>
          <span>Rs {quote.base_fare}</span>
        </div>
        <div className="summary-row">
          <span>Discount</span>
          <span>{quote.discount_pct}%</span>
        </div>
        <div className="summary-total">
          <span>Payable</span>
          <span>Rs {quote.payable}</span>
        </div>
      </div>
      <button className="btn-primary" type="submit" disabled={loading}>
        {loading ? "Submitting..." : "Continue to confirm"}
      </button>
    </form>
  );
}
