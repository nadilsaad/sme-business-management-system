import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

const navItems = [
  ["Dashboard", "/dashboard"],
  ["Products", "/products"],
  ["Categories", "/categories"],
  ["Inventory", "/inventory"],
  ["Sales", "/sales"],
  ["Expenses", "/expenses"],
  ["Customers", "/customers"],
  ["Debts", "/debts"],
  ["Reports", "/reports"],
  ["Settings", "/settings"],
];

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">SME BMS</p>
          <h1>Business Hub</h1>
          <p className="muted">Sales, inventory, debt, and reporting for Tanzania-based SMEs.</p>
        </div>
        <nav className="nav-list">
          {navItems.map(([label, path]) => (
            <NavLink key={path} to={path} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="profile-card">
          <strong>{user?.full_name || user?.username}</strong>
          <span>{user?.role?.name || "User"}</span>
          <button type="button" className="button secondary" onClick={logout}>
            Sign Out
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
