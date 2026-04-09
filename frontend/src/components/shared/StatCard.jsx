import { formatTZS } from "../../utils/currency";

export function StatCard({ label, value, tone = "default", currency = true }) {
  return (
    <article className={`stat-card ${tone}`}>
      <span>{label}</span>
      <strong>{currency ? formatTZS(value) : value}</strong>
    </article>
  );
}
