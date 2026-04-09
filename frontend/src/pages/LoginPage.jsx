import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [form, setForm] = useState({ username: "admin", password: "demo1234" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(form);
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.non_field_errors?.[0] || "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-shell">
      <section className="login-panel hero">
        <div>
          <p className="eyebrow">SME Business Management System</p>
          <h1>Run your shop, salon, boutique, or pharmacy from one control center.</h1>
          <p className="muted">
            Monitor sales, stock, debts, expenses, and customer payments with a UI designed for fast-moving SMEs in Tanzania.
          </p>
        </div>
      </section>
      <section className="login-panel form">
        <form className="form-card" onSubmit={handleSubmit}>
          <h2>Welcome back</h2>
          <label>
            Username
            <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </label>
          <label>
            Password
            <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </label>
          {error ? <div className="error-banner">{error}</div> : null}
          <button type="submit" className="button primary" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
          <p className="muted">Demo: `admin / demo1234`, `cashier / demo1234`, `storekeeper / demo1234`</p>
        </form>
      </section>
    </div>
  );
}
