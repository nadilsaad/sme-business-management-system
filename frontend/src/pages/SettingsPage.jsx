import { PageHeader } from "../components/shared/PageHeader";

export function SettingsPage() {
  return (
    <div className="page-stack">
      <PageHeader title="Settings" description="Environment notes, demo credentials, and configuration reminders." />
      <div className="info-card">
        <h3>Demo Credentials</h3>
        <p>`admin / demo1234`</p>
        <p>`cashier / demo1234`</p>
        <p>`storekeeper / demo1234`</p>
      </div>
      <div className="info-card">
        <h3>Deployment Notes</h3>
        <p>Backend expects PostgreSQL by default and can fall back to SQLite by setting `USE_SQLITE=1` during local development.</p>
        <p>Frontend reads the API base URL from `VITE_API_BASE_URL`.</p>
      </div>
    </div>
  );
}
