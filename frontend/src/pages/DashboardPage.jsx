import { useEffect, useState } from "react";
import { dashboardApi } from "../api/endpoints";
import { CategoryMixChart } from "../components/charts/CategoryMixChart";
import { SalesTrendChart } from "../components/charts/SalesTrendChart";
import { DataTable } from "../components/shared/DataTable";
import { PageHeader } from "../components/shared/PageHeader";
import { StatCard } from "../components/shared/StatCard";
import { formatDate } from "../utils/date";

export function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi.getOverview().then(({ data: payload }) => setData(payload)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="state-card">Loading dashboard...</div>;
  if (!data) return <div className="state-card">No dashboard data available.</div>;

  return (
    <div className="page-stack">
      <PageHeader title="Dashboard" description="Daily visibility into sales, expenses, debts, and stock risk." />
      <section className="stats-grid">
        <StatCard label="Sales Today" value={data.kpis.sales_today} />
        <StatCard label="Sales This Month" value={data.kpis.sales_month} tone="accent" />
        <StatCard label="Expenses This Month" value={data.kpis.expenses_month} tone="warm" />
        <StatCard label="Open Debts" value={data.kpis.open_debts} tone="alert" />
        <StatCard label="Low Stock Items" value={data.kpis.low_stock_count} currency={false} />
      </section>
      <section className="dashboard-grid">
        <SalesTrendChart data={data.sales_trend} />
        <CategoryMixChart data={data.category_mix} />
      </section>
      <section className="dashboard-grid">
        <DataTable
          columns={[
            { key: "name", label: "Low Stock Product", render: (row) => row.name },
            { key: "sku", label: "SKU" },
            { key: "stock_quantity", label: "Stock" },
          ]}
          rows={data.low_stock_products}
          emptyMessage="No low-stock products right now."
        />
        <DataTable
          columns={[
            { key: "action", label: "Activity" },
            { key: "description", label: "Description" },
            { key: "created_at", label: "Date", render: (row) => formatDate(row.created_at) },
          ]}
          rows={data.recent_activities}
          emptyMessage="No recent activity yet."
        />
      </section>
    </div>
  );
}
